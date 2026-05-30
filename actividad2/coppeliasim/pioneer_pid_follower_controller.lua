-- VIU SRM - Actividad 2.1
-- Pioneer follower controller for Bill.
-- The mode is selected with followerControlMode = P|PI|PID|LQR|NMPC.

sim = require('sim')

local Config = {
    wheelRadius = 0.0975,
    trackWidth = 0.331,
    desiredDistance = 0.82,
    vMax = 0.72,
    vReverseMax = -0.10,
    wMax = 1.65,
    headingKp = 1.70,
    headingKd = 0.04,
    integralLimit = 0.45,
    derivativeAlpha = 0.22,
    logPeriod = 0.80,
    kinematicBase = true,
    robotZ = 0.1388,
    robotMass = 16.5,
    yawInertia = 0.72,
    rollingForce = 2.8,
    wheelViscous = 0.006,
}

local Gains = {
    P = {kp = 0.42, ki = 0.00, kd = 0.00},
    PI = {kp = 0.62, ki = 0.140, kd = 0.00},
    PID = {kp = 0.75, ki = 0.100, kd = 0.34},
}

local DriveProfiles = {
    P = {vMax = 0.50, vReverseMax = -0.20, wMax = 1.35, headingKp = 1.35, headingKd = 0.00, accel = 3.0, brake = 0.22, turnAccel = 2.0, settleError = 0.08},
    PI = {vMax = 0.58, vReverseMax = -0.12, wMax = 1.70, headingKp = 1.70, headingKd = 0.04, accel = 6.0, brake = 5.0, turnAccel = 6.0, settleError = 0.08},
    PID = {vMax = 0.56, vReverseMax = -0.12, wMax = 1.85, headingKp = 1.85, headingKd = 0.08, accel = 7.5, brake = 7.5, turnAccel = 8.0, settleError = 0.045, settleExit = 0.075, derivativeAlpha = 0.22},
    LQR = {vMax = 0.42, vReverseMax = -0.08, wMax = 1.30, headingKp = 1.38, headingKd = 0.20, accel = 1.45, brake = 1.35, turnAccel = 1.55, settleError = 0.055, settleExit = 0.105, derivativeAlpha = 0.055, deadband = 0.014, commandDeadband = 0.004},
    NMPC = {vMax = 0.36, vReverseMax = -0.08, wMax = 0.90, accel = 1.80, brake = 1.70, turnAccel = 1.70, settleError = 0.060, settleExit = 0.11},
}

local NmpcConfig = {
    horizon = 10,
    dt = 0.22,
    -- Derivative-free receding-horizon solver: a Hooke-Jeeves pattern search
    -- over the (v,w) command sequence with geometrically shrinking steps. No
    -- SQP/interior-point library (IPOPT/CasADi) is available inside the
    -- CoppeliaSim Lua sandbox, so the optimiser is implemented from scratch.
    iterations = 6,
    stepV0 = 0.090,
    stepW0 = 0.220,
    stepShrink = 0.55,
    stepFloorV = 0.004,
    stepFloorW = 0.010,
    qDistance = 48.0,
    qTarget = 7.0,
    qHeading = 1.2,
    rV = 1.4,
    rW = 1.8,
    rWheel = 0.020,
    sV = 65.0,
    sW = 18.0,
    terminal = 6.0,
}

local LqrConfig = {
    -- Discrete LQR for x=[e_long, e_lat, e_yaw] and u=[delta_v, delta_w].
    -- The gain K is now solved on-line at scene init by iterating the discrete
    -- algebraic Riccati equation (see solveDiscreteLqr); it is no longer a value
    -- copied from compute_follower_lqr_gain.py. That Python script is kept only
    -- as an off-line cross-check (it reaches the same K via scipy).
    K = nil,
    vRef = 0.22,   -- reference forward speed of the linearisation point [m/s]
    rho = 1.55,    -- reference turn radius [m] -> wRef = vRef / rho
    dt = 0.05,     -- discretisation step [s]
    q = {35.0, 80.0, 18.0},
    r = {6.0, 3.0},
}

local Paths = {
    robot = '/PioneerP3DX',
    bill = '/Bill',
    leftMotor = '/PioneerP3DX/leftMotor',
    rightMotor = '/PioneerP3DX/rightMotor',
}

local SearchSigns = {1, -1}

local MathEx = {}

function MathEx.clamp(value, lo, hi)
    if value < lo then return lo end
    if value > hi then return hi end
    return value
end

