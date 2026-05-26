-- VIU SRM - Task 2 Phase 1
-- B1 walking manager. Bill moves between two worktables and exposes simple
-- semantic signals so R1 can coordinate handoffs.

sim = require('sim')

local cfg = {
    speed = 0.110,
    z = 0.0,
    workPauseWs1 = 12.0,
    workPauseWs2 = 18.0,
    logPeriod = 1.5,
}

local routeWs1ToWs2 = {
    {x = -2.12, y = 1.10},
    {x = -1.50, y = 1.10},
    {x = -1.50, y = -1.60},
    {x = -0.40, y = -1.60},
    {x = 0.80, y = -1.60},
    {x = 2.12, y = -1.10},
}

local routeWs2ToWs1 = {
    {x = 2.12, y = -1.10},
    {x = 1.50, y = -1.10},
    {x = 1.50, y = 1.10},
    {x = 0.70, y = 1.10},
    {x = -0.70, y = 1.10},
    {x = -2.12, y = 1.10},
}

local Stations = {
    WS1 = {
        state = 'WORKING_WS1',
        station = 'WS1',
        tableName = 'WORKTABLE_1',
        requestTool = 'T1',
        pose = {x = -2.12, y = 1.10},
        tablePose = {x = -2.12, y = 1.76},
        pause = cfg.workPauseWs1,
        returnedSignal = 'phase1Tool1Returned',
        walkAction = 'WALKING_TO_WS2',
        transitState = 'TRANSIT_TO_WS2',
        route = routeWs1ToWs2,
    },
    WS2 = {
        state = 'WORKING_WS2',
        station = 'WS2',
        tableName = 'WORKTABLE_2',
        requestTool = 'T2',
        pose = {x = 2.12, y = -1.10},
        tablePose = {x = 2.12, y = -1.76},
        pause = cfg.workPauseWs2,
        returnedSignal = 'phase1Tool2Returned',
        walkAction = 'WALKING_TO_WS1',
        transitState = 'TRANSIT_TO_WS1',
        route = routeWs2ToWs1,
    },
}

local StationByState = {
    WORKING_WS1 = Stations.WS1,
    WORKING_WS2 = Stations.WS2,
}

local ArrivalByTransitState = {
    TRANSIT_TO_WS2 = Stations.WS2,
    TRANSIT_TO_WS1 = Stations.WS1,
}

local b1 = -1
local joints = {}
local state = Stations.WS1.state
local route = {}
local routeIndex = 1
local segmentU = 0
local walkPhase = 0
local lastT = -1
local stateStartT = 0
local movedDistance = 0
local lastPosition = nil
local currentAction = 'WAITING_FOR_T1'
local lastLogT = -1000

local function clamp(value, lo, hi)
    if value < lo then return lo end
    if value > hi then return hi end
    return value
end

local function atan2(y, x)
    if math.atan2 then return math.atan2(y, x) end
    return math.atan(y, x)
end

local function distance2d(a, b)
    local dx = b.x - a.x
    local dy = b.y - a.y
    return math.sqrt(dx * dx + dy * dy)
end

local function yawForBillFront(dx, dy)
    return atan2(dy, dx)
end

local function yawToFacePoint(fromPoint, toPoint)
    return yawForBillFront(toPoint.x - fromPoint.x, toPoint.y - fromPoint.y)
end

local function safeGetObject(path)
    local ok, handle = pcall(sim.getObject, path)
    if ok and handle and handle >= 0 then return handle end
    return -1
end

local function readIntSignal(name, default)
    local value = sim.getInt32Signal(name)
    if value == nil then return default end
    return value
end

local function readStringSignal(name, default)
    local value = sim.getStringSignal(name)
    if value == nil then return default end
    return value
end

local function setStringSignals(values)
    for name, value in pairs(values) do
        sim.setStringSignal(name, value)
    end
end

local function setIntSignals(values)
    for name, value in pairs(values) do
        sim.setInt32Signal(name, value)
    end
end

