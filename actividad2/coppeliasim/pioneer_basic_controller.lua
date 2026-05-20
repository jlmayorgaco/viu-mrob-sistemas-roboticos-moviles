-- VIU SRM - Actividad 2
-- Basic Pioneer controller: potential fields + obstacle avoidance.
-- Scope intentionally limited to the official guide.

sim = require('sim')

local cfg = {
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
    logPeriod = 0.85,
}

local robot = -1
local leftMotor = -1
local rightMotor = -1
local target = -1
local targetAlias = ''
local sensors = {}
local lastLogTime = -1000
local lastState = ''
local lastAvoidTurn = 1

local function clamp(value, lo, hi)
    if value < lo then return lo end
    if value > hi then return hi end
    return value
end

local function sign(value)
    if value >= 0 then return 1 end
    return -1
end

local function atan2(y, x)
    if math.atan2 then return math.atan2(y, x) end
    return math.atan(y, x)
end

local function safeGetObject(path)
    local ok, handle = pcall(sim.getObject, path)
    if ok and handle and handle >= 0 then
        return handle
    end
    return -1
end

local function readIntSignal(name, default)
    local value = sim.getInt32Signal(name)
    if value == nil then return default end
    return value
end

local function setWheelSpeeds(v, w)
    local vLeft = (v - 0.5 * cfg.trackWidth * w) / cfg.wheelRadius
    local vRight = (v + 0.5 * cfg.trackWidth * w) / cfg.wheelRadius
    sim.setJointTargetVelocity(leftMotor, vLeft)
    sim.setJointTargetVelocity(rightMotor, vRight)
end

local function findTarget()
    local candidates = {'/mannequin', '/Bill', '/GoalStation'}
    for _, path in ipairs(candidates) do
        local handle = safeGetObject(path)
        if handle >= 0 then
            targetAlias = path
            return handle
        end
    end
    targetAlias = ''
    return -1
end