function MathEx.atan2(y, x)
    if math.atan2 then return math.atan2(y, x) end
    return math.atan(y, x)
end

function MathEx.wrapAngle(a)
    while a > math.pi do a = a - 2 * math.pi end
    while a < -math.pi do a = a + 2 * math.pi end
    return a
end

function MathEx.firstOrder(current, target, rate, dt)
    local alpha = MathEx.clamp(rate * dt, 0, 1)
    return current + (target - current) * alpha
end

local function safeGetObject(path)
    local ok, handle = pcall(sim.getObject, path)
    if ok and handle and handle >= 0 then return handle end
    return -1
end

local Handles = {}
Handles.__index = Handles

function Handles:new(paths)
    local instance = setmetatable({paths = paths}, self)
    instance:resolve()
    return instance
end

function Handles:resolve()
    self.robot = safeGetObject(self.paths.robot)
    self.bill = safeGetObject(self.paths.bill)
    self.leftMotor = safeGetObject(self.paths.leftMotor)
    self.rightMotor = safeGetObject(self.paths.rightMotor)
end

function Handles:isReady()
    return self.robot >= 0 and self.bill >= 0 and self.leftMotor >= 0 and self.rightMotor >= 0
end

local RuntimeState = {}
RuntimeState.__index = RuntimeState

function RuntimeState:new()
    local instance = setmetatable({}, self)
    instance:resetAll()
    return instance
end

function RuntimeState:resetAll()
    self.lastT = sim.getSimulationTime()
    self.lastLogT = -1000
    self.lastState = ''
    self:resetControlMemory()
end

function RuntimeState:resetControlMemory()
    self.integral = 0
    self.lastError = 0
    self.lastErrorValid = false
    self.lastHeading = 0
    self.lastHeadingValid = false
    self.filteredDerivative = 0
    self.actualV = 0
    self.actualW = 0
    self.settledLatched = false
end

local SignalBus = {}
SignalBus.__index = SignalBus

function SignalBus:new()
    return setmetatable({}, self)
end

function SignalBus:readMode()
    local signal = sim.getStringSignal('followerControlMode')
    if signal == 'P' or signal == 'PI' or signal == 'PID' or signal == 'LQR' or signal == 'NMPC' then
        return signal
    end
    return 'P'
end

function SignalBus:publishFollower(mode, runtime, state, distance, error, heading, v, w, derivative)
    sim.setStringSignal('followerMode', mode)
    sim.setStringSignal('followerState', state)
    sim.setFloatSignal('followerDistance', distance or -1)
    sim.setFloatSignal('followerDistanceError', error or 0)
    sim.setFloatSignal('followerHeadingError', heading or 0)
    sim.setFloatSignal('followerIntegralError', runtime.integral)
    sim.setFloatSignal('followerDerivativeError', derivative or 0)
    sim.setFloatSignal('followerControlV', v or 0)
    sim.setFloatSignal('followerControlW', w or 0)
    sim.setInt32Signal('followerReady', 1)
end

local DifferentialDrive = {}
DifferentialDrive.__index = DifferentialDrive

function DifferentialDrive:new(cfg, handles)
    return setmetatable({cfg = cfg, handles = handles}, self)
end

function DifferentialDrive:setWheelSpeeds(v, w)
    if self.cfg.kinematicBase then
        sim.setJointTargetVelocity(self.handles.leftMotor, 0)
        sim.setJointTargetVelocity(self.handles.rightMotor, 0)
        return
    end

    local left = (v - 0.5 * self.cfg.trackWidth * w) / self.cfg.wheelRadius
    local right = (v + 0.5 * self.cfg.trackWidth * w) / self.cfg.wheelRadius
    sim.setJointTargetVelocity(self.handles.leftMotor, left)
    sim.setJointTargetVelocity(self.handles.rightMotor, right)
end

function DifferentialDrive:wheelKinematics(v, w)
    local leftLinear = v - 0.5 * self.cfg.trackWidth * w
    local rightLinear = v + 0.5 * self.cfg.trackWidth * w
    return leftLinear, rightLinear, leftLinear / self.cfg.wheelRadius, rightLinear / self.cfg.wheelRadius
end

function DifferentialDrive:integrateKinematicBase(v, w, dt)
    if not self.cfg.kinematicBase then return end

    local pos = sim.getObjectPosition(self.handles.robot)
    local ori = sim.getObjectOrientation(self.handles.robot)
    local yaw = MathEx.wrapAngle(ori[3] + w * dt)
    local step = v * dt

    pos[1] = pos[1] + step * math.cos(yaw)
    pos[2] = pos[2] + step * math.sin(yaw)
    pos[3] = self.cfg.robotZ
    sim.setObjectPosition(self.handles.robot, pos)
    sim.setObjectOrientation(self.handles.robot, {0, 0, yaw})
    pcall(sim.resetDynamicObject, self.handles.robot)