local function setFloatSignals(values)
    for name, value in pairs(values) do
        sim.setFloatSignal(name, value)
    end
end

local function registerJoint(key, path)
    local handle = safeGetObject(path)
    if handle >= 0 then joints[key] = handle end
end

local function setJointTarget(key, target)
    local handle = joints[key]
    if handle then sim.setJointTargetPosition(handle, target) end
end

local function setJointTargets(targets)
    for key, value in pairs(targets) do
        setJointTarget(key, value)
    end
end

local function setB1Pose(x, y, yaw)
    if b1 >= 0 then
        sim.setObjectPosition(b1, {x, y, cfg.z})
        sim.setObjectOrientation(b1, {0, 0, yaw})
    end

    if lastPosition then
        local dx = x - lastPosition[1]
        local dy = y - lastPosition[2]
        movedDistance = movedDistance + math.sqrt(dx * dx + dy * dy)
    end
    lastPosition = {x, y}
end

local function setBillAtStation(station)
    setB1Pose(
        station.pose.x,
        station.pose.y,
        yawToFacePoint(station.pose, station.tablePose)
    )
end

local function actionContains(text)
    return string.find(currentAction, text, 1, true) ~= nil
end

local function publish(speed)
    local p = {0, 0, 0}
    if b1 >= 0 then p = sim.getObjectPosition(b1, -1) end

    local station = 'TRANSIT'
    local tableName = 'NONE'
    local requestTool = 'NONE'
    local atWs1 = 0
    local atWs2 = 0

    local stationInfo = StationByState[state]
    if stationInfo then
        station = stationInfo.station
        tableName = stationInfo.tableName
        requestTool = stationInfo.requestTool
        atWs1 = stationInfo == Stations.WS1 and 1 or 0
        atWs2 = stationInfo == Stations.WS2 and 1 or 0
    elseif ArrivalByTransitState[state] then
        station = state
    end

    setStringSignals({
        phase1B1State = state,
        phase1B1Station = station,
        phase1B1WorkTable = tableName,
        phase1B1RequestTool = requestTool,
        phase1B1Action = currentAction,
    })
    setIntSignals({
        phase1B1AtWs1 = atWs1,
        phase1B1AtWs2 = atWs2,
    })
    setFloatSignals({
        phase1B1Speed = speed or 0,
        phase1B1X = p[1] or 0,
        phase1B1Y = p[2] or 0,
        phase1B1MovedDistance = movedDistance,
    })
end

local function tableWorkPose()
    local pulse = math.sin(walkPhase)
    local pose = {
        leftLeg = 0,
        rightLeg = 0,
        leftKnee = 0,
        rightKnee = 0,
        leftShoulder = 0,
        rightShoulder = 0,
    }

    if actionContains('TAKING') then
        pose.leftShoulder = 0.42 + 0.06 * pulse
        pose.rightShoulder = 0.38 - 0.05 * pulse
        pose.leftKnee = 0.04
        pose.rightKnee = 0.04
    elseif actionContains('WORKING') then
        pose.leftShoulder = 0.58 + 0.12 * pulse
        pose.rightShoulder = 0.54 - 0.10 * pulse
        pose.leftKnee = 0.07 + 0.03 * math.abs(pulse)
        pose.rightKnee = pose.leftKnee
    elseif actionContains('GIVING') then
        pose.leftShoulder = 0.40 + 0.04 * pulse
        pose.rightShoulder = 0.40 - 0.04 * pulse
        pose.leftKnee = 0.03
        pose.rightKnee = 0.03
    elseif StationByState[state] then
        pose.leftShoulder = 0.12
        pose.rightShoulder = 0.12
    end

    return pose
end

local function animateAtTable(dt)
    walkPhase = walkPhase + dt * 5.2
    setJointTargets(tableWorkPose())
end

