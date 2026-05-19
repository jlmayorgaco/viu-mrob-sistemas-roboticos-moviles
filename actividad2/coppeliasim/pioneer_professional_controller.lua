-- VIU SRM - Actividad 2
-- Pioneer P3DX professional controller for CoppeliaSim/Lua.
-- Covers potential-field navigation, waypoint routing, ultrasonic + virtual
-- safety sensors, reactive anti-collision, stuck recovery, battery policy,
-- speed zones, sensor degradation handling and cell telemetry.

sim = require('sim')

local cfg = {
    wheelRadius = 0.0975,
    trackWidth = 0.331,
    followDistance = 0.72,
    arrivalTolerance = 0.35,
    waypointTolerance = 0.64,
    vMax = 0.55,
    wMax = 1.45,
    kAttraction = 0.95,
    kHeading = 2.05,
    avoidRange = 0.72,
    virtualAvoidRange = 1.08,
    hardStopRange = 0.16,
    kRepulsion = 1.78,
    virtualSensorWeight = 0.78,
    maxAccel = 0.52,
    maxAngularAccel = 2.8,
    stuckTimeout = 4.5,
    stuckDistance = 0.08,
    recoveryDuration = 0.85,
    logPeriod = 0.75,
    batteryStart = 100.0,
    batteryLowThreshold = 60.0,
    batteryCriticalThreshold = 30.0,
    batteryIdleDrain = 0.035,
    batteryMotionDrain = 1.55,
    batteryTurnDrain = 0.045,
    batteryChargeRate = 4.8,
    lowBatterySpeedFactor = 0.72,
    criticalBatterySpeedFactor = 0.38,
    dockingChargeDistance = 0.58,
    sensorNoiseStd = 0.018,
}

local robot = -1
local leftMotor = -1
local rightMotor = -1
local target = -1
local targetAlias = ''
local sensors = {}
local dockingStation = -1
local route = {}
local routeIndex = 1
local routeComplete = false
local lastLogTime = -1000
local lastState = ''
local lastControlTime = -1
local previousV = 0
local previousW = 0
local progressDistance = math.huge
local progressTime = 0
local recoveryUntil = 0
local recoverySide = 1
local batteryLevel = cfg.batteryStart
local batteryMode = 'NORMAL'
local chargingActive = 0
local lastBatteryTime = -1
local speedZoneName = 'DEFAULT'
local speedLimitFactor = 1.0
local sensorFaultActive = 0
local sensorFaultCount = 0
local hmi = {}

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

local function tableContains(values, value)
    for _, item in ipairs(values) do
        if item == value then return true end
    end
    return false
end

local function readIntSignal(name, default)
    local value = sim.getInt32Signal(name)
    if value == nil then return default end
    return value
end

local function readFloatSignal(name, default)
    local value = sim.getFloatSignal(name)
    if value == nil then return default end
    return value
end

local function setShapeColorSafe(handle, rgb)
    if handle and handle >= 0 then
        pcall(sim.setShapeColor, handle, nil, sim.colorcomponent_ambient_diffuse, rgb)
    end
end

local function hmiHandle(alias)
    if hmi[alias] == nil then
        hmi[alias] = safeGetObject('/' .. alias)
    end
    return hmi[alias]
end

local function setHmiColor(alias, rgb)
    setShapeColorSafe(hmiHandle(alias), rgb)
end

local function updateBatteryTelemetry()
    local t = sim.getSimulationTime()
    local dt = 0.05
    if lastBatteryTime >= 0 then
        dt = clamp(t - lastBatteryTime, 0.0, 0.20)
    end
    lastBatteryTime = t

    local override = readFloatSignal('pioneerBatteryOverride', -1)
    if override >= 0 then
        batteryLevel = clamp(override, 0, 100)
    else
        local drain = cfg.batteryIdleDrain * dt
            + math.abs(previousV) * cfg.batteryMotionDrain * dt
            + math.abs(previousW) * cfg.batteryTurnDrain * dt

        chargingActive = 0
        if dockingStation >= 0 and robot >= 0 then
            local ok, rel = pcall(sim.getObjectPosition, dockingStation, robot)
            if ok and rel then
                local d = math.sqrt(rel[1] * rel[1] + rel[2] * rel[2])
                if d <= cfg.dockingChargeDistance then
                    chargingActive = 1
                    drain = drain - cfg.batteryChargeRate * dt
                end
            end
        end
        batteryLevel = clamp(batteryLevel - drain, 0, 100)
    end

    if chargingActive == 1 and batteryLevel < 99.5 then
        batteryMode = 'CHARGING'
    elseif batteryLevel <= cfg.batteryCriticalThreshold then
        batteryMode = 'CRITICAL'
    elseif batteryLevel <= cfg.batteryLowThreshold then
        batteryMode = 'LOW'
    else
        batteryMode = 'NORMAL'
    end