end

local PowerTelemetry = {}
PowerTelemetry.__index = PowerTelemetry

function PowerTelemetry:new(cfg, drive)
    local instance = setmetatable({cfg = cfg, drive = drive}, self)
    instance:reset()
    return instance
end

function PowerTelemetry:reset()
    self.lastPowerV = 0
    self.lastPowerW = 0
    self.lastULeft = 0
    self.lastURight = 0
    self.energyJ = 0
end

function PowerTelemetry:publish(v, w, dt)
    local leftLinear, rightLinear, leftOmega, rightOmega = self.drive:wheelKinematics(v, w)
    local duLeft = 0
    local duRight = 0
    local accel = 0
    local angularAccel = 0

    if dt > 0.000001 then
        duLeft = leftOmega - self.lastULeft
        duRight = rightOmega - self.lastURight
        accel = (v - self.lastPowerV) / dt
        angularAccel = (w - self.lastPowerW) / dt
    end

    local leftPower = math.abs(0.5 * self.cfg.robotMass * accel * leftLinear)
        + 0.5 * self.cfg.rollingForce * math.abs(leftLinear)
        + self.cfg.wheelViscous * leftOmega * leftOmega
    local rightPower = math.abs(0.5 * self.cfg.robotMass * accel * rightLinear)
        + 0.5 * self.cfg.rollingForce * math.abs(rightLinear)
        + self.cfg.wheelViscous * rightOmega * rightOmega
    local yawPower = math.abs(self.cfg.yawInertia * angularAccel * w)
    local totalPower = leftPower + rightPower + yawPower

    self.energyJ = self.energyJ + totalPower * dt
    self.lastPowerV = v
    self.lastPowerW = w
    self.lastULeft = leftOmega
    self.lastURight = rightOmega

    sim.setFloatSignal('followerWheelLeftLinear', leftLinear)
    sim.setFloatSignal('followerWheelRightLinear', rightLinear)
    sim.setFloatSignal('followerWheelLeftOmega', leftOmega)
    sim.setFloatSignal('followerWheelRightOmega', rightOmega)
    sim.setFloatSignal('followerWheelLeftU', leftOmega)
    sim.setFloatSignal('followerWheelRightU', rightOmega)
    sim.setFloatSignal('followerWheelLeftDeltaU', duLeft)
    sim.setFloatSignal('followerWheelRightDeltaU', duRight)
    sim.setFloatSignal('followerWheelLeftPower', leftPower)
    sim.setFloatSignal('followerWheelRightPower', rightPower)
    sim.setFloatSignal('followerYawPower', yawPower)
    sim.setFloatSignal('followerPowerTotal', totalPower)
    sim.setFloatSignal('followerEnergyJ', self.energyJ)
end

local BillReferenceEstimator = {}
BillReferenceEstimator.__index = BillReferenceEstimator

function BillReferenceEstimator:new(cfg)
    local instance = setmetatable({cfg = cfg}, self)
    instance:reset()
    return instance
end

function BillReferenceEstimator:reset()
    self.lastYaw = 0
    self.lastYawValid = false
    self.filteredYawRate = 0
end

function BillReferenceEstimator:read(billPos, billYaw, dt)
    local billSpeed = sim.getFloatSignal('billSpeed') or 0
    local yawRate = 0

    if self.lastYawValid and dt > 0.000001 then
        yawRate = MathEx.clamp(MathEx.wrapAngle(billYaw - self.lastYaw) / dt, -1.4, 1.4)
    end

    self.filteredYawRate = 0.22 * yawRate + 0.78 * self.filteredYawRate
    self.lastYaw = billYaw
    self.lastYawValid = true

    local c = math.cos(billYaw)
    local s = math.sin(billYaw)
    local targetX = billPos[1] - self.cfg.desiredDistance * c
    local targetY = billPos[2] - self.cfg.desiredDistance * s
    local targetVx = billSpeed * c + self.cfg.desiredDistance * self.filteredYawRate * s
    local targetVy = billSpeed * s - self.cfg.desiredDistance * self.filteredYawRate * c
    local targetSpeed = math.sqrt(targetVx * targetVx + targetVy * targetVy)
    local targetYaw = billYaw

    if targetSpeed > 0.004 then
        targetYaw = MathEx.atan2(targetVy, targetVx)
    end

    return {
        billSpeed = billSpeed,
        billYawRate = self.filteredYawRate,
        targetX = targetX,
        targetY = targetY,
        targetYaw = targetYaw,
        targetSpeed = targetSpeed,
    }