local function animateWalking(dt, speed)
    if speed <= 0.001 then
        animateAtTable(dt)
        return
    end

    walkPhase = walkPhase + dt * 7.0
    local step = math.sin(walkPhase)
    setJointTargets({
        leftLeg = step * 0.30,
        rightLeg = -step * 0.30,
        leftKnee = math.max(0, step) * 0.38,
        rightKnee = math.max(0, -step) * 0.38,
        leftShoulder = math.sin(walkPhase + math.pi) * 0.18,
        rightShoulder = -math.sin(walkPhase + math.pi) * 0.18,
    })
end

local function startTransit(station)
    state = station.transitState
    route = station.route
    routeIndex = 1
    segmentU = 0
    stateStartT = sim.getSimulationTime()
    currentAction = station.walkAction
end

local function arriveFromTransit()
    local station = ArrivalByTransitState[state] or Stations.WS1
    state = station.state
    stateStartT = sim.getSimulationTime()
    setBillAtStation(station)
    return 0
end

local function updateTransit(dt)
    local a = route[routeIndex]
    local b = route[routeIndex + 1]
    if not a or not b then
        return arriveFromTransit()
    end

    local segmentLength = math.max(0.001, distance2d(a, b))
    segmentU = segmentU + cfg.speed * dt / segmentLength

    while segmentU >= 1.0 do
        segmentU = segmentU - 1.0
        routeIndex = routeIndex + 1
        a = route[routeIndex]
        b = route[routeIndex + 1]
        if not a or not b then
            return arriveFromTransit()
        end
        segmentLength = math.max(0.001, distance2d(a, b))
    end

    local dx = b.x - a.x
    local dy = b.y - a.y
    setB1Pose(a.x + dx * segmentU, a.y + dy * segmentU, yawForBillFront(dx, dy))
    return cfg.speed
end

local function updateWorkingAt(station, t)
    setBillAtStation(station)
    if t - stateStartT >= station.pause
        and readIntSignal(station.returnedSignal, 0) == 1 then
        startTransit(station)
        return cfg.speed
    end
    return 0
end

local function updateB1(dt)
    local t = sim.getSimulationTime()
    currentAction = readStringSignal('phase1B1ToolActionCommand', currentAction)

    local station = StationByState[state]
    if station then
        return updateWorkingAt(station, t)
    end

    return updateTransit(dt)
end

local function loadBillJoints()
    registerJoint('leftLeg', '/B1/leftLegJoint')
    registerJoint('rightLeg', '/B1/rightLegJoint')
    registerJoint('leftKnee', '/B1/leftKneeJoint')
    registerJoint('rightKnee', '/B1/rightKneeJoint')
    registerJoint('leftShoulder', '/B1/leftShoulderJoint')
    registerJoint('rightShoulder', '/B1/rightShoulderJoint')
end

local function resetRuntime()
    state = Stations.WS1.state
    route = {}
    routeIndex = 1
    segmentU = 0
    movedDistance = 0
    walkPhase = 0
    lastT = sim.getSimulationTime()
    stateStartT = lastT
    lastPosition = {Stations.WS1.pose.x, Stations.WS1.pose.y}
    currentAction = 'WAITING_FOR_T1'
    setBillAtStation(Stations.WS1)
end

function sysCall_init()
    b1 = safeGetObject('/B1')
    loadBillJoints()
    resetRuntime()
    publish(0)
    sim.addLog(sim.verbosity_scriptinfos, 'Phase1 B1 ready: working between WorkTable 1 and WorkTable 2.')
end

function sysCall_actuation()
    if b1 < 0 then
        publish(0)
        return
    end

    local t = sim.getSimulationTime()
    local dt = clamp(t - lastT, 0.0, 0.12)
    lastT = t

    local speed = updateB1(dt)
    animateWalking(dt, speed)
    publish(speed)

    if t - lastLogT >= cfg.logPeriod then
        sim.addLog(
            sim.verbosity_scriptinfos,
            string.format(
                'Phase1 B1 state=%s station=%s action=%s moved=%.2f m',
                state,
                sim.getStringSignal('phase1B1Station') or 'NONE',
                currentAction,
                movedDistance
            )
        )
        lastLogT = t
    end
end

function sysCall_cleanup()
    publish(0)
end