local function loadSensors()
    sensors = {}
    for i = 0, 15 do
        local handle = safeGetObject('/PioneerP3DX/ultrasonicSensor[' .. i .. ']')
        if handle >= 0 then
            local ok, p = pcall(sim.getObjectPosition, handle, robot)
            if ok and p then
                sensors[#sensors + 1] = {handle = handle, x = p[1], y = p[2]}
            end
        end
    end
end

local function readObstacleField()
    local steer = 0
    local slow = 0
    local risk = 0
    local minDistance = math.huge
    local hardStop = false

    for _, s in ipairs(sensors) do
        local result, distance = sim.readProximitySensor(s.handle)
        if result and result > 0 and distance and distance > 0 then
            if distance < minDistance then
                minDistance = distance
            end
            if distance < cfg.avoidRange then
                local influence = (cfg.avoidRange - distance) / cfg.avoidRange
                influence = influence * influence
                local side = s.y
                if math.abs(side) < 0.035 then
                    side = -0.08 * lastAvoidTurn
                end
                local frontWeight = 0.30
                if s.x > 0.02 then
                    frontWeight = 1.0
                elseif s.x < -0.04 then
                    frontWeight = 0.18
                end
                steer = steer - sign(side) * cfg.kRepulsion * influence * frontWeight
                slow = math.max(slow, influence * frontWeight)
                risk = math.max(risk, clamp(influence * frontWeight, 0, 1))
                if s.x > 0 and distance < cfg.hardStopRange then
                    hardStop = true
                    lastAvoidTurn = -sign(side)
                end
            end
        end
    end

    if minDistance == math.huge then
        minDistance = -1
    end
    return steer, clamp(slow, 0, 1), minDistance, hardStop, risk
end

local function publishTelemetry(state, distance, minObstacle, risk)
    sim.setStringSignal('pioneerState', state)
    sim.setStringSignal('pioneerTargetAlias', targetAlias)
    sim.setFloatSignal('pioneerDistanceToTarget', distance or -1)
    sim.setFloatSignal('pioneerMinObstacleDistance', minObstacle or -1)
    sim.setFloatSignal('pioneerObstacleRisk', risk or 0)
    sim.setInt32Signal('pioneerSensorCount', #sensors)
    sim.setInt32Signal('pioneerArrived', state == 'ARRIVED' and 1 or 0)
    sim.setStringSignal('basicGuideCompliance', 'potential_fields+anti_collision+robotized_cell')
end

local function logState(state, distance, minObstacle, risk)
    local t = sim.getSimulationTime()
    if state ~= lastState or (t - lastLogTime) >= cfg.logPeriod then
        sim.addLog(
            sim.verbosity_scriptinfos,
            string.format(
                'Basic A2 state=%s target=%s distance=%.2f minObstacle=%.2f risk=%.2f sensors=%d',
                state,
                targetAlias ~= '' and targetAlias or 'none',
                distance or -1,
                minObstacle or -1,
                risk or 0,
                #sensors
            )
        )
        lastState = state
        lastLogTime = t
    end
end

function sysCall_init()
    robot = safeGetObject('..')
    if robot < 0 then
        robot = safeGetObject('/PioneerP3DX')
    end
    leftMotor = safeGetObject('/PioneerP3DX/leftMotor')
    rightMotor = safeGetObject('/PioneerP3DX/rightMotor')
    target = findTarget()
    loadSensors()

    if sim.getInt32Signal('missionReady') == nil then
        sim.setInt32Signal('missionReady', 1)
    end
    publishTelemetry('INIT', -1, -1, 0)
    sim.addLog(sim.verbosity_scriptinfos, 'Actividad 2 basic controller ready: potential fields + anti-collision + robotized cell.')
end

function sysCall_actuation()
    if leftMotor < 0 or rightMotor < 0 or robot < 0 then
        publishTelemetry('ERROR_HANDLES', -1, -1, 0)
        return
    end

    if readIntSignal('missionReady', 1) == 0 then
        setWheelSpeeds(0, 0)
        publishTelemetry('HOLD', -1, -1, 0)
        logState('HOLD', -1, -1, 0)
        return
    end

    if target < 0 or not pcall(sim.getObjectPosition, target, robot) then
        target = findTarget()
    end
    if target < 0 then
        setWheelSpeeds(0, 0)
        publishTelemetry('NO_TARGET', -1, -1, 0)
        logState('NO_TARGET', -1, -1, 0)
        return
    end

    local rel = sim.getObjectPosition(target, robot)
    local dx = rel[1]
    local dy = rel[2]
    local distance = math.sqrt(dx * dx + dy * dy)
    local heading = atan2(dy, dx)
    local obstacleSteer, obstacleSlow, minObstacle, hardStop, risk = readObstacleField()

    if distance <= cfg.arrivalTolerance then
        setWheelSpeeds(0, 0)
        publishTelemetry('ARRIVED', distance, minObstacle, risk)
        logState('ARRIVED', distance, minObstacle, risk)
        return
    end

    local state = 'ROUTE'
    if minObstacle > 0 and minObstacle < cfg.avoidRange then
        state = 'AVOIDING'
    end

    local forwardScale = clamp(math.cos(heading), 0, 1)
    local v = clamp(cfg.kAttraction * math.max(distance - cfg.followDistance, 0) * forwardScale, 0, cfg.vMax)
    if math.abs(heading) > 1.20 then
        v = math.min(v, 0.08)
    end
    local w = clamp(cfg.kHeading * heading + obstacleSteer, -cfg.wMax, cfg.wMax)

    if hardStop then
        state = 'AVOIDING'
        v = -0.04
        w = clamp(lastAvoidTurn * cfg.wMax * 0.70, -cfg.wMax, cfg.wMax)
    else
        v = v * (1 - 0.55 * obstacleSlow)
    end

    setWheelSpeeds(v, w)
    publishTelemetry(state, distance, minObstacle, risk)
    logState(state, distance, minObstacle, risk)
end

function sysCall_cleanup()
    if leftMotor >= 0 and rightMotor >= 0 then
        setWheelSpeeds(0, 0)
    end
    publishTelemetry('STOPPED', -1, -1, 0)
end
