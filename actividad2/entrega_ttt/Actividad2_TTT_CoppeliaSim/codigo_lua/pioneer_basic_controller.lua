-- VIU SRM - Actividad 2
-- Basic Pioneer controller: potential fields + obstacle avoidance.
-- Baseline scene controller.

sim = require('sim')

local Config = {
    wheelRadius = 0.0975,
    trackWidth = 0.331,
    followDistance = 0.62,
    arrivalTolerance = 0.70,
    vMax = 0.44,
    wMax = 1.30,
    kAttraction = 0.82,
    kHeading = 1.85,
    avoidRange = 0.74,
    hardStopRange = 0.17,
    kRepulsion = 1.55,
    escapeTriggerTime = 1.35,
    escapeDuration = 1.10,
    escapeForwardSpeed = 0.08,
    logPeriod = 0.85,
}

local Paths = {
    robot = '/PioneerP3DX',
    leftMotor = '/PioneerP3DX/leftMotor',
    rightMotor = '/PioneerP3DX/rightMotor',
    targets = {'/mannequin', '/Bill', '/GoalStation'},
}

local MathEx = {}

function MathEx.clamp(value, lo, hi)
    if value < lo then return lo end
    if value > hi then return hi end
    return value
end

function MathEx.sign(value)
    if value >= 0 then return 1 end
    return -1
end

function MathEx.atan2(y, x)
    if math.atan2 then return math.atan2(y, x) end
    return math.atan(y, x)
end

local function safeGetObject(path)
    local ok, handle = pcall(sim.getObject, path)
    if ok and handle and handle >= 0 then return handle end
    return -1
end

local SignalBus = {}
SignalBus.__index = SignalBus

function SignalBus:new()
    return setmetatable({}, self)
end

function SignalBus:readInt(name, defaultValue)
    local value = sim.getInt32Signal(name)
    if value == nil then return defaultValue end
    return value
end

function SignalBus:publish(state, targetAlias, distance, minObstacle, risk, sensorCount)
    sim.setStringSignal('pioneerState', state)
    sim.setStringSignal('pioneerTargetAlias', targetAlias)
    sim.setFloatSignal('pioneerDistanceToTarget', distance or -1)
    sim.setFloatSignal('pioneerMinObstacleDistance', minObstacle or -1)
    sim.setFloatSignal('pioneerObstacleRisk', risk or 0)
    sim.setInt32Signal('pioneerSensorCount', sensorCount or 0)
    sim.setInt32Signal('pioneerArrived', state == 'ARRIVED' and 1 or 0)
    sim.setStringSignal('basicGuideCompliance', 'potential_fields+anti_collision+robotized_cell+furniture_sofa')
end

local Handles = {}
Handles.__index = Handles

function Handles:new(paths)
    local instance = setmetatable({paths = paths, targetAlias = ''}, self)
    instance:resolve()
    return instance
end

function Handles:resolve()
    self.robot = safeGetObject('..')
    if self.robot < 0 then
        self.robot = safeGetObject(self.paths.robot)
    end
    self.leftMotor = safeGetObject(self.paths.leftMotor)
    self.rightMotor = safeGetObject(self.paths.rightMotor)
    self.target = self:findTarget()
end

function Handles:isReady()
    return self.robot >= 0 and self.leftMotor >= 0 and self.rightMotor >= 0
end

function Handles:findTarget()
    for _, path in ipairs(self.paths.targets) do
        local handle = safeGetObject(path)
        if handle >= 0 then
            self.targetAlias = path
            return handle
        end
    end
    self.targetAlias = ''
    return -1
end

function Handles:ensureTarget()
    if self.target < 0 or not pcall(sim.getObjectPosition, self.target, self.robot) then
        self.target = self:findTarget()
    end
    return self.target >= 0
end

local DifferentialDrive = {}
DifferentialDrive.__index = DifferentialDrive

function DifferentialDrive:new(cfg, handles)
    return setmetatable({cfg = cfg, handles = handles}, self)
end

function DifferentialDrive:setVelocity(v, w)
    local left = (v - 0.5 * self.cfg.trackWidth * w) / self.cfg.wheelRadius
    local right = (v + 0.5 * self.cfg.trackWidth * w) / self.cfg.wheelRadius
    sim.setJointTargetVelocity(self.handles.leftMotor, left)
    sim.setJointTargetVelocity(self.handles.rightMotor, right)
end

local ObstacleField = {}
ObstacleField.__index = ObstacleField

function ObstacleField:new(cfg, handles)
    return setmetatable({cfg = cfg, handles = handles, sensors = {}, lastAvoidTurn = 1}, self)
end