end

local PidStrategy = {}
PidStrategy.__index = PidStrategy

function PidStrategy:new(cfg, gains)
    return setmetatable({cfg = cfg, gains = gains}, self)
end

function PidStrategy:compute(ctx)
    local g = self.gains[ctx.mode] or self.gains.P
    local d = ctx.profile
    local rawV = g.kp * ctx.error + g.ki * ctx.runtime.integral + g.kd * ctx.runtime.filteredDerivative
    local forwardScale = MathEx.clamp(math.cos(ctx.heading), 0, 1)
    local v = MathEx.clamp(rawV * forwardScale, d.vReverseMax or self.cfg.vReverseMax, d.vMax or self.cfg.vMax)

    if math.abs(ctx.heading) > 0.85 then
        v = MathEx.clamp(rawV * 0.22, -0.02, 0.10)
    end
    if math.abs(ctx.heading) > 1.35 then
        v = 0
    end

    local w = MathEx.clamp(
        (d.headingKp or self.cfg.headingKp) * ctx.heading + (d.headingKd or self.cfg.headingKd) * ctx.headingDerivative,
        -(d.wMax or self.cfg.wMax),
        d.wMax or self.cfg.wMax
    )
    return v, w
end

local LqrStrategy = {}
LqrStrategy.__index = LqrStrategy

-- ----------------------------------------------------------------------------
-- In-scene discrete LQR (Riccati) solver. Pure-Lua small matrix algebra so the
-- gain is computed inside CoppeliaSim at init, not imported as a constant.
-- ----------------------------------------------------------------------------
local function matMul(A, B)
    local r, n, c = #A, #B, #B[1]
    local out = {}
    for i = 1, r do
        out[i] = {}
        for j = 1, c do
            local s = 0
            for k = 1, n do s = s + A[i][k] * B[k][j] end
            out[i][j] = s
        end
    end
    return out
end

local function matT(A)
    local out = {}
    for i = 1, #A[1] do
        out[i] = {}
        for j = 1, #A do out[i][j] = A[j][i] end
    end
    return out
end

local function matAddScaled(A, B, sgn)
    local out = {}
    for i = 1, #A do
        out[i] = {}
        for j = 1, #A[1] do out[i][j] = A[i][j] + sgn * B[i][j] end
    end
    return out
end

local function inv2(M)
    local det = M[1][1] * M[2][2] - M[1][2] * M[2][1]
    if math.abs(det) < 1e-12 then det = (det >= 0 and 1 or -1) * 1e-12 end
    return {
        { M[2][2] / det, -M[1][2] / det},
        {-M[2][1] / det,  M[1][1] / det},
    }
end