end

local function updateSpeedZone()
    speedZoneName = 'DEFAULT'
    speedLimitFactor = 1.0

    local ok, p = pcall(sim.getObjectPosition, robot, -1)
    if ok and p then
        local x = p[1]
        local y = p[2]
        if x >= -1.95 and x <= -1.10 and y >= -2.32 and y <= -1.55 then
            speedZoneName = 'DOCKING'
            speedLimitFactor = 0.55
        elseif x >= 0.20 and x <= 1.25 and y >= -0.72 and y <= -0.14 then
            speedZoneName = 'NARROW_PASSAGE'
            speedLimitFactor = 0.45
        elseif x >= 1.02 and x <= 1.90 and y >= 0.74 and y <= 1.66 then
            speedZoneName = 'TARGET_ZONE'
            speedLimitFactor = 0.42
        elseif y >= -1.78 and y <= -1.30 and x >= -1.35 and x <= 2.20 then
            speedZoneName = 'APPROACH_LANE'
            speedLimitFactor = 0.82
        end
    end

    if batteryMode == 'LOW' then
        speedLimitFactor = math.min(speedLimitFactor, cfg.lowBatterySpeedFactor)
    elseif batteryMode == 'CRITICAL' then
        speedLimitFactor = math.min(speedLimitFactor, cfg.criticalBatterySpeedFactor)
    end
end

local function updateHMI(state)
    local dim = {0.06, 0.07, 0.08}
    local green = {0.02, 0.72, 0.18}
    local yellow = {0.95, 0.68, 0.05}
    local red = {0.95, 0.06, 0.04}
    local blue = {0.10, 0.34, 0.92}
    local white = {0.86, 0.92, 0.96}

    local activeBatteryColor = green
    if batteryMode == 'LOW' then activeBatteryColor = yellow end
    if batteryMode == 'CRITICAL' then activeBatteryColor = red end
    local litSegments = math.max(1, math.ceil(batteryLevel / 10.0))
    for i = 1, 10 do
        if i <= litSegments then
            setHmiColor('VIU_HMI_Battery_' .. i, activeBatteryColor)
        else
            setHmiColor('VIU_HMI_Battery_' .. i, dim)
        end
    end

    local states = {'ROUTE', 'AVOIDING', 'RECOVERY', 'HOLD', 'ARRIVED'}
    for _, s in ipairs(states) do
        local color = dim
        if state == s or (state == 'TRACKING' and s == 'ROUTE') then
            color = white
            if s == 'AVOIDING' then color = yellow end
            if s == 'RECOVERY' or s == 'HOLD' then color = red end
            if s == 'ARRIVED' then color = green end
        end
        setHmiColor('VIU_HMI_State_' .. s, color)
    end

    local zones = {'DEFAULT', 'APPROACH_LANE', 'NARROW_PASSAGE', 'TARGET_ZONE', 'DOCKING'}
    for _, z in ipairs(zones) do
        setHmiColor('VIU_HMI_Zone_' .. z, z == speedZoneName and blue or dim)
    end

    setHmiColor('VIU_HMI_SensorFault', sensorFaultActive == 1 and red or dim)
    setHmiColor('VIU_HMI_BatteryLow', (batteryMode == 'LOW' or batteryMode == 'CRITICAL') and yellow or dim)
    setHmiColor('VIU_HMI_Charging', chargingActive == 1 and blue or dim)
end