function ObstacleField:load()
    self.sensors = {}
    for i = 0, 15 do
        local handle = safeGetObject('/PioneerP3DX/ultrasonicSensor[' .. i .. ']')
        if handle >= 0 then
            local ok, p = pcall(sim.getObjectPosition, handle, self.handles.robot)
            if ok and p then
                self.sensors[#self.sensors + 1] = {handle = handle, x = p[1], y = p[2]}
            end
        end
    end
end

function ObstacleField:count()
    return #self.sensors
end

function ObstacleField:read()
    local steer = 0
    local slow = 0
    local risk = 0
    local minDistance = math.huge
    local hardStop = false
    local turnHint = self.lastAvoidTurn
    local strongestFront = 0

    for _, sensor in ipairs(self.sensors) do
        local result, distance = sim.readProximitySensor(sensor.handle)
        if result and result > 0 and distance and distance > 0 then
            minDistance = math.min(minDistance, distance)

            if distance < self.cfg.avoidRange then
                local influence = (self.cfg.avoidRange - distance) / self.cfg.avoidRange
                influence = influence * influence

                local side = sensor.y
                if math.abs(side) < 0.035 then
                    side = -0.08 * self.lastAvoidTurn
                end

                local frontWeight = 0.30
                if sensor.x > 0.02 then
                    frontWeight = 1.0
                elseif sensor.x < -0.04 then
                    frontWeight = 0.18
                end

                steer = steer - MathEx.sign(side) * self.cfg.kRepulsion * influence * frontWeight
                slow = math.max(slow, influence * frontWeight)
                risk = math.max(risk, MathEx.clamp(influence * frontWeight, 0, 1))

                if sensor.x > -0.02 and influence * frontWeight > strongestFront then
                    strongestFront = influence * frontWeight
                    turnHint = -MathEx.sign(side)
                end

                if sensor.x > 0 and distance < self.cfg.hardStopRange then
                    hardStop = true
                    turnHint = -MathEx.sign(side)
                end
            end
        end
    end

    if strongestFront > 0.04 then
        self.lastAvoidTurn = turnHint
        if math.abs(steer) < 0.20 then
            steer = steer + self.lastAvoidTurn * self.cfg.kRepulsion * strongestFront * 0.72
        end
    end

    if minDistance == math.huge then
        minDistance = -1
    end

    return {
        steer = steer,
        slow = MathEx.clamp(slow, 0, 1),
        minDistance = minDistance,
        hardStop = hardStop,
        risk = risk,
        turnHint = self.lastAvoidTurn,
    }
end

local StateLogger = {}
StateLogger.__index = StateLogger

function StateLogger:new(cfg, obstacleField)
    return setmetatable({cfg = cfg, obstacleField = obstacleField, lastLogTime = -1000, lastState = ''}, self)
end

function StateLogger:log(state, targetAlias, distance, minObstacle, risk)
    local t = sim.getSimulationTime()
    if state ~= self.lastState or (t - self.lastLogTime) >= self.cfg.logPeriod then
        sim.addLog(
            sim.verbosity_scriptinfos,
            string.format(
                'Basic A2 state=%s target=%s distance=%.2f minObstacle=%.2f risk=%.2f sensors=%d',
                state,
                targetAlias ~= '' and targetAlias or 'none',
                distance or -1,
                minObstacle or -1,
                risk or 0,
                self.obstacleField:count()
            )
        )
        self.lastState = state
        self.lastLogTime = t
    end
end

local PotentialFieldController = {}
PotentialFieldController.__index = PotentialFieldController

function PotentialFieldController:new(cfg, obstacleField)
    return setmetatable({
        cfg = cfg,
        obstacleField = obstacleField,
        bestDistance = math.huge,
        lastProgressTime = 0,
        escapeUntil = 0,
        escapeTurn = 1,
    }, self)
end

function PotentialFieldController:updateEscape(distance, obstacle)
    local now = sim.getSimulationTime()
    if distance + 0.04 < self.bestDistance then
        self.bestDistance = distance
        self.lastProgressTime = now
    elseif self.bestDistance == math.huge then
        self.bestDistance = distance
        self.lastProgressTime = now
    end

    local nearObstacle = obstacle.minDistance > 0 and obstacle.minDistance < self.cfg.avoidRange and obstacle.slow > 0.12
    local farFromGoal = distance > self.cfg.arrivalTolerance + 0.22
    if nearObstacle and farFromGoal and now - self.lastProgressTime > self.cfg.escapeTriggerTime and now >= self.escapeUntil then
        self.escapeTurn = obstacle.turnHint or self.obstacleField.lastAvoidTurn
        self.escapeUntil = now + self.cfg.escapeDuration
        self.lastProgressTime = now
        self.bestDistance = distance
    end

    return now < self.escapeUntil
end

function PotentialFieldController:compute(distance, heading)
    local obstacle = self.obstacleField:read()
    if distance <= self.cfg.arrivalTolerance then
        return 'ARRIVED', 0, 0, obstacle
    end

    local state = 'ROUTE'
    if obstacle.minDistance > 0 and obstacle.minDistance < self.cfg.avoidRange then
        state = 'AVOIDING'
    end

    local forwardScale = MathEx.clamp(math.cos(heading), 0, 1)
    local v = MathEx.clamp(
        self.cfg.kAttraction * math.max(distance - self.cfg.followDistance, 0) * forwardScale,
        0,
        self.cfg.vMax
    )
    if math.abs(heading) > 1.20 then
        v = math.min(v, 0.08)
    end

    local w = MathEx.clamp(self.cfg.kHeading * heading + obstacle.steer, -self.cfg.wMax, self.cfg.wMax)
    local escaping = self:updateEscape(distance, obstacle)

    if escaping then
        state = 'AVOIDING'
        if obstacle.hardStop then
            v = -0.04
        else
            v = math.max(v, self.cfg.escapeForwardSpeed)
        end
        w = MathEx.clamp(self.escapeTurn * self.cfg.wMax * 0.82, -self.cfg.wMax, self.cfg.wMax)
    elseif obstacle.hardStop then
        state = 'AVOIDING'
        v = -0.04
        w = MathEx.clamp(self.obstacleField.lastAvoidTurn * self.cfg.wMax * 0.70, -self.cfg.wMax, self.cfg.wMax)
    else
        v = v * (1 - 0.55 * obstacle.slow)
    end

    return state, v, w, obstacle
end

local BasicFollowerApp = {}
BasicFollowerApp.__index = BasicFollowerApp

function BasicFollowerApp:new()
    local handles = Handles:new(Paths)
    local obstacleField = ObstacleField:new(Config, handles)
    return setmetatable({
        handles = handles,
        signals = SignalBus:new(),
        drive = DifferentialDrive:new(Config, handles),
        obstacleField = obstacleField,
        controller = PotentialFieldController:new(Config, obstacleField),
        logger = StateLogger:new(Config, obstacleField),
    }, self)
end

function BasicFollowerApp:init()
    self.handles:resolve()
    self.obstacleField:load()

    if sim.getInt32Signal('missionReady') == nil then
        sim.setInt32Signal('missionReady', 1)
    end

    self.signals:publish('INIT', self.handles.targetAlias, -1, -1, 0, self.obstacleField:count())
    sim.addLog(sim.verbosity_scriptinfos, 'Actividad 2 basic controller configured: potential fields + anti-collision + robotized cell.')
end

function BasicFollowerApp:stopAndPublish(state, distance, minObstacle, risk)
    self.drive:setVelocity(0, 0)
    self.signals:publish(state, self.handles.targetAlias, distance, minObstacle, risk, self.obstacleField:count())
    self.logger:log(state, self.handles.targetAlias, distance, minObstacle, risk)
end

function BasicFollowerApp:actuate()
    if not self.handles:isReady() then
        self.signals:publish('ERROR_HANDLES', self.handles.targetAlias, -1, -1, 0, self.obstacleField:count())
        return
    end

    if self.signals:readInt('missionReady', 1) == 0 then
        self:stopAndPublish('HOLD', -1, -1, 0)
        return
    end

    if not self.handles:ensureTarget() then
        self:stopAndPublish('NO_TARGET', -1, -1, 0)
        return
    end

    local rel = sim.getObjectPosition(self.handles.target, self.handles.robot)
    local dx = rel[1]
    local dy = rel[2]
    local distance = math.sqrt(dx * dx + dy * dy)
    local heading = MathEx.atan2(dy, dx)
    local state, v, w, obstacle = self.controller:compute(distance, heading)

    self.drive:setVelocity(v, w)
    self.signals:publish(state, self.handles.targetAlias, distance, obstacle.minDistance, obstacle.risk, self.obstacleField:count())
    self.logger:log(state, self.handles.targetAlias, distance, obstacle.minDistance, obstacle.risk)
end

function BasicFollowerApp:cleanup()
    if self.handles.leftMotor >= 0 and self.handles.rightMotor >= 0 then
        self.drive:setVelocity(0, 0)
    end
    self.signals:publish('STOPPED', self.handles.targetAlias, -1, -1, 0, self.obstacleField:count())
end

local app = nil

function sysCall_init()
    app = BasicFollowerApp:new()
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