-- Iterate P <- A'PA - (A'PB)(R+B'PB)^-1(B'PA) + Q to the fixed point, then
-- return K = (R + B'PB)^-1 B'PA.
local function solveDiscreteLqr(A, B, Q, R, iterations, tol)
    iterations = iterations or 5000
    tol = tol or 1e-11
    local P = {}
    for i = 1, #Q do P[i] = {} for j = 1, #Q do P[i][j] = Q[i][j] end end
    local At, Bt = matT(A), matT(B)
    local K = nil
    for _ = 1, iterations do
        local BtP = matMul(Bt, P)
        local inv = inv2(matAddScaled(R, matMul(BtP, B), 1))
        K = matMul(matMul(inv, BtP), A)
        local AtP = matMul(At, P)
        local Pn = matAddScaled(matAddScaled(matMul(AtP, A), matMul(matMul(AtP, B), K), -1), Q, 1)
        local diff = 0
        for i = 1, #P do for j = 1, #P do diff = diff + math.abs(Pn[i][j] - P[i][j]) end end
        P = Pn
        if diff < tol then break end
    end
    return K
end

-- Build the linearised unicycle error model about the reference trajectory and
-- solve the discrete LQR for the follower.
local function computeFollowerLqrGain(lqrCfg)
    local vRef = lqrCfg.vRef or 0.22
    local wRef = vRef / (lqrCfg.rho or 1.55)
    local dt = lqrCfg.dt or 0.05
    local Ac = {{0, wRef, 0}, {-wRef, 0, vRef}, {0, 0, 0}}
    local Bc = {{-1, 0}, {0, 0}, {0, -1}}
    local Ad, Bd = {}, {}
    for i = 1, 3 do
        Ad[i] = {}
        for j = 1, 3 do Ad[i][j] = (i == j and 1 or 0) + dt * Ac[i][j] end
        Bd[i] = {dt * Bc[i][1], dt * Bc[i][2]}
    end
    local Q = {{lqrCfg.q[1], 0, 0}, {0, lqrCfg.q[2], 0}, {0, 0, lqrCfg.q[3]}}
    local R = {{lqrCfg.r[1], 0}, {0, lqrCfg.r[2]}}
    return solveDiscreteLqr(Ad, Bd, Q, R)
end

function LqrStrategy:new(cfg, lqrCfg)
    -- Solve the Riccati equation in-scene; the gain is no longer hardcoded.
    lqrCfg.K = computeFollowerLqrGain(lqrCfg)
    return setmetatable({cfg = cfg, lqrCfg = lqrCfg}, self)
end

function LqrStrategy:compute(ctx)
    local dxTarget = ctx.ref.targetX - ctx.robotPos[1]
    local dyTarget = ctx.ref.targetY - ctx.robotPos[2]
    local c = math.cos(ctx.robotYaw)
    local s = math.sin(ctx.robotYaw)
    local eLong = c * dxTarget + s * dyTarget
    local eLat = -s * dxTarget + c * dyTarget
    local eYaw = MathEx.wrapAngle(ctx.ref.targetYaw - ctx.robotYaw)

    local k = self.lqrCfg.K
    local deltaV = -(k[1][1] * eLong + k[1][2] * eLat + k[1][3] * eYaw)
    local deltaW = -(k[2][1] * eLong + k[2][2] * eLat + k[2][3] * eYaw)
    local d = ctx.profile
    local vRef = MathEx.clamp(ctx.ref.targetSpeed, 0, d.vMax or self.cfg.vMax)
    local wRef = MathEx.clamp(ctx.ref.billYawRate, -(d.wMax or self.cfg.wMax), d.wMax or self.cfg.wMax)
    local v = vRef + deltaV
    local w = wRef + deltaW

    if math.abs(eLong) < (d.deadband or 0) and math.abs(eLat) < (d.deadband or 0) then
        if math.abs(v - vRef) < (d.commandDeadband or 0) then
            v = vRef
        end
    end

    if math.abs(eYaw) > 1.35 then
        v = 0
    elseif math.abs(eYaw) > 0.85 then
        v = MathEx.clamp(v, -0.02, 0.10)
    end

    return MathEx.clamp(v, d.vReverseMax or self.cfg.vReverseMax, d.vMax or self.cfg.vMax),
        MathEx.clamp(w, -(d.wMax or self.cfg.wMax), d.wMax or self.cfg.wMax)
end

local NmpcOptimizer = {}
NmpcOptimizer.__index = NmpcOptimizer

function NmpcOptimizer:new(cfg, robotCfg)
    local instance = setmetatable({cfg = cfg, robotCfg = robotCfg, seqV = {}, seqW = {}, initialized = false}, self)
    return instance
end

function NmpcOptimizer:reset()
    self.initialized = false
    self.seqV = {}
    self.seqW = {}
end

function NmpcOptimizer:initialize(actualV, actualW)
    if self.initialized then
        for i = 1, self.cfg.horizon - 1 do
            self.seqV[i] = self.seqV[i + 1] or self.seqV[i] or actualV
            self.seqW[i] = self.seqW[i + 1] or self.seqW[i] or actualW
        end
        self.seqV[self.cfg.horizon] = self.seqV[self.cfg.horizon - 1] or actualV
        self.seqW[self.cfg.horizon] = self.seqW[self.cfg.horizon - 1] or actualW
        return
    end

    for i = 1, self.cfg.horizon do
        self.seqV[i] = actualV
        self.seqW[i] = actualW
    end
    self.initialized = true
end

function NmpcOptimizer:cost(seqV, seqW, ctx)
    local x = ctx.robotPos[1]
    local y = ctx.robotPos[2]
    local yaw = ctx.robotYaw
    local bx = ctx.billPos[1]
    local by = ctx.billPos[2]
    local byaw = ctx.billYaw
    local previousV = ctx.runtime.actualV
    local previousW = ctx.runtime.actualW
    local d = ctx.profile
    local cost = 0

    for i = 1, self.cfg.horizon do
        local v = MathEx.clamp(seqV[i] or 0, d.vReverseMax or self.robotCfg.vReverseMax, d.vMax or self.robotCfg.vMax)
        local w = MathEx.clamp(seqW[i] or 0, -(d.wMax or self.robotCfg.wMax), d.wMax or self.robotCfg.wMax)
        local h = self.cfg.dt

        yaw = MathEx.wrapAngle(yaw + w * h)
        x = x + v * math.cos(yaw) * h
        y = y + v * math.sin(yaw) * h

        byaw = MathEx.wrapAngle(byaw + ctx.ref.billYawRate * h)
        bx = bx + ctx.ref.billSpeed * math.cos(byaw) * h
        by = by + ctx.ref.billSpeed * math.sin(byaw) * h

        local c = math.cos(byaw)
        local s = math.sin(byaw)
        local tx = bx - self.robotCfg.desiredDistance * c
        local ty = by - self.robotCfg.desiredDistance * s
        local dxBill = bx - x
        local dyBill = by - y
        local distance = math.sqrt(dxBill * dxBill + dyBill * dyBill)
        local eDistance = distance - self.robotCfg.desiredDistance
        local eTargetX = tx - x
        local eTargetY = ty - y
        local eHeading = MathEx.wrapAngle(MathEx.atan2(dyBill, dxBill) - yaw)

        local leftOmega = (v - 0.5 * self.robotCfg.trackWidth * w) / self.robotCfg.wheelRadius
        local rightOmega = (v + 0.5 * self.robotCfg.trackWidth * w) / self.robotCfg.wheelRadius
        local duV = v - previousV
        local duW = w - previousW
        local terminalScale = 1
        if i == self.cfg.horizon then
            terminalScale = self.cfg.terminal
        end

        cost = cost
            + terminalScale * self.cfg.qDistance * eDistance * eDistance
            + terminalScale * self.cfg.qTarget * (eTargetX * eTargetX + eTargetY * eTargetY)
            + self.cfg.qHeading * eHeading * eHeading
            + self.cfg.rV * v * v
            + self.cfg.rW * w * w
            + self.cfg.rWheel * (leftOmega * leftOmega + rightOmega * rightOmega)
            + self.cfg.sV * duV * duV
            + self.cfg.sW * duW * duW

        previousV = v
        previousW = w
    end

    return cost
end

function NmpcOptimizer:solve(ctx)
    self:initialize(ctx.runtime.actualV, ctx.runtime.actualW)
    local d = ctx.profile
    local vLo = d.vReverseMax or self.robotCfg.vReverseMax
    local vHi = d.vMax or self.robotCfg.vMax
    local wHi = d.wMax or self.robotCfg.wMax
    local bestCost = self:cost(self.seqV, self.seqW, ctx)

    -- Hooke-Jeeves pattern search: each pass probes +/- the current step on
    -- every command of the horizon, keeps any move that lowers the cost, and
    -- shrinks the step geometrically. Passes stop early once a whole sweep
    -- yields no improvement (local optimum reached for this step size).
    local stepV = self.cfg.stepV0
    local stepW = self.cfg.stepW0
    for _ = 1, self.cfg.iterations do
        local improved = false
        for i = 1, self.cfg.horizon do
            local originalV = self.seqV[i]
            for _, s in ipairs(SearchSigns) do
                self.seqV[i] = MathEx.clamp(originalV + s * stepV, vLo, vHi)
                local cost = self:cost(self.seqV, self.seqW, ctx)
                if cost < bestCost then
                    bestCost = cost
                    originalV = self.seqV[i]
                    improved = true
                end
            end
            self.seqV[i] = originalV

            local originalW = self.seqW[i]
            for _, s in ipairs(SearchSigns) do
                self.seqW[i] = MathEx.clamp(originalW + s * stepW, -wHi, wHi)
                local cost = self:cost(self.seqV, self.seqW, ctx)
                if cost < bestCost then
                    bestCost = cost
                    originalW = self.seqW[i]
                    improved = true
                end
            end
            self.seqW[i] = originalW
        end

        if not improved then
            -- Refine the resolution; stop when both steps hit their floor.
            stepV = stepV * self.cfg.stepShrink
            stepW = stepW * self.cfg.stepShrink
            if stepV < self.cfg.stepFloorV and stepW < self.cfg.stepFloorW then
                break
            end
        end
    end

    return MathEx.clamp(self.seqV[1] or 0, vLo, vHi),
        MathEx.clamp(self.seqW[1] or 0, -wHi, wHi)
end

local NmpcStrategy = {}
NmpcStrategy.__index = NmpcStrategy

function NmpcStrategy:new(optimizer)
    return setmetatable({optimizer = optimizer}, self)
end

function NmpcStrategy:compute(ctx)
    return self.optimizer:solve(ctx)
end

local StrategyRegistry = {}
StrategyRegistry.__index = StrategyRegistry

function StrategyRegistry:new(strategies)
    return setmetatable({strategies = strategies}, self)
end

function StrategyRegistry:forMode(mode)
    if mode == 'LQR' then return self.strategies.LQR end
    if mode == 'NMPC' then return self.strategies.NMPC end
    return self.strategies.PID
end

local FollowerApplication = {}
FollowerApplication.__index = FollowerApplication

function FollowerApplication:new()
    local handles = Handles:new(Paths)
    local drive = DifferentialDrive:new(Config, handles)
    local nmpcOptimizer = NmpcOptimizer:new(NmpcConfig, Config)

    return setmetatable({
        handles = handles,
        drive = drive,
        power = PowerTelemetry:new(Config, drive),
        billReference = BillReferenceEstimator:new(Config),
        runtime = RuntimeState:new(),
        signals = SignalBus:new(),
        nmpcOptimizer = nmpcOptimizer,
        strategies = StrategyRegistry:new({
            PID = PidStrategy:new(Config, Gains),
            LQR = LqrStrategy:new(Config, LqrConfig),
            NMPC = NmpcStrategy:new(nmpcOptimizer),
        }),
        mode = 'P',
    }, self)
end

function FollowerApplication:init()
    self.handles:resolve()
    self.mode = self.signals:readMode()
    self.runtime:resetAll()
    self:resetControlMemory()
    self.signals:publishFollower(self.mode, self.runtime, 'INIT', -1, 0, 0, 0, 0, 0)
    sim.addLog(sim.verbosity_scriptinfos, 'Pioneer Bill follower configured: P, PI, PID, LQR and NMPC modes.')
end

function FollowerApplication:resetControlMemory()
    self.runtime:resetControlMemory()
    self.power:reset()
    self.billReference:reset()
    self.nmpcOptimizer:reset()
    self.power:publish(0, 0, 0)
end

function FollowerApplication:readMeasurements(dt)
    local robotPos = sim.getObjectPosition(self.handles.robot)
    local billPos = sim.getObjectPosition(self.handles.bill)
    local robotOri = sim.getObjectOrientation(self.handles.robot)
    local billOri = sim.getObjectOrientation(self.handles.bill)
    local dx = billPos[1] - robotPos[1]
    local dy = billPos[2] - robotPos[2]

    return {
        robotPos = robotPos,
        billPos = billPos,
        robotYaw = robotOri[3],
        billYaw = billOri[3],
        distance = math.sqrt(dx * dx + dy * dy),
        heading = MathEx.wrapAngle(MathEx.atan2(dy, dx) - robotOri[3]),
        ref = self.billReference:read(billPos, billOri[3], dt),
    }
end

function FollowerApplication:updateErrorFilters(error, heading, profile, dt)
    local runtime = self.runtime

    if error * runtime.lastError < 0 then
        runtime.integral = runtime.integral * 0.35
    end

    if math.abs(heading) < 1.10 then
        runtime.integral = MathEx.clamp(runtime.integral + error * dt, -Config.integralLimit, Config.integralLimit)
    else
        runtime.integral = runtime.integral * 0.985
    end

    local derivative = 0
    if runtime.lastErrorValid then
        derivative = MathEx.clamp((error - runtime.lastError) / dt, -3.0, 3.0)
    end

    local derivativeAlpha = profile.derivativeAlpha or Config.derivativeAlpha
    runtime.filteredDerivative = derivativeAlpha * derivative + (1.0 - derivativeAlpha) * runtime.filteredDerivative
    runtime.lastError = error
    runtime.lastErrorValid = true

    local headingDerivative = 0
    if runtime.lastHeadingValid then
        headingDerivative = MathEx.clamp(MathEx.wrapAngle(heading - runtime.lastHeading) / dt, -4.0, 4.0)
    end
    runtime.lastHeading = heading
    runtime.lastHeadingValid = true

    return headingDerivative
end

function FollowerApplication:applySettleLogic(profile, error, heading, v, w)
    local state = 'FOLLOWING'
    local billStopped = sim.getInt32Signal('billStopped') == 1

    if billStopped and self.runtime.settledLatched and math.abs(error) < (profile.settleExit or 0.12) and math.abs(heading) < 0.30 then
        v = 0
        w = 0
        self.runtime.actualV = 0
        self.runtime.actualW = 0
        state = 'SETTLED'
    elseif billStopped and math.abs(error) < (profile.settleError or 0.08) and math.abs(heading) < 0.24 then
        self.runtime.settledLatched = true
        v = 0
        w = 0
        self.runtime.actualV = 0
        self.runtime.actualW = 0
        state = 'SETTLED'
    else
        self.runtime.settledLatched = false
    end

    if state ~= 'SETTLED' and math.abs(error) < 0.08 then
        state = 'TRACKING'
    end

    return state, v, w
end

function FollowerApplication:smoothCommand(profile, v, w, dt)
    local response = profile.accel or 5.0
    if math.abs(v) < math.abs(self.runtime.actualV) or (v * self.runtime.actualV) < 0 then
        response = profile.brake or response
    end

    self.runtime.actualV = MathEx.firstOrder(self.runtime.actualV, v, response, dt)
    self.runtime.actualW = MathEx.firstOrder(self.runtime.actualW, w, profile.turnAccel or response, dt)
end

function FollowerApplication:logState(state, distance, error)
    local t = sim.getSimulationTime()
    if state ~= self.runtime.lastState or (t - self.runtime.lastLogT) >= Config.logPeriod then
        sim.addLog(
            sim.verbosity_scriptinfos,
            string.format(
                'Follower %s state=%s distance=%.3f error=%.3f v=%.3f w=%.3f',
                self.mode,
                state,
                distance or -1,
                error or 0,
                self.runtime.actualV or 0,
                self.runtime.actualW or 0
            )
        )
        self.runtime.lastState = state
        self.runtime.lastLogT = t
    end
end

function FollowerApplication:actuate()
    if not self.handles:isReady() then
        self.signals:publishFollower(self.mode, self.runtime, 'ERROR_HANDLES', -1, 0, 0, 0, 0, 0)
        return
    end

    local newMode = self.signals:readMode()
    if newMode ~= self.mode then
        self.mode = newMode
        self:resetControlMemory()
    end

    local t = sim.getSimulationTime()
    local rawDt = t - self.runtime.lastT
    if rawDt <= 0.000001 then
        return
    end
    local dt = MathEx.clamp(rawDt, 0.0, 0.12)
    self.runtime.lastT = t

    local profile = DriveProfiles[self.mode] or DriveProfiles.P
    local measurements = self:readMeasurements(dt)
    local error = measurements.distance - Config.desiredDistance
    local headingDerivative = self:updateErrorFilters(error, measurements.heading, profile, dt)

    local ctx = {
        mode = self.mode,
        profile = profile,
        runtime = self.runtime,
        robotPos = measurements.robotPos,
        billPos = measurements.billPos,
        robotYaw = measurements.robotYaw,
        billYaw = measurements.billYaw,
        distance = measurements.distance,
        error = error,
        heading = measurements.heading,
        headingDerivative = headingDerivative,
        ref = measurements.ref,
    }

    local strategy = self.strategies:forMode(self.mode)
    local v, w = strategy:compute(ctx)
    local state
    state, v, w = self:applySettleLogic(profile, error, measurements.heading, v, w)

    self:smoothCommand(profile, v, w, dt)
    self.drive:setWheelSpeeds(self.runtime.actualV, self.runtime.actualW)
    self.drive:integrateKinematicBase(self.runtime.actualV, self.runtime.actualW, dt)
    self.power:publish(self.runtime.actualV, self.runtime.actualW, dt)
    self.signals:publishFollower(self.mode, self.runtime, state, measurements.distance, error, measurements.heading, self.runtime.actualV, self.runtime.actualW, self.runtime.filteredDerivative)
    self:logState(state, measurements.distance, error)
end

function FollowerApplication:cleanup()
    if self.handles.leftMotor >= 0 and self.handles.rightMotor >= 0 then
        self.drive:setWheelSpeeds(0, 0)
    end
    self.runtime.actualV = 0
    self.runtime.actualW = 0
    self.power:publish(0, 0, 0)
    self.signals:publishFollower(self.mode, self.runtime, 'STOPPED', -1, 0, 0, 0, 0, 0)
end

local app = nil

function sysCall_init()
    app = FollowerApplication:new()
    app:init()
end

function sysCall_actuation()
    if app then
        app:actuate()
    end
end

function sysCall_cleanup()
    if app then
        app:cleanup()
    end
end