local function publishTelemetry(state, distance, minObstacleDistance, obstacleRisk)
    sim.setStringSignal('pioneerState', state)
    sim.setStringSignal('pioneerTargetAlias', targetAlias or '')
    sim.setFloatSignal('pioneerDistanceToTarget', distance or -1)
    sim.setFloatSignal('pioneerMinObstacleDistance', minObstacleDistance or -1)
    sim.setFloatSignal('pioneerObstacleRisk', obstacleRisk or 0)
    sim.setInt32Signal('pioneerRouteIndex', routeIndex)
    sim.setInt32Signal('pioneerSensorCount', #sensors)
    sim.setFloatSignal('pioneerBatteryLevel', batteryLevel)
    sim.setStringSignal('pioneerBatteryMode', batteryMode)
    sim.setInt32Signal('pioneerCharging', chargingActive)
    sim.setStringSignal('pioneerSpeedZone', speedZoneName)
    sim.setFloatSignal('pioneerSpeedLimitFactor', speedLimitFactor)
    sim.setInt32Signal('pioneerSensorFaultActive', sensorFaultActive)
    sim.setInt32Signal('pioneerSensorFaultCount', sensorFaultCount)
    if state == 'ARRIVED' then
        sim.setInt32Signal('pioneerArrived', 1)
    else
        sim.setInt32Signal('pioneerArrived', 0)
    end
    updateHMI(state)
end

local function setWheelSpeedsRaw(v, w)
    local vLeft = (v - 0.5 * cfg.trackWidth * w) / cfg.wheelRadius
    local vRight = (v + 0.5 * cfg.trackWidth * w) / cfg.wheelRadius
    sim.setJointTargetVelocity(leftMotor, vLeft)
    sim.setJointTargetVelocity(rightMotor, vRight)
end

local function rateLimit(targetValue, previousValue, maxStep)
    return clamp(targetValue, previousValue - maxStep, previousValue + maxStep)
end

local function setWheelSpeeds(v, w)
    local t = sim.getSimulationTime()
    local dt = 0.05
    if lastControlTime >= 0 then
        dt = clamp(t - lastControlTime, 0.01, 0.12)
    end
    lastControlTime = t

    local limitedV = rateLimit(v, previousV, cfg.maxAccel * dt)
    local limitedW = rateLimit(w, previousW, cfg.maxAngularAccel * dt)
    previousV = limitedV
    previousW = limitedW
    setWheelSpeedsRaw(limitedV, limitedW)
end

local function findTarget()
    local candidates = {'/mannequin', '/Bill', '/GoalStation', '/PioneerGoal'}
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

local function loadRoute()
    route = {}
    local names = {
        '/VIU_Waypoint_1',
        '/VIU_Waypoint_2',
        '/VIU_Waypoint_3',
        '/VIU_Waypoint_4',
        '/mannequin',
    }
    for _, name in ipairs(names) do
        local handle = safeGetObject(name)
        if handle >= 0 then
            route[#route + 1] = {handle = handle, alias = name}
        end
    end
    routeIndex = 1
    routeComplete = #route == 0
end

local function selectTarget()
    local useWaypoints = readIntSignal('pioneerUseWaypoints', 1)
    if useWaypoints ~= 0 and #route > 0 and not routeComplete then
        routeIndex = clamp(routeIndex, 1, #route)
        targetAlias = route[routeIndex].alias
        return route[routeIndex].handle
    end
    return findTarget()
end

local function addSensor(handle, label, isVirtual)
    if handle < 0 then return end
    local ok, p = pcall(sim.getObjectPosition, handle, robot)
    if ok and p then
        sensors[#sensors + 1] = {
            handle = handle,
            label = label,
            x = p[1],
            y = p[2],
            isVirtual = isVirtual,
            range = isVirtual and cfg.virtualAvoidRange or cfg.avoidRange,
            noisePhase = (#sensors + 1) * 1.137,
        }
    end
end

local function loadSensors()
    sensors = {}
    for i = 0, 15 do
        addSensor(safeGetObject('/PioneerP3DX/ultrasonicSensor[' .. i .. ']'), 'US' .. i, false)
    end

    local virtualNames = {
        '/PioneerP3DX/VIU_Virtual_Lidar_Front',
        '/PioneerP3DX/VIU_Virtual_Lidar_FrontLeft',
        '/PioneerP3DX/VIU_Virtual_Lidar_FrontRight',
        '/PioneerP3DX/VIU_Virtual_Safety_Left',
        '/PioneerP3DX/VIU_Virtual_Safety_Right',
        '/PioneerP3DX/VIU_Virtual_LongRange_Center',
    }
    for _, path in ipairs(virtualNames) do
        addSensor(safeGetObject(path), path, true)
    end
end

local function readObstacleField()
    local steer = 0
    local slow = 0
    local obstacleRisk = 0
    local minDistance = math.huge
    local hardStop = false
    local closestSide = 0
    local frontMin = math.huge
    local t = sim.getSimulationTime()
    local noiseEnabled = readIntSignal('pioneerSensorNoiseEnabled', 1)
    local faultMode = readIntSignal('pioneerSensorFaultMode', 0)
    sensorFaultActive = 0
    sensorFaultCount = 0

    for _, s in ipairs(sensors) do
        local result, distance = sim.readProximitySensor(s.handle)
        local faulted = faultMode ~= 0
            and (
                s.label == 'US2'
                or s.label == 'US3'
                or string.find(s.label, 'FrontLeft', 1, true) ~= nil
            )
        if faulted then
            sensorFaultActive = 1
            sensorFaultCount = sensorFaultCount + 1
            if math.floor(t * 2.0) % 2 == 0 then
                result = 0
                distance = nil
            elseif distance ~= nil then
                distance = distance + 0.16
            end
        end
        if result and result > 0 and distance and distance > 0 then
            if noiseEnabled ~= 0 then
                local noise = math.sin(t * 7.13 + (s.noisePhase or 0)) * cfg.sensorNoiseStd
                distance = clamp(distance + noise, 0.025, s.range + 0.35)
            end
            if distance < minDistance then
                minDistance = distance
                closestSide = s.y
            end
            if s.x > 0.02 and distance < frontMin then
                frontMin = distance
            end

            local activeRange = s.range
            if distance < activeRange then
                local influence = (activeRange - distance) / activeRange
                influence = influence * influence
                if s.isVirtual then
                    influence = influence * cfg.virtualSensorWeight
                end

                local side = s.y
                if math.abs(side) < 0.035 then
                    side = -0.09 * recoverySide
                end

                local frontWeight = 0.38
                if s.x > 0.02 then
                    frontWeight = 1.0
                elseif s.x < -0.04 then
                    frontWeight = 0.22
                end

                steer = steer - sign(side) * cfg.kRepulsion * influence * frontWeight
                slow = math.max(slow, influence * frontWeight)
                obstacleRisk = math.max(obstacleRisk, clamp(influence * frontWeight, 0, 1))

                if (not s.isVirtual) and s.x > 0 and distance < cfg.hardStopRange then
                    hardStop = true
                end
            end
        end
    end

    if minDistance == math.huge then
        minDistance = -1
    end
    if frontMin == math.huge then
        frontMin = -1
    end
    return steer, clamp(slow, 0, 1), minDistance, hardStop, closestSide, obstacleRisk, frontMin
end

local function updateRoute(distance)
    if #route == 0 or routeComplete then return end
    if routeIndex < #route and distance <= cfg.waypointTolerance then
        routeIndex = routeIndex + 1
        targetAlias = route[routeIndex].alias
        sim.setStringSignal('pioneerRouteEvent', 'NEXT_WAYPOINT:' .. targetAlias)
        progressDistance = math.huge
        progressTime = sim.getSimulationTime()
    elseif routeIndex >= #route and distance <= cfg.arrivalTolerance then
        routeComplete = true
    end
end

local function updateRecovery(distance, closestSide)
    local t = sim.getSimulationTime()
    if progressDistance == math.huge or distance < progressDistance - cfg.stuckDistance then
        progressDistance = distance
        progressTime = t
        return false
    end

    if t < recoveryUntil then
        return true
    end

    if distance > cfg.followDistance + 0.25 and (t - progressTime) > cfg.stuckTimeout then
        recoveryUntil = t + cfg.recoveryDuration
        recoverySide = -recoverySide
        if closestSide ~= nil and math.abs(closestSide) > 0.035 then
            recoverySide = sign(closestSide)
        end
        progressDistance = distance
        progressTime = t
        sim.setStringSignal('pioneerRouteEvent', 'STUCK_RECOVERY')
        return true
    end
    return false
end

local function logState(state, distance, minObstacleDistance, obstacleRisk)
    local t = sim.getSimulationTime()
    if state ~= lastState or (t - lastLogTime) >= cfg.logPeriod then
        sim.addLog(
            sim.verbosity_scriptinfos,
            string.format(
                'Pioneer state=%s target=%s route=%d/%d distance=%.2f minObstacle=%.2f risk=%.2f sensors=%d',
                state,
                targetAlias ~= '' and targetAlias or 'none',
                routeIndex,
                #route,
                distance or -1,
                minObstacleDistance or -1,
                obstacleRisk or 0,
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
    dockingStation = safeGetObject('/DockingStation')

    loadRoute()
    target = selectTarget()
    loadSensors()

    if sim.getInt32Signal('missionReady') == nil then
        sim.setInt32Signal('missionReady', 1)
    end
    if sim.getInt32Signal('pioneerUseWaypoints') == nil then
        sim.setInt32Signal('pioneerUseWaypoints', 1)
    end
    if sim.getInt32Signal('pioneerSensorNoiseEnabled') == nil then
        sim.setInt32Signal('pioneerSensorNoiseEnabled', 1)
    end
    if sim.getInt32Signal('pioneerSensorFaultMode') == nil then
        sim.setInt32Signal('pioneerSensorFaultMode', 0)
    end
    if sim.getFloatSignal('pioneerBatteryOverride') == nil then
        sim.setFloatSignal('pioneerBatteryOverride', -1)
    end

    progressTime = sim.getSimulationTime()
    updateBatteryTelemetry()
    updateSpeedZone()
    publishTelemetry('INIT', -1, -1, 0)
    sim.addLog(sim.verbosity_scriptinfos, 'Actividad 2 Pioneer controller ready: FSM + potential fields + anti-collision + virtual sensors + battery + speed zones + HMI + scenarios.')
end

function sysCall_actuation()
    if leftMotor < 0 or rightMotor < 0 or robot < 0 then
        publishTelemetry('ERROR_HANDLES', -1, -1, 0)
        return
    end

    updateBatteryTelemetry()
    updateSpeedZone()

    local missionReady = readIntSignal('missionReady', 1)
    if missionReady == 0 then
        setWheelSpeeds(0, 0)
        publishTelemetry('HOLD', -1, -1, 0)
        logState('HOLD', -1, -1, 0)
        return
    end

    if target < 0 or not pcall(sim.getObjectPosition, target, robot) then
        target = selectTarget()
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
    updateRoute(distance)
    if routeComplete then
        target = findTarget()
        rel = sim.getObjectPosition(target, robot)
        dx = rel[1]
        dy = rel[2]
        distance = math.sqrt(dx * dx + dy * dy)
    elseif #route > 0 then
        target = route[routeIndex].handle
        targetAlias = route[routeIndex].alias
        rel = sim.getObjectPosition(target, robot)
        dx = rel[1]
        dy = rel[2]
        distance = math.sqrt(dx * dx + dy * dy)
    end

    local heading = atan2(dy, dx)
    local obstacleSteer, obstacleSlow, minObstacleDistance, hardStop, closestSide, obstacleRisk =
        readObstacleField()

    local isFinalTarget = (#route == 0) or routeComplete or (routeIndex >= #route)
    local standOff = isFinalTarget and cfg.followDistance or 0.06
    local distanceError = distance - standOff

    if isFinalTarget and (distance <= cfg.arrivalTolerance or distanceError <= 0.02) then
        setWheelSpeeds(0, 0)
        publishTelemetry('ARRIVED', distance, minObstacleDistance, obstacleRisk)
        logState('ARRIVED', distance, minObstacleDistance, obstacleRisk)
        return
    end

    local state = 'ROUTE'
    if isFinalTarget then state = 'TRACKING' end
    if minObstacleDistance > 0 and minObstacleDistance < cfg.avoidRange then
        state = 'AVOIDING'
    end

    local inRecovery = updateRecovery(distance, closestSide)
    local headingAbs = math.abs(heading)
    local forwardScale = clamp(math.cos(heading), 0, 1)
    local zoneVMax = cfg.vMax * speedLimitFactor
    local v = clamp(cfg.kAttraction * math.max(distanceError, 0) * forwardScale, 0, zoneVMax)
    if headingAbs > 1.2 then
        v = math.min(v, 0.08)
    end

    local w = 0
    if hardStop or inRecovery then
        v = -0.045
        w = clamp(-sign(recoverySide) * cfg.wMax * 0.72, -cfg.wMax, cfg.wMax)
        state = 'RECOVERY'
    else
        local tangentialEscape = 0
        if obstacleRisk > 0.18 then
            tangentialEscape = sign(heading) * 0.18 * obstacleRisk
        end
        v = v * (1 - 0.58 * obstacleSlow)
        v = math.min(v, zoneVMax)
        w = clamp(cfg.kHeading * heading + obstacleSteer + tangentialEscape, -cfg.wMax, cfg.wMax)
    end

    if tableContains({'ROUTE', 'TRACKING', 'AVOIDING', 'RECOVERY'}, state) then
        setWheelSpeeds(v, w)
    else
        setWheelSpeeds(0, 0)
    end
    publishTelemetry(state, distance, minObstacleDistance, obstacleRisk)
    logState(state, distance, minObstacleDistance, obstacleRisk)
end

function sysCall_cleanup()
    if leftMotor >= 0 and rightMotor >= 0 then
        setWheelSpeedsRaw(0, 0)
    end
    publishTelemetry('STOPPED', -1, -1, 0)
end
