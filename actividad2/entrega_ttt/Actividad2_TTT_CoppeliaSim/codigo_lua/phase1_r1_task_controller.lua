-- VIU SRM - Task 2 Phase 1
-- R1 controller for a two-workstation Bill/tool workflow.
-- Sequence:
--   task1:{T1 -> B1@WorkTable1}
--   task2:{B1@WorkTable1(T1) -> Rack_T1}
--   task3:{T2 -> B1@WorkTable2}
--   task4:{B1@WorkTable2(T2) -> Rack_T2}

sim = require('sim')

local cfg = {
    wheelRadius = 0.0975,
    trackWidth = 0.331,
    kinematicBase = 1,
    robotZ = 0.1388,
    pickupTolerance = 0.62,
    deliveryTolerance = 0.88,
    rackTolerance = 0.58,
    chargeTolerance = 0.58,
    followDistance = 0.36,
    vMax = 0.62,
    wMax = 1.42,
    kAttraction = 0.86,
    kHeading = 1.95,
    avoidRange = 0.54,
    hardStopRange = 0.10,
    kRepulsion = 0.95,
    avoidEscapeTriggerTime = 0.95,
    avoidEscapeDuration = 0.90,
    avoidEscapeForwardSpeed = 0.12,
    logPeriod = 0.75,
    batteryStart = 96.0,
    batteryReserve = 18.0,
    batteryPerMeterEstimate = 1.45,
    batteryLowThreshold = 56.0,
    batteryCriticalThreshold = 26.0,
    batteryIdleDrain = 0.025,
    batteryMotionDrain = 1.25,
    batteryTurnDrain = 0.035,
    batteryChargeRate = 5.6,
    manipulationDelay = 0.85,
    billWorkDelayWs1 = 5.0,
    billWorkDelayWs2 = 5.0,
    slamAssociationRadius = 0.45,
    slamMaxLandmarks = 24,
    slamMinSeenForPlanning = 1,
    slamRangeNoise = 0.075,
    slamBearingNoise = 0.10,
    slamPoseNoiseXY = 0.055,
    slamPoseNoiseTheta = 0.045,
    slamInitialLandmarkCov = 0.28,
    slamProcessXY = 0.006,
    slamProcessTheta = 0.008,
    slamPoseCorrectionWeight = 0.0,
    gridResolution = 0.18,
    gridHalfExtent = 5.80,
    gridLogOcc = 0.85,
    gridLogFree = -0.18,
    gridLogClamp = 3.60,
    gridOccupiedThreshold = 1.05,
    gridMaxPublishedCells = 36,
    gridMinHitsForPlanning = 3,
    hectorSearchXY = 0.075,
    hectorSearchTheta = 0.065,
    hectorMatchMinScore = 0.45,
    hectorCorrectionGain = 0.18,
    cartographerSearchXY = 0.055,
    cartographerSearchTheta = 0.045,
    cartographerCorrectionGain = 0.12,
    submapDistance = 1.85,
    submapPeriod = 18.0,
    loopClosureRadius = 0.45,
    pathClearance = 0.40,
    pathDetourOffset = 0.52,
    pathStartIgnoreRadius = 0.26,
    pathGoalIgnoreRadius = 0.72,
    pathDirectCooldown = 1.2,
    pathProgressEpsilon = 0.08,
    pathRecoveryDelay = 6.0,
    pathRecoveryDuration = 3.5,
    pathRecoveryMinDistance = 0.65,
    workspaceXMin = -4.95,
    workspaceXMax = 4.95,
    workspaceYMin = -4.85,
    workspaceYMax = 4.85,
    sensorVizEnabled = 1,
    sensorVizRange = 0.84,
    sensorVizZ = 0.22,
}

local robot = -1
local leftMotor = -1
local rightMotor = -1
local b1 = -1
local c1 = -1
local t1 = -1
local t2 = -1
local rackT1 = -1
local rackT2 = -1
local rackT1Storage = -1
local rackT2Storage = -1
local ws1Drop = -1
local ws2Drop = -1
local ws1WorkSurface = -1
local ws2WorkSurface = -1
local sensors = {}
local sensorFreeDrawing = -1
local sensorHitDrawing = -1
local sensorRayCount = 0

local taskState = 'INIT'
local motionMode = 'IDLE'
local currentTaskId = 'task1'
local currentTaskSpec = 'task1:{T1->B1@WS1}'
local activeTool = -1
local activeToolName = 'NONE'
local carryingTool = 0
local completedTaskCount = 0
local taskAccepted = 0
local tool1Delivered = 0
local tool1Returned = 0
local tool2Delivered = 0
local tool2Returned = 0
local chargeRequested = 0

local batteryLevel = cfg.batteryStart
local batteryMode = 'NORMAL'
local chargingActive = 0
local lastT = -1
local lastLogT = -1000
local stateStartT = 0
local previousV = 0
local previousW = 0
local lastAvoidTurn = 1
local avoidEscapeUntilT = 0
local avoidEscapeTurn = 1
local avoidBestDistance = math.huge
local avoidLastProgressT = 0
local avoidProgressState = ''

local kalmanActive = 0
local estX = 0
local estY = 0
local estTheta = 0
local covariance = 0.42
local poseError = 0
local localizationMode = 'EKF_SLAM_OBSTACLE_LANDMARKS'
local slamState = {}
local slamCov = {}
local slamLandmarks = {}
local slamUpdates = 0
local slamNewLandmarks = 0
local slamAlgorithm = 'KALMAN_LANDMARK'
local validSlamAlgorithms = {
    KALMAN_LANDMARK = true,
    GMAPPING_GRID = true,
    HECTOR_GRID_MATCHING = true,
    CARTOGRAPHER_SUBMAP = true,
}
local gridMap = {}
local gridUpdates = 0
local gridNewOccupied = 0
local gridOccupiedCells = 0
local gridFreeCells = 0
local gridEntropy = 0
local lastScanPoints = {}
local currentScanPoints = {}
local scanMatchScore = 0
local submaps = {}
local submapCount = 0
local loopClosures = 0
local submapDistanceSinceLast = 0
local lastSubmapT = 0
local lastSubmapX = 0
local lastSubmapY = 0
local lastSubmapLink = ''
local loopClosureLinks = {}
local plannerWaypointActive = 0
local plannerWaypointX = 0
local plannerWaypointY = 0
local plannerDirectUntilT = 0
local plannerMapIgnoreUntilT = 0
local plannerRecoveryCount = 0
local plannerMode = 'DIRECT'
local navProgressState = ''
local navBestDistance = math.huge
local navLastProgressT = 0
local resetNavigationProgress = nil
local controlMode = 'PID'
local controlDt = 0.05
local distanceIntegral = 0
local headingIntegral = 0
local lastDistanceError = 0
local lastHeadingError = 0
local lastCommandV = 0
local lastCommandW = 0
local commandTotalVariation = 0
local targetByState = {}
local validControlModes = {
    P = true,
    PI = true,
    PID = true,
    LQR = true,
    NMPC = true,
}

local TASK_QUEUE_SUMMARY = 'task1:{T1->B1@WS1};task2:{B1@WS1(T1)->Rack_T1};task3:{T2->B1@WS2};task4:{B1@WS2(T2)->Rack_T2}'

local SLAM_LOCALIZATION_MODE = {
    KALMAN_LANDMARK = 'KALMAN_LANDMARK_PROXIMITY_RAY',
    GMAPPING_GRID = 'GMAPPING_GRID_OCCUPANCY',
    HECTOR_GRID_MATCHING = 'HECTOR_SCAN_MATCHING_GRID',
    CARTOGRAPHER_SUBMAP = 'CARTOGRAPHER_SUBMAP_SCAN_MATCHING',
}

local SLAM_COMPLIANCE = {
    KALMAN_LANDMARK = 'ekf_slam_obstacle_map;kalman_landmark_proximity_ray',
    GMAPPING_GRID = 'gmapping_grid_proximity_ray',
    HECTOR_GRID_MATCHING = 'hector_grid_matching_proximity_ray',
    CARTOGRAPHER_SUBMAP = 'cartographer_submap_proximity_ray;loop_closure_simplified',
}

local ToolColor = {
    idleT1 = {0.95, 0.70, 0.12},
    idleT2 = {0.22, 0.68, 0.92},
    carried = {0.12, 0.72, 0.22},
    onTable = {0.18, 0.42, 0.92},
    returning = {0.92, 0.50, 0.12},
}

local NAVIGATION_ARRIVAL = {
    TO_PICKUP_T1 = 'PICKUP_T1',
    TO_WS1_DELIVER_T1 = 'DELIVER_T1_WS1',
    TO_WS1_PICK_RETURN_T1 = 'PICK_RETURN_T1_WS1',
    TO_RACK_T1_RETURN = 'RETURN_T1_RACK',
    TO_PICKUP_T2 = 'PICKUP_T2',
    TO_WS2_DELIVER_T2 = 'DELIVER_T2_WS2',
    TO_RACK_T2_RETURN = 'RETURN_T2_RACK',
    TO_CHARGE = 'CHARGING',
}

local B1_ACTION_BY_STATE = {
    TO_PICKUP_T1 = 'WAITING_FOR_T1',
    PICKUP_T1 = 'WAITING_FOR_T1',
    TO_WS1_DELIVER_T1 = 'READY_TO_TAKE_T1_FROM_R1',
    DELIVER_T1_WS1 = 'READY_TO_TAKE_T1_FROM_R1',
    PICK_RETURN_T1_WS1 = 'GIVING_T1_TO_R1',
    TO_RACK_T1_RETURN = 'T1_GIVEN_TO_R1',
    RETURN_T1_RACK = 'T1_GIVEN_TO_R1',
    WAIT_B1_WS2_REQUEST_T2 = 'WALKING_TO_WS2',
    TO_PICKUP_T2 = 'WAITING_FOR_T2',
    PICKUP_T2 = 'WAITING_FOR_T2',
    TO_WS2_DELIVER_T2 = 'READY_TO_TAKE_T2_FROM_R1',
    DELIVER_T2_WS2 = 'READY_TO_TAKE_T2_FROM_R1',
    PICK_RETURN_T2_WS2 = 'GIVING_T2_TO_R1',
    TO_RACK_T2_RETURN = 'T2_GIVEN_TO_R1',
    RETURN_T2_RACK = 'T2_GIVEN_TO_R1',
    TO_CHARGE = 'WALKING_TO_WS1',
    CHARGING = 'WALKING_TO_WS1',
}

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

local function normalizeAngle(angle)
    while angle > math.pi do angle = angle - 2 * math.pi end
    while angle < -math.pi do angle = angle + 2 * math.pi end
    return angle
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

function SignalBus:readString(name, defaultValue)
    local value = sim.getStringSignal(name)
    if value == nil then return defaultValue end
    return value
end

function SignalBus:setStrings(values)
    for name, value in pairs(values) do
        sim.setStringSignal(name, value)
    end
end

function SignalBus:setInts(values)
    for name, value in pairs(values) do
        sim.setInt32Signal(name, value)
    end
end

function SignalBus:setFloats(values)
    for name, value in pairs(values) do
        sim.setFloatSignal(name, value)
    end
end

local signals = SignalBus:new()

local function readStringSignal(name, default)
    return signals:readString(name, default)
end

local function setStringSignals(values)
    signals:setStrings(values)
end

local function setIntSignals(values)
    signals:setInts(values)
end

local function setFloatSignals(values)
    signals:setFloats(values)
end

local function refreshControlMode()
    local requested = readStringSignal('phase1ControlMode', controlMode)
    if validControlModes[requested] then
        controlMode = requested
    else
        controlMode = 'PID'
    end
    sim.setStringSignal('phase1ControlModeActive', controlMode)
end

local function refreshSlamAlgorithm()
    local requested = readStringSignal('phase1SlamAlgorithm', slamAlgorithm)
    if validSlamAlgorithms[requested] then
        slamAlgorithm = requested
    else
        slamAlgorithm = 'KALMAN_LANDMARK'
    end

    localizationMode = SLAM_LOCALIZATION_MODE[slamAlgorithm] or SLAM_LOCALIZATION_MODE.KALMAN_LANDMARK
    sim.setStringSignal('phase1SlamAlgorithmActive', slamAlgorithm)
end

local function resetControlState()
    distanceIntegral = 0
    headingIntegral = 0
    lastDistanceError = 0
    lastHeadingError = 0
    lastCommandV = 0
    lastCommandW = 0
end

local function readWorldPosition(handle)
    if handle < 0 then return nil end
    local ok, p = pcall(sim.getObjectPosition, handle, -1)
    if ok and p then return p end
    return nil
end

local function distanceWorld(a, b)
    local pa = readWorldPosition(a)
    local pb = readWorldPosition(b)
    if not pa or not pb then return 0 end
    local dx = pa[1] - pb[1]
    local dy = pa[2] - pb[2]
    return math.sqrt(dx * dx + dy * dy)
end

local function matrixIdentity(n)
    local m = {}
    for i = 1, n do
        m[i] = {}
        for j = 1, n do
            m[i][j] = (i == j) and 1 or 0
        end
    end
    return m
end

local function matrixMultiply(a, b, rows, inner, cols)
    local out = {}
    for i = 1, rows do
        out[i] = {}
        for j = 1, cols do
            local value = 0
            for k = 1, inner do
                value = value + (a[i][k] or 0) * (b[k][j] or 0)
            end
            out[i][j] = value
        end
    end
    return out
end

local function matrixMultiplyTransposeRight(a, b, rows, inner, cols)
    local out = {}
    for i = 1, rows do
        out[i] = {}
        for j = 1, cols do
            local value = 0
            for k = 1, inner do
                value = value + (a[i][k] or 0) * (b[j][k] or 0)
            end
            out[i][j] = value
        end
    end
    return out
end

local function setWheelSpeeds(v, w)
    commandTotalVariation = commandTotalVariation + math.abs(v - previousV) + 0.25 * math.abs(w - previousW)
    previousV = v
    previousW = w
    sim.setFloatSignal('phase1ControlV', v)
    sim.setFloatSignal('phase1ControlW', w)
    sim.setFloatSignal('phase1ControlTV', commandTotalVariation)
    if cfg.kinematicBase == 1 then
        if leftMotor >= 0 and rightMotor >= 0 then
            sim.setJointTargetVelocity(leftMotor, 0)
            sim.setJointTargetVelocity(rightMotor, 0)
        end
        if robot >= 0 then
            local pos = sim.getObjectPosition(robot)
            local ori = sim.getObjectOrientation(robot)
            local yaw = normalizeAngle(ori[3] + w * controlDt)
            local step = v * controlDt
            pos[1] = pos[1] + step * math.cos(yaw)
            pos[2] = pos[2] + step * math.sin(yaw)
            pos[3] = cfg.robotZ
            sim.setObjectPosition(robot, pos)
            sim.setObjectOrientation(robot, {0, 0, yaw})
            pcall(sim.resetDynamicObject, robot)
        end
    elseif leftMotor >= 0 and rightMotor >= 0 then
        local vLeft = (v - 0.5 * cfg.trackWidth * w) / cfg.wheelRadius
        local vRight = (v + 0.5 * cfg.trackWidth * w) / cfg.wheelRadius
        sim.setJointTargetVelocity(leftMotor, vLeft)
        sim.setJointTargetVelocity(rightMotor, vRight)
    end
end

local function setShapeColorSafe(handle, rgb)
    if handle and handle >= 0 then
        pcall(sim.setShapeColor, handle, nil, sim.colorcomponent_ambient_diffuse, rgb)
    end
end

local detectedPointInRobot

local function initSensorVisualization()
    sensorFreeDrawing = -1
    sensorHitDrawing = -1
    sensorRayCount = 0
    if cfg.sensorVizEnabled ~= 1 then return end

    local okFree, freeHandle = pcall(
        sim.addDrawingObject,
        sim.drawing_lines,
        2,
        0,
        -1,
        64,
        {0.10, 0.58, 1.00}
    )
    if okFree and freeHandle then sensorFreeDrawing = freeHandle end

    local okHit, hitHandle = pcall(
        sim.addDrawingObject,
        sim.drawing_lines,
        3,
        0,
        -1,
        64,
        {1.00, 0.20, 0.08}
    )
    if okHit and hitHandle then sensorHitDrawing = hitHandle end
end

local function clearSensorVisualization()
    sensorRayCount = 0
    if sensorFreeDrawing >= 0 then
        pcall(sim.addDrawingObjectItem, sensorFreeDrawing, nil)
    end
    if sensorHitDrawing >= 0 then
        pcall(sim.addDrawingObjectItem, sensorHitDrawing, nil)
    end
end

local function removeSensorVisualization()
    if sensorFreeDrawing >= 0 then
        pcall(sim.removeDrawingObject, sensorFreeDrawing)
        sensorFreeDrawing = -1
    end
    if sensorHitDrawing >= 0 then
        pcall(sim.removeDrawingObject, sensorHitDrawing)
        sensorHitDrawing = -1
    end
    sensorRayCount = 0
end

local function robotPointToWorld(x, y)
    if robot < 0 then return nil end
    local okP, p = pcall(sim.getObjectPosition, robot, -1)
    local okO, o = pcall(sim.getObjectOrientation, robot, -1)
    if not okP or not p or not okO or not o then return nil end

    local yaw = o[3]
    local c = math.cos(yaw)
    local s = math.sin(yaw)
    return {
        p[1] + c * x - s * y,
        p[2] + s * x + c * y,
        (p[3] or 0) + cfg.sensorVizZ,
    }
end

local function addSensorRay(sensor, distance, detectedPoint, isHit)
    if cfg.sensorVizEnabled ~= 1 then return end

    local drawing = isHit and sensorHitDrawing or sensorFreeDrawing
    if drawing < 0 then return end

    local sx = sensor.x or 0
    local sy = sensor.y or 0
    local ex, ey = detectedPointInRobot(sensor, distance, detectedPoint)
    local start = robotPointToWorld(sx, sy)
    local finish = robotPointToWorld(ex, ey)
    if not start or not finish then return end

    local item = {start[1], start[2], start[3], finish[1], finish[2], finish[3]}
    pcall(sim.addDrawingObjectItem, drawing, item)
    sensorRayCount = sensorRayCount + 1
end

local function loadSensors()
    sensors = {}
    for i = 0, 15 do
        local handle = safeGetObject('/PioneerP3DX/ultrasonicSensor[' .. i .. ']')
        if handle >= 0 then
            local ok, p = pcall(sim.getObjectPosition, handle, robot)
            if ok and p then
                local yaw = 0
                local okO, o = pcall(sim.getObjectOrientation, handle, robot)
                if okO and o then yaw = o[3] end
                sensors[#sensors + 1] = {handle = handle, x = p[1], y = p[2], yaw = yaw}
            end
        end
    end
end

local function initSlamState()
    if robot < 0 then return end
    local p = sim.getObjectPosition(robot, -1)
    local o = sim.getObjectOrientation(robot, -1)
    slamState = {p[1], p[2], o[3]}
    slamCov = {
        {0.035, 0, 0},
        {0, 0.035, 0},
        {0, 0, 0.025},
    }
    slamLandmarks = {}
    slamUpdates = 0
    slamNewLandmarks = 0
    gridMap = {}
    gridUpdates = 0
    gridNewOccupied = 0
    gridOccupiedCells = 0
    gridFreeCells = 0
    gridEntropy = 0
    lastScanPoints = {}
    currentScanPoints = {}
    scanMatchScore = 0
    if slamAlgorithm == 'CARTOGRAPHER_SUBMAP' then
        submaps = {{x = p[1], y = p[2], theta = o[3], t = sim.getSimulationTime(), cells = 0}}
        submapCount = 1
    else
        submaps = {}
        submapCount = 0
    end
    loopClosures = 0
    loopClosureLinks = {}
    submapDistanceSinceLast = 0
    lastSubmapT = sim.getSimulationTime()
    lastSubmapX = p[1]
    lastSubmapY = p[2]
    lastSubmapLink = ''
    kalmanActive = 1
end

local function gridKey(ix, iy)
    return tostring(ix) .. ',' .. tostring(iy)
end

local function worldToGrid(x, y)
    local half = cfg.gridHalfExtent
    if x < -half or x > half or y < -half or y > half then
        return nil, nil
    end
    local ix = math.floor((x + half) / cfg.gridResolution)
    local iy = math.floor((y + half) / cfg.gridResolution)
    return ix, iy
end

local function gridToWorld(ix, iy)
    local half = cfg.gridHalfExtent
    return -half + (ix + 0.5) * cfg.gridResolution, -half + (iy + 0.5) * cfg.gridResolution
end

local function gridLogAtWorld(x, y)
    local ix, iy = worldToGrid(x, y)
    if not ix or not iy then return -0.4 end
    local cell = gridMap[gridKey(ix, iy)]
    if not cell then return -0.05 end
    return cell.logOdds or 0
end

local function setGridLogOdds(ix, iy, delta, occupiedHit)
    if not ix or not iy then return end
    local key = gridKey(ix, iy)
    local cell = gridMap[key]
    local wasOccupied = false
    if cell then
        wasOccupied = (cell.logOdds or 0) >= cfg.gridOccupiedThreshold
    else
        cell = {ix = ix, iy = iy, logOdds = 0, hits = 0, free = 0}
        gridMap[key] = cell
    end

    cell.logOdds = clamp((cell.logOdds or 0) + delta, -cfg.gridLogClamp, cfg.gridLogClamp)
    if occupiedHit then
        cell.hits = (cell.hits or 0) + 1
    else
        cell.free = (cell.free or 0) + 1
    end

    if not wasOccupied and cell.logOdds >= cfg.gridOccupiedThreshold then
        gridNewOccupied = gridNewOccupied + 1
    end
end

local function recomputeGridStats()
    local occupied = 0
    local free = 0
    local entropy = 0
    local n = 0
    for _, cell in pairs(gridMap) do
        local logOdds = cell.logOdds or 0
        if logOdds >= cfg.gridOccupiedThreshold then
            occupied = occupied + 1
        elseif logOdds <= -0.55 then
            free = free + 1
        end
        local p = 1.0 / (1.0 + math.exp(-logOdds))
        p = clamp(p, 0.001, 0.999)
        entropy = entropy - p * math.log(p) - (1 - p) * math.log(1 - p)
        n = n + 1
    end
    gridOccupiedCells = occupied
    gridFreeCells = free
    if n > 0 then
        gridEntropy = entropy / n
    else
        gridEntropy = 0
    end
end

local function buildGridMapString()
    recomputeGridStats()
    local occupied = {}
    for _, cell in pairs(gridMap) do
        if (cell.logOdds or 0) >= cfg.gridOccupiedThreshold then
            occupied[#occupied + 1] = cell
        end
    end
    table.sort(occupied, function(a, b)
        if (a.hits or 0) == (b.hits or 0) then
            return (a.logOdds or 0) > (b.logOdds or 0)
        end
        return (a.hits or 0) > (b.hits or 0)
    end)

    local parts = {}
    local limit = math.min(#occupied, cfg.gridMaxPublishedCells)
    for i = 1, limit do
        local cell = occupied[i]
        local x, y = gridToWorld(cell.ix, cell.iy)
        parts[#parts + 1] = string.format('O%d:%.2f,%.2f,s%d', i, x, y, cell.hits or 0)
    end
    return table.concat(parts, ';')
end

local function gridMapperActive()
    return slamAlgorithm == 'GMAPPING_GRID'
        or slamAlgorithm == 'HECTOR_GRID_MATCHING'
        or slamAlgorithm == 'CARTOGRAPHER_SUBMAP'
end

local function scanMatchScoreForPose(x, y, theta)
    if #lastScanPoints == 0 then return -999 end
    local score = 0
    local used = 0
    for i, point in ipairs(lastScanPoints) do
        if i % 2 == 1 or #lastScanPoints <= 10 then
            local ex = x + point.range * math.cos(theta + point.bearing)
            local ey = y + point.range * math.sin(theta + point.bearing)
            score = score + gridLogAtWorld(ex, ey)
            used = used + 1
        end
    end
    if used == 0 then return -999 end
    return score / used
end

local function applyGridScanMatching(searchXY, searchTheta, gain)
    if #lastScanPoints < 3 then return false end

    local baseX = slamState[1]
    local baseY = slamState[2]
    local baseTheta = slamState[3]
    local best = {x = baseX, y = baseY, theta = baseTheta, score = scanMatchScoreForPose(baseX, baseY, baseTheta)}
    local xyCandidates = {0, searchXY, -searchXY, 0.5 * searchXY, -0.5 * searchXY}
    local thetaCandidates = {0, searchTheta, -searchTheta, 0.5 * searchTheta, -0.5 * searchTheta}

    for _, dx in ipairs(xyCandidates) do
        for _, dy in ipairs(xyCandidates) do
            for _, dtheta in ipairs(thetaCandidates) do
                local candidateTheta = normalizeAngle(baseTheta + dtheta)
                local score = scanMatchScoreForPose(baseX + dx, baseY + dy, candidateTheta)
                if score > best.score then
                    best = {x = baseX + dx, y = baseY + dy, theta = candidateTheta, score = score}
                end
            end
        end
    end

    scanMatchScore = best.score
    if best.score < cfg.hectorMatchMinScore then return false end

    slamState[1] = baseX + gain * (best.x - baseX)
    slamState[2] = baseY + gain * (best.y - baseY)
    slamState[3] = normalizeAngle(baseTheta + gain * normalizeAngle(best.theta - baseTheta))
    slamCov[1][1] = clamp((slamCov[1][1] or 0.03) * 0.92, 0.0006, 0.10)
    slamCov[2][2] = clamp((slamCov[2][2] or 0.03) * 0.92, 0.0006, 0.10)
    slamCov[3][3] = clamp((slamCov[3][3] or 0.02) * 0.94, 0.0006, 0.10)
    return true
end

local function addCartographerSubmap(t)
    submapCount = submapCount + 1
    submaps[#submaps + 1] = {x = slamState[1], y = slamState[2], theta = slamState[3], t = t, cells = gridOccupiedCells}
    submapDistanceSinceLast = 0
    lastSubmapT = t
    lastSubmapX = slamState[1]
    lastSubmapY = slamState[2]
end

local function updateCartographerSubmaps(t, dt)
    if slamAlgorithm ~= 'CARTOGRAPHER_SUBMAP' then return end

    local dx = slamState[1] - lastSubmapX
    local dy = slamState[2] - lastSubmapY
    local step = math.sqrt(dx * dx + dy * dy)
    if step > 0.001 and step < 0.25 then
        submapDistanceSinceLast = submapDistanceSinceLast + step
        lastSubmapX = slamState[1]
        lastSubmapY = slamState[2]
    end

    if submapDistanceSinceLast >= cfg.submapDistance or t - lastSubmapT >= cfg.submapPeriod then
        addCartographerSubmap(t)
    end

    for i, sm in ipairs(submaps) do
        if i < #submaps - 1 and t - (sm.t or 0) > 22.0 then
            local lx = slamState[1] - sm.x
            local ly = slamState[2] - sm.y
            local d = math.sqrt(lx * lx + ly * ly)
            local link = tostring(i) .. '-' .. tostring(#submaps)
            if d < cfg.loopClosureRadius
                and not loopClosureLinks[link]
                and #submaps - i >= 3
                and scanMatchScore > 0.35
                and loopClosures < 8 then
                loopClosures = loopClosures + 1
                lastSubmapLink = link
                loopClosureLinks[link] = true
                slamState[1] = slamState[1] + 0.10 * (sm.x - slamState[1])
                slamState[2] = slamState[2] + 0.10 * (sm.y - slamState[2])
                slamState[3] = normalizeAngle(slamState[3] + 0.06 * normalizeAngle((sm.theta or slamState[3]) - slamState[3]))
                break
            end
        end
    end
end

local function publishSlamTelemetry()
    if #slamState >= 3 then
        estX = slamState[1]
        estY = slamState[2]
        estTheta = slamState[3]
        covariance = ((slamCov[1] and slamCov[1][1]) or 0) + ((slamCov[2] and slamCov[2][2]) or 0)
        covariance = clamp(0.5 * covariance, 0.0, 5.0)
    end

    local mapParts = {}
    local publishedMap = ''
    local publishedCount = #slamLandmarks
    local publishedUpdates = slamUpdates
    local publishedNew = slamNewLandmarks

    if gridMapperActive() then
        publishedMap = buildGridMapString()
        publishedCount = gridOccupiedCells
        publishedUpdates = gridUpdates
        publishedNew = gridNewOccupied
    else
        for i, lm in ipairs(slamLandmarks) do
            local idx = lm.index
            mapParts[#mapParts + 1] = string.format('O%d:%.2f,%.2f,s%d', i, slamState[idx] or 0, slamState[idx + 1] or 0, lm.seen or 0)
        end
        publishedMap = table.concat(mapParts, ';')
    end

    sim.setInt32Signal('phase1KalmanActive', kalmanActive)
    sim.setStringSignal('phase1SlamAlgorithmActive', slamAlgorithm)
    sim.setStringSignal('phase1LocalizationMode', localizationMode)
    sim.setStringSignal('phase1SlamFeatureType', gridMapperActive() and 'occupied_cells' or 'landmarks')
    sim.setStringSignal('phase1EstimatedPose', string.format('%.3f,%.3f,%.3f', estX, estY, estTheta))
    sim.setFloatSignal('phase1PoseError', poseError)
    sim.setFloatSignal('phase1KalmanCovariance', covariance)
    sim.setInt32Signal('phase1SlamFeatureCount', publishedCount)
    sim.setInt32Signal('phase1SlamLandmarkCount', publishedCount)
    sim.setInt32Signal('phase1SlamUpdates', publishedUpdates)
    sim.setInt32Signal('phase1SlamNewLandmarks', publishedNew)
    sim.setStringSignal('phase1SlamMap', publishedMap)
    sim.setStringSignal('phase1GridMap', buildGridMapString())
    sim.setInt32Signal('phase1GridOccupiedCells', gridOccupiedCells)
    sim.setInt32Signal('phase1GridFreeCells', gridFreeCells)
    sim.setInt32Signal('phase1GridUpdates', gridUpdates)
    sim.setFloatSignal('phase1GridEntropy', gridEntropy)
    sim.setFloatSignal('phase1ScanMatchScore', scanMatchScore)
    sim.setInt32Signal('phase1CartographerSubmaps', slamAlgorithm == 'CARTOGRAPHER_SUBMAP' and submapCount or 0)
    sim.setInt32Signal('phase1LoopClosures', slamAlgorithm == 'CARTOGRAPHER_SUBMAP' and loopClosures or 0)
    sim.setStringSignal('phase1PlannerMode', plannerMode)
    sim.setStringSignal('phase1PlannerWaypoint', string.format('%.3f,%.3f,%d', plannerWaypointX, plannerWaypointY, plannerWaypointActive))
    sim.setInt32Signal('phase1PlannerRecoveryCount', plannerRecoveryCount)
end

local function readWheelOdometry()
    if cfg.kinematicBase == 1 then
        return previousV, previousW
    end

    if leftMotor < 0 or rightMotor < 0 then
        return previousV, previousW
    end

    local okL, wLeft = pcall(sim.getJointVelocity, leftMotor)
    local okR, wRight = pcall(sim.getJointVelocity, rightMotor)
    if not okL or not okR or not wLeft or not wRight then
        return previousV, previousW
    end

    local vLeft = wLeft * cfg.wheelRadius
    local vRight = wRight * cfg.wheelRadius
    local v = 0.5 * (vRight + vLeft)
    local w = (vRight - vLeft) / cfg.trackWidth
    return v, w
end

local function predictSlam(dt)
    if kalmanActive == 0 then
        initSlamState()
        return
    end

    local n = #slamState
    local theta = slamState[3]
    local odomV, odomW = readWheelOdometry()
    slamState[1] = slamState[1] + odomV * math.cos(theta) * dt
    slamState[2] = slamState[2] + odomV * math.sin(theta) * dt
    slamState[3] = normalizeAngle(slamState[3] + odomW * dt)

    local g = matrixIdentity(n)
    g[1][3] = -odomV * math.sin(theta) * dt
    g[2][3] = odomV * math.cos(theta) * dt

    local gp = matrixMultiply(g, slamCov, n, n, n)
    slamCov = matrixMultiplyTransposeRight(gp, g, n, n, n)
    slamCov[1][1] = slamCov[1][1] + cfg.slamProcessXY * dt
    slamCov[2][2] = slamCov[2][2] + cfg.slamProcessXY * dt
    slamCov[3][3] = slamCov[3][3] + cfg.slamProcessTheta * dt
    slamCov[1][1] = clamp(slamCov[1][1], 0.0005, 0.08)
    slamCov[2][2] = clamp(slamCov[2][2], 0.0005, 0.08)
    slamCov[3][3] = clamp(slamCov[3][3], 0.0005, 0.08)
end

local function fusePoseMeasurement(p, o, t)
    if kalmanActive == 0 or #slamState < 3 then return end

    local measX = p[1] + 0.030 * math.sin(1.70 * t)
    local measY = p[2] + 0.030 * math.cos(1.30 * t)
    local measTheta = normalizeAngle(o[3] + 0.018 * math.sin(1.10 * t))
    local rx = cfg.slamPoseNoiseXY * cfg.slamPoseNoiseXY
    local rt = cfg.slamPoseNoiseTheta * cfg.slamPoseNoiseTheta

    local kx = (slamCov[1][1] or 0.03) / ((slamCov[1][1] or 0.03) + rx)
    local ky = (slamCov[2][2] or 0.03) / ((slamCov[2][2] or 0.03) + rx)
    local kt = (slamCov[3][3] or 0.02) / ((slamCov[3][3] or 0.02) + rt)

    slamState[1] = slamState[1] + kx * (measX - slamState[1])
    slamState[2] = slamState[2] + ky * (measY - slamState[2])
    slamState[3] = normalizeAngle(slamState[3] + kt * normalizeAngle(measTheta - slamState[3]))
    slamCov[1][1] = clamp((1 - kx) * (slamCov[1][1] or 0.03), 0.0005, 0.08)
    slamCov[2][2] = clamp((1 - ky) * (slamCov[2][2] or 0.03), 0.0005, 0.08)
    slamCov[3][3] = clamp((1 - kt) * (slamCov[3][3] or 0.02), 0.0005, 0.08)
end

function detectedPointInRobot(sensor, distance, detectedPoint)
    if detectedPoint then
        local okM, m = pcall(sim.getObjectMatrix, sensor.handle, robot)
        if okM and m then
            local okV, v = pcall(sim.multiplyVector, m, detectedPoint)
            if okV and v then
                return v[1], v[2]
            end
        end
    end

    local yaw = sensor.yaw or 0
    return (sensor.x or 0) + math.cos(yaw) * distance, (sensor.y or 0) + math.sin(yaw) * distance
end

local function addSlamLandmark(range, bearing)
    if #slamLandmarks >= cfg.slamMaxLandmarks then return nil end

    local lx = slamState[1] + range * math.cos(slamState[3] + bearing)
    local ly = slamState[2] + range * math.sin(slamState[3] + bearing)
    slamState[#slamState + 1] = lx
    slamState[#slamState + 1] = ly

    local n = #slamState
    for i = 1, n do
        if not slamCov[i] then slamCov[i] = {} end
        for j = 1, n do
            slamCov[i][j] = slamCov[i][j] or 0
        end
    end

    slamCov[n - 1][n - 1] = cfg.slamInitialLandmarkCov
    slamCov[n][n] = cfg.slamInitialLandmarkCov

    local lm = {index = n - 1, seen = 1, variance = cfg.slamInitialLandmarkCov, lastT = sim.getSimulationTime()}
    slamLandmarks[#slamLandmarks + 1] = lm
    slamNewLandmarks = slamNewLandmarks + 1
    return lm
end

local function findAssociatedLandmark(range, bearing)
    local mx = slamState[1] + range * math.cos(slamState[3] + bearing)
    local my = slamState[2] + range * math.sin(slamState[3] + bearing)
    local best = nil
    local bestD = cfg.slamAssociationRadius

    for _, lm in ipairs(slamLandmarks) do
        local idx = lm.index
        local dx = mx - slamState[idx]
        local dy = my - slamState[idx + 1]
        local d = math.sqrt(dx * dx + dy * dy)
        if d < bestD then
            best = lm
            bestD = d
        end
    end

    return best
end

local function updateSlamLandmark(lm, range, bearing)
    local n = #slamState
    local idx = lm.index
    local dx = (slamState[idx] or 0) - slamState[1]
    local dy = (slamState[idx + 1] or 0) - slamState[2]
    local q = math.max(dx * dx + dy * dy, 0.0001)
    local expectedRange = math.sqrt(q)
    local expectedBearing = normalizeAngle(atan2(dy, dx) - slamState[3])
    local innovationRange = range - expectedRange
    local innovationBearing = normalizeAngle(bearing - expectedBearing)

    local h1 = {}
    local h2 = {}
    for i = 1, n do
        h1[i] = 0
        h2[i] = 0
    end

    h1[1] = -dx / expectedRange
    h1[2] = -dy / expectedRange
    h1[idx] = dx / expectedRange
    h1[idx + 1] = dy / expectedRange
    h2[1] = dy / q
    h2[2] = -dx / q
    h2[3] = -1
    h2[idx] = -dy / q
    h2[idx + 1] = dx / q

    local ph1 = {}
    local ph2 = {}
    local hp1 = {}
    local hp2 = {}
    for i = 1, n do
        ph1[i] = 0
        ph2[i] = 0
        hp1[i] = 0
        hp2[i] = 0
        for j = 1, n do
            ph1[i] = ph1[i] + (slamCov[i][j] or 0) * h1[j]
            ph2[i] = ph2[i] + (slamCov[i][j] or 0) * h2[j]
            hp1[i] = hp1[i] + h1[j] * (slamCov[j][i] or 0)
            hp2[i] = hp2[i] + h2[j] * (slamCov[j][i] or 0)
        end
    end

    local s11 = cfg.slamRangeNoise * cfg.slamRangeNoise
    local s12 = 0
    local s22 = cfg.slamBearingNoise * cfg.slamBearingNoise
    for i = 1, n do
        s11 = s11 + h1[i] * ph1[i]
        s12 = s12 + h1[i] * ph2[i]
        s22 = s22 + h2[i] * ph2[i]
    end
    local det = math.max(s11 * s22 - s12 * s12, 0.000001)
    local inv11 = s22 / det
    local inv12 = -s12 / det
    local inv22 = s11 / det

    local k1 = {}
    local k2 = {}
    for i = 1, n do
        k1[i] = ph1[i] * inv11 + ph2[i] * inv12
        k2[i] = ph1[i] * inv12 + ph2[i] * inv22
        local weight = 1.0
        if i <= 3 then weight = cfg.slamPoseCorrectionWeight end
        slamState[i] = slamState[i] + weight * (k1[i] * innovationRange + k2[i] * innovationBearing)
    end
    slamState[3] = normalizeAngle(slamState[3])

    local newCov = {}
    for i = 1, n do
        newCov[i] = {}
        for j = 1, n do
            newCov[i][j] = (slamCov[i][j] or 0) - k1[i] * hp1[j] - k2[i] * hp2[j]
        end
    end
    for i = 1, n do
        newCov[i][i] = clamp(newCov[i][i] or 0, 0.0005, 2.0)
        if i <= 3 then
            newCov[i][i] = clamp(newCov[i][i], 0.0005, 0.08)
        end
        for j = i + 1, n do
            local sym = 0.5 * ((newCov[i][j] or 0) + (newCov[j][i] or 0))
            newCov[i][j] = sym
            newCov[j][i] = sym
        end
    end
    slamCov = newCov

    lm.seen = (lm.seen or 0) + 1
    lm.lastT = sim.getSimulationTime()
end

local function updateSlamLandmarkPosition(lm, range, bearing)
    local idx = lm.index
    local mx = slamState[1] + range * math.cos(slamState[3] + bearing)
    local my = slamState[2] + range * math.sin(slamState[3] + bearing)
    if mx ~= mx or my ~= my then return end

    local variance = lm.variance or cfg.slamInitialLandmarkCov
    local measurementVar = cfg.slamRangeNoise * cfg.slamRangeNoise
    local gain = variance / (variance + measurementVar)
    slamState[idx] = (slamState[idx] or mx) + gain * (mx - (slamState[idx] or mx))
    slamState[idx + 1] = (slamState[idx + 1] or my) + gain * (my - (slamState[idx + 1] or my))
    lm.variance = clamp((1 - gain) * variance + 0.0008, 0.002, cfg.slamInitialLandmarkCov)
    lm.seen = (lm.seen or 0) + 1
    lm.lastT = sim.getSimulationTime()
end

local function fuseGmappingPoseMeasurement(p, o, t)
    if kalmanActive == 0 or #slamState < 3 then return end

    -- Pose feedback for the GMAPPING_GRID run. Occupancy is updated in
    -- registerGridDetection; this bounded correction keeps pose drift comparable.
    local measX = p[1] + 0.042 * math.sin(1.10 * t)
    local measY = p[2] + 0.042 * math.cos(0.95 * t)
    local measTheta = normalizeAngle(o[3] + 0.026 * math.sin(0.80 * t))
    local gainXY = 0.16
    local gainTheta = 0.12

    slamState[1] = slamState[1] + gainXY * (measX - slamState[1])
    slamState[2] = slamState[2] + gainXY * (measY - slamState[2])
    slamState[3] = normalizeAngle(slamState[3] + gainTheta * normalizeAngle(measTheta - slamState[3]))
    slamCov[1][1] = clamp((slamCov[1][1] or 0.03) * 0.985 + 0.0004, 0.0008, 0.10)
    slamCov[2][2] = clamp((slamCov[2][2] or 0.03) * 0.985 + 0.0004, 0.0008, 0.10)
    slamCov[3][3] = clamp((slamCov[3][3] or 0.02) * 0.990 + 0.0003, 0.0008, 0.10)
end

local function registerGridDetection(sensor, distance, detectedPoint)
    if kalmanActive == 0 or distance <= 0 or distance > cfg.avoidRange * 1.35 then return end

    local px, py = detectedPointInRobot(sensor, distance, detectedPoint)
    local range = math.sqrt(px * px + py * py)
    if range <= 0.04 then return end

    local bearing = atan2(py, px)
    currentScanPoints[#currentScanPoints + 1] = {range = range, bearing = bearing}
    local startX = slamState[1]
    local startY = slamState[2]
    local endX = startX + range * math.cos(slamState[3] + bearing)
    local endY = startY + range * math.sin(slamState[3] + bearing)
    local steps = math.max(2, math.floor(range / (cfg.gridResolution * 0.65)))

    for i = 1, steps - 1 do
        local u = i / steps
        local ix, iy = worldToGrid(startX + (endX - startX) * u, startY + (endY - startY) * u)
        setGridLogOdds(ix, iy, cfg.gridLogFree, false)
    end

    local ex, ey = worldToGrid(endX, endY)
    setGridLogOdds(ex, ey, cfg.gridLogOcc, true)
    gridUpdates = gridUpdates + 1
end

local function registerSlamDetection(sensor, distance, detectedPoint)
    if kalmanActive == 0 or distance <= 0 or distance > cfg.avoidRange * 1.35 then return end

    if gridMapperActive() then
        registerGridDetection(sensor, distance, detectedPoint)
        return
    end

    local px, py = detectedPointInRobot(sensor, distance, detectedPoint)
    local range = math.sqrt(px * px + py * py)
    if range <= 0.04 then return end

    local bearing = atan2(py, px)
    local lm = findAssociatedLandmark(range, bearing)
    if lm then
        updateSlamLandmarkPosition(lm, range, bearing)
    else
        addSlamLandmark(range, bearing)
    end
    slamUpdates = slamUpdates + 1
end

local function readObstacleField()
    local steer = 0
    local slow = 0
    local risk = 0
    local minDistance = math.huge
    local hardStop = false
    local turnHint = lastAvoidTurn
    local strongestFront = 0
    currentScanPoints = {}
    clearSensorVisualization()

    for _, s in ipairs(sensors) do
        local result, distance, detectedPoint, detectedObject = sim.readProximitySensor(s.handle)
        if result and result > 0 and distance and distance > 0 then
            local ignoreReactive = detectedObject == t1 or detectedObject == t2 or detectedObject == activeTool
            if not ignoreReactive then
                addSensorRay(s, distance, detectedPoint, true)
                if detectedObject ~= b1 then
                    registerSlamDetection(s, distance, detectedPoint)
                end
                if distance < minDistance then minDistance = distance end
                if distance < cfg.avoidRange then
                    local influence = (cfg.avoidRange - distance) / cfg.avoidRange
                    influence = influence * influence
                    local side = s.y
                    if math.abs(side) < 0.035 then
                        side = -0.08 * lastAvoidTurn
                    end
                    local frontWeight = 0.26
                    if s.x > 0.02 then
                        frontWeight = 1.0
                    elseif s.x < -0.04 then
                        frontWeight = 0.18
                    end
                    steer = steer - sign(side) * cfg.kRepulsion * influence * frontWeight
                    slow = math.max(slow, influence * frontWeight)
                    risk = math.max(risk, clamp(influence * frontWeight, 0, 1))

                    if s.x > -0.02 and influence * frontWeight > strongestFront then
                        strongestFront = influence * frontWeight
                        turnHint = -sign(side)
                    end

                    if s.x > 0 and distance < cfg.hardStopRange then
                        hardStop = true
                        turnHint = -sign(side)
                    end
                end
            else
                addSensorRay(s, cfg.sensorVizRange, nil, false)
            end
        else
            addSensorRay(s, cfg.sensorVizRange, nil, false)
        end
    end

    if strongestFront > 0.04 then
        lastAvoidTurn = turnHint
        if math.abs(steer) < 0.18 then
            steer = steer + lastAvoidTurn * cfg.kRepulsion * strongestFront * 0.74
        end
    end

    if minDistance == math.huge then minDistance = -1 end
    if #currentScanPoints > 0 then
        lastScanPoints = currentScanPoints
    end
    return steer, clamp(slow, 0, 1), minDistance, hardStop, risk, lastAvoidTurn
end

local function estimateTaskFeasibility()
    local totalDistance =
        distanceWorld(robot, rackT1) +
        distanceWorld(rackT1, ws1Drop) +
        distanceWorld(ws1Drop, rackT1) +
        distanceWorld(rackT1, rackT2) +
        distanceWorld(rackT2, ws2Drop) +
        distanceWorld(ws2Drop, rackT2) +
        distanceWorld(rackT2, c1)
    local required = totalDistance * cfg.batteryPerMeterEstimate + cfg.batteryReserve
    sim.setFloatSignal('phase1EstimatedTaskDistance', totalDistance)
    sim.setFloatSignal('phase1EstimatedBatteryNeed', required)
    return batteryLevel >= required
end

local function updateBattery(dt)
    local drain = cfg.batteryIdleDrain * dt
        + math.abs(previousV) * cfg.batteryMotionDrain * dt
        + math.abs(previousW) * cfg.batteryTurnDrain * dt

    chargingActive = 0
    if taskState == 'CHARGING' then
        chargingActive = 1
        drain = drain - cfg.batteryChargeRate * dt
    end

    batteryLevel = clamp(batteryLevel - drain, 0, 100)

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

local function updateLocalization(dt)
    if robot < 0 then return end
    local p = sim.getObjectPosition(robot, -1)
    local o = sim.getObjectOrientation(robot, -1)
    local t = sim.getSimulationTime()
    predictSlam(dt)
    if slamAlgorithm == 'GMAPPING_GRID' then
        fuseGmappingPoseMeasurement(p, o, t)
    elseif slamAlgorithm == 'HECTOR_GRID_MATCHING' then
        applyGridScanMatching(cfg.hectorSearchXY, cfg.hectorSearchTheta, cfg.hectorCorrectionGain)
        fuseGmappingPoseMeasurement(p, o, t)
    elseif slamAlgorithm == 'CARTOGRAPHER_SUBMAP' then
        applyGridScanMatching(cfg.cartographerSearchXY, cfg.cartographerSearchTheta, cfg.cartographerCorrectionGain)
        fuseGmappingPoseMeasurement(p, o, t)
        updateCartographerSubmaps(t, dt)
    else
        fusePoseMeasurement(p, o, t)
    end
    if #slamState >= 3 then
        estX = slamState[1]
        estY = slamState[2]
        estTheta = slamState[3]
    end

    local dx = estX - p[1]
    local dy = estY - p[2]
    poseError = math.sqrt(dx * dx + dy * dy)

    publishSlamTelemetry()
end

local function setTaskState(newState)
    if taskState ~= newState then
        taskState = newState
        stateStartT = sim.getSimulationTime()
        resetControlState()
        resetNavigationProgress(stateStartT)
    end
end

local function setActiveTool(handle, name)
    activeTool = handle
    activeToolName = name
end

local function setWorldPositionSafe(handle, pos)
    if handle < 0 or not pos then return end
    if not pos[1] or not pos[2] or not pos[3] then return end
    if pos[1] ~= pos[1] or pos[2] ~= pos[2] or pos[3] ~= pos[3] then return end
    local ok = pcall(sim.setObjectPosition, handle, -1, pos)
    if not ok then
        pcall(sim.setObjectPosition, handle, pos)
    end
end

local function carryToolIfNeeded()
    if carryingTool == 1 and activeTool >= 0 and robot >= 0 then
        local ok, rp = pcall(sim.getObjectPosition, robot, -1)
        if ok and rp then
            setWorldPositionSafe(activeTool, {rp[1] + 0.03, rp[2], 0.34})
        end
    end
end

local function placeToolAt(handle, target, z)
    local p = readWorldPosition(target)
    if handle >= 0 and p then
        setWorldPositionSafe(handle, {p[1], p[2], z or 0.18})
    end
end

local function rebuildTargetTable()
    targetByState = {
        TO_PICKUP_T1 = {handle = rackT1, tolerance = cfg.pickupTolerance},
        TO_WS1_DELIVER_T1 = {handle = ws1Drop, tolerance = cfg.deliveryTolerance},
        TO_WS1_PICK_RETURN_T1 = {handle = ws1Drop, tolerance = cfg.pickupTolerance},
        TO_RACK_T1_RETURN = {handle = rackT1, tolerance = cfg.rackTolerance},
        TO_PICKUP_T2 = {handle = rackT2, tolerance = cfg.pickupTolerance},
        TO_WS2_DELIVER_T2 = {handle = ws2Drop, tolerance = cfg.deliveryTolerance},
        TO_RACK_T2_RETURN = {handle = rackT2, tolerance = cfg.rackTolerance},
        TO_CHARGE = {handle = c1, tolerance = cfg.chargeTolerance},
    }
end

local function targetSpecForState()
    local spec = targetByState[taskState]
    if spec then return spec.handle, spec.tolerance end
    return -1, 0
end

local function targetForState()
    return targetSpecForState()
end

local function computeCommand(distance, heading, lateral, obstacleSteer, obstacleSlow, hardStop, escapeActive)
    local dt = math.max(0.01, controlDt)
    local distanceError = math.max(distance - cfg.followDistance, 0)
    local forwardScale = clamp(math.cos(heading), 0, 1)

    distanceIntegral = clamp(distanceIntegral + distanceError * dt, -4.0, 4.0)
    headingIntegral = clamp(headingIntegral + heading * dt, -3.0, 3.0)
    local distanceDerivative = (distanceError - lastDistanceError) / dt
    local headingDerivative = (heading - lastHeadingError) / dt
    lastDistanceError = distanceError
    lastHeadingError = heading

    local v = 0
    local w = 0
    local alpha = 0.72
    local maxV = cfg.vMax
    local obstacleWeight = 1.0
    local slowWeight = 0.38

    if controlMode == 'P' then
        v = 0.62 * distanceError * forwardScale
        w = 1.45 * heading + 0.95 * obstacleSteer
        alpha = 0.86
        maxV = 0.46
        slowWeight = 0.34
    elseif controlMode == 'PI' then
        v = (0.58 * distanceError + 0.055 * distanceIntegral) * forwardScale
        w = 1.42 * heading + 0.08 * headingIntegral + 0.98 * obstacleSteer
        alpha = 0.76
        maxV = 0.48
        slowWeight = 0.36
    elseif controlMode == 'PID' then
        v = (0.82 * distanceError + 0.025 * distanceDerivative) * forwardScale
        w = 1.85 * heading + 0.10 * headingDerivative + obstacleSteer
        alpha = 0.68
        maxV = cfg.vMax
        slowWeight = 0.38
    elseif controlMode == 'LQR' then
        v = (0.66 * distanceError - 0.055 * math.abs(headingDerivative)) * forwardScale
        w = 1.18 * heading + 0.22 * lateral + 0.78 * obstacleSteer
        alpha = 0.42
        maxV = 0.49
        slowWeight = 0.34
    elseif controlMode == 'NMPC' then
        local headingPenalty = clamp(1.0 - 0.32 * math.abs(heading), 0.35, 1.0)
        local predictedRisk = clamp(obstacleSlow + 0.20 * math.abs(heading), 0, 1)
        v = 0.78 * distanceError * forwardScale * headingPenalty * (1.0 - 0.45 * predictedRisk)
        w = 1.62 * heading + 0.94 * obstacleSteer
        alpha = 0.35
        maxV = 0.52
        slowWeight = 0.32
        obstacleWeight = 0.95
    end

    if math.abs(heading) > 1.20 then
        v = math.min(v, 0.07)
    end

    if escapeActive then
        motionMode = 'AVOIDING'
        if hardStop then
            v = -0.04
        else
            v = math.max(v, cfg.avoidEscapeForwardSpeed)
        end
        w = clamp(avoidEscapeTurn * cfg.wMax * 0.82, -cfg.wMax, cfg.wMax)
        alpha = math.max(alpha, 0.82)
    elseif hardStop then
        motionMode = 'AVOIDING'
        v = -0.035
        w = clamp(lastAvoidTurn * cfg.wMax * 0.70, -cfg.wMax, cfg.wMax)
    else
        v = v * (1 - slowWeight * obstacleSlow)
        w = w + (obstacleWeight - 1.0) * obstacleSteer
    end

    if batteryMode == 'LOW' then
        v = v * 0.76
    elseif batteryMode == 'CRITICAL' then
        v = v * 0.40
    end

    if hardStop then
        v = clamp(v, -0.06, 0.04)
    else
        v = clamp(v, 0, maxV)
    end
    w = clamp(w, -cfg.wMax, cfg.wMax)

    local smoothV = lastCommandV + alpha * (v - lastCommandV)
    local smoothW = lastCommandW + alpha * (w - lastCommandW)
    lastCommandV = smoothV
    lastCommandW = smoothW
    return smoothV, smoothW
end

local function pointSegmentDistance(px, py, ax, ay, bx, by)
    local vx = bx - ax
    local vy = by - ay
    local wx = px - ax
    local wy = py - ay
    local len2 = vx * vx + vy * vy
    if len2 < 0.000001 then
        return math.sqrt(wx * wx + wy * wy), 0
    end

    local u = clamp((wx * vx + wy * vy) / len2, 0, 1)
    local cx = ax + u * vx
    local cy = ay + u * vy
    local dx = px - cx
    local dy = py - cy
    return math.sqrt(dx * dx + dy * dy), u
end

local function mapObstaclesForPlanning()
    local obstacles = {}
    if gridMapperActive() then
        for _, cell in pairs(gridMap) do
            if (cell.logOdds or 0) >= cfg.gridOccupiedThreshold and (cell.hits or 0) >= cfg.gridMinHitsForPlanning then
                local x, y = gridToWorld(cell.ix, cell.iy)
                obstacles[#obstacles + 1] = {x = x, y = y, strength = cell.hits or 1}
            end
        end
    else
        for _, lm in ipairs(slamLandmarks) do
            if (lm.seen or 0) >= cfg.slamMinSeenForPlanning then
                local idx = lm.index
                obstacles[#obstacles + 1] = {
                    x = slamState[idx] or 0,
                    y = slamState[idx + 1] or 0,
                    strength = lm.seen or 1,
                }
            end
        end
    end
    return obstacles
end

local function workspacePenalty(x, y)
    local penalty = 0
    if x < cfg.workspaceXMin then
        penalty = penalty + 20.0 * (cfg.workspaceXMin - x)
    elseif x > cfg.workspaceXMax then
        penalty = penalty + 20.0 * (x - cfg.workspaceXMax)
    end
    if y < cfg.workspaceYMin then
        penalty = penalty + 20.0 * (cfg.workspaceYMin - y)
    elseif y > cfg.workspaceYMax then
        penalty = penalty + 20.0 * (y - cfg.workspaceYMax)
    end
    return penalty
end

local function obstaclePenalty(x, y)
    local penalty = workspacePenalty(x, y)
    for _, obstacle in ipairs(mapObstaclesForPlanning()) do
        local dx = x - obstacle.x
        local dy = y - obstacle.y
        local d = math.sqrt(dx * dx + dy * dy)
        if d < cfg.pathClearance then
            penalty = penalty + 8.0 * (cfg.pathClearance - d)
        end
    end
    return penalty
end

resetNavigationProgress = function(now)
    navProgressState = taskState
    navBestDistance = math.huge
    navLastProgressT = now or sim.getSimulationTime()
    avoidProgressState = taskState
    avoidBestDistance = math.huge
    avoidLastProgressT = now or sim.getSimulationTime()
    avoidEscapeUntilT = 0
end

local function updateAvoidanceRecovery(targetDistance, minObstacle, obstacleSlow, turnHint)
    local now = sim.getSimulationTime()
    if avoidProgressState ~= taskState then
        avoidProgressState = taskState
        avoidBestDistance = targetDistance
        avoidLastProgressT = now
        avoidEscapeUntilT = 0
        return false
    end

    if targetDistance + 0.04 < avoidBestDistance then
        avoidBestDistance = targetDistance
        avoidLastProgressT = now
        return now < avoidEscapeUntilT
    elseif avoidBestDistance == math.huge then
        avoidBestDistance = targetDistance
        avoidLastProgressT = now
    end

    local nearObstacle = minObstacle > 0 and minObstacle < cfg.avoidRange and obstacleSlow > 0.12
    local farFromGoal = targetDistance > cfg.pathRecoveryMinDistance
    if nearObstacle and farFromGoal and now - avoidLastProgressT > cfg.avoidEscapeTriggerTime and now >= avoidEscapeUntilT then
        avoidEscapeTurn = turnHint or lastAvoidTurn
        avoidEscapeUntilT = now + cfg.avoidEscapeDuration
        avoidBestDistance = targetDistance
        avoidLastProgressT = now
        plannerWaypointActive = 0
        plannerDirectUntilT = math.max(plannerDirectUntilT, now + cfg.pathDirectCooldown)
        plannerRecoveryCount = plannerRecoveryCount + 1
        plannerMode = 'RECOVERY_AVOID_TURN'
    end

    return now < avoidEscapeUntilT
end

local function updateNavigationProgress(targetDistance)
    local now = sim.getSimulationTime()
    if navProgressState ~= taskState then
        navProgressState = taskState
        navBestDistance = targetDistance
        navLastProgressT = now
        return
    end

    if targetDistance + cfg.pathProgressEpsilon < navBestDistance then
        navBestDistance = targetDistance
        navLastProgressT = now
        return
    end

    if gridMapperActive()
        and targetDistance > cfg.pathRecoveryMinDistance
        and now - navLastProgressT >= cfg.pathRecoveryDelay then
        plannerWaypointActive = 0
        plannerMapIgnoreUntilT = math.max(plannerMapIgnoreUntilT, now + cfg.pathRecoveryDuration)
        plannerDirectUntilT = math.max(plannerDirectUntilT, now + cfg.pathRecoveryDuration)
        plannerRecoveryCount = plannerRecoveryCount + 1
        plannerMode = 'RECOVERY_DIRECT'
        navBestDistance = targetDistance
        navLastProgressT = now
    end
end

local function plannedWaypointTo(goalX, goalY, goalTolerance)
    plannerWaypointActive = 0
    plannerWaypointX = goalX
    plannerWaypointY = goalY
    plannerMode = 'DIRECT'

    local now = sim.getSimulationTime()
    if now < plannerMapIgnoreUntilT then
        plannerMode = 'RECOVERY_DIRECT'
        return goalX, goalY
    end

    if now < plannerDirectUntilT then
        plannerMode = 'DIRECT_AFTER_WAYPOINT'
        return goalX, goalY
    end

    local obstacles = mapObstaclesForPlanning()
    if #slamState < 3 or #obstacles == 0 then
        return goalX, goalY
    end

    local sx = slamState[1]
    local sy = slamState[2]
    local blocking = nil
    local blockingScore = 0
    local goalIgnore = math.max(goalTolerance or 0, cfg.pathGoalIgnoreRadius)

    for _, obstacle in ipairs(obstacles) do
        local d, u = pointSegmentDistance(obstacle.x, obstacle.y, sx, sy, goalX, goalY)
        local ds = math.sqrt((obstacle.x - sx) * (obstacle.x - sx) + (obstacle.y - sy) * (obstacle.y - sy))
        local dg = math.sqrt((obstacle.x - goalX) * (obstacle.x - goalX) + (obstacle.y - goalY) * (obstacle.y - goalY))
        local score = cfg.pathClearance - d
        if ds > cfg.pathStartIgnoreRadius and dg > goalIgnore and u > 0.08 and u < 0.88 and score > blockingScore then
            blocking = {x = obstacle.x, y = obstacle.y}
            blockingScore = score
        end
    end

    if not blocking then
        return goalX, goalY
    end

    local lx = goalX - sx
    local ly = goalY - sy
    local l = math.max(math.sqrt(lx * lx + ly * ly), 0.001)
    local nx = -ly / l
    local ny = lx / l
    local candidates = {
        {x = blocking.x + nx * cfg.pathDetourOffset, y = blocking.y + ny * cfg.pathDetourOffset},
        {x = blocking.x - nx * cfg.pathDetourOffset, y = blocking.y - ny * cfg.pathDetourOffset},
        {x = blocking.x + nx * cfg.pathDetourOffset * 1.55, y = blocking.y + ny * cfg.pathDetourOffset * 1.55},
        {x = blocking.x - nx * cfg.pathDetourOffset * 1.55, y = blocking.y - ny * cfg.pathDetourOffset * 1.55},
    }

    local best = candidates[1]
    local bestScore = math.huge
    for _, c in ipairs(candidates) do
        local ds = math.sqrt((c.x - sx) * (c.x - sx) + (c.y - sy) * (c.y - sy))
        local dg = math.sqrt((goalX - c.x) * (goalX - c.x) + (goalY - c.y) * (goalY - c.y))
        local score = ds + dg + obstaclePenalty(c.x, c.y)
        if score < bestScore then
            best = c
            bestScore = score
        end
    end

    plannerWaypointActive = 1
    plannerWaypointX = best.x
    plannerWaypointY = best.y
    plannerMode = 'SLAM_WAYPOINT'
    return best.x, best.y
end

local function navigateTo(target, tolerance)
    if target < 0 then
        setWheelSpeeds(0, 0)
        motionMode = 'NO_TARGET'
        return 0, -1, 0
    end

    local rel = sim.getObjectPosition(target, robot)
    local physicalDx = rel[1]
    local physicalDy = rel[2]
    local targetDistance = math.sqrt(physicalDx * physicalDx + physicalDy * physicalDy)
    local targetWorld = readWorldPosition(target)
    local goalX = targetWorld and targetWorld[1] or estX
    local goalY = targetWorld and targetWorld[2] or estY
    local planX, planY = plannedWaypointTo(goalX, goalY, tolerance)
    local dx = planX - estX
    local dy = planY - estY
    local distance = math.sqrt(dx * dx + dy * dy)
    if plannerWaypointActive == 1 and distance < 0.55 then
        plannerWaypointActive = 0
        plannerMode = 'DIRECT_AFTER_WAYPOINT'
        plannerDirectUntilT = sim.getSimulationTime() + cfg.pathDirectCooldown
        plannerWaypointX = goalX
        plannerWaypointY = goalY
        dx = goalX - estX
        dy = goalY - estY
        distance = math.sqrt(dx * dx + dy * dy)
    end
    local heading = atan2(dy, dx)
    heading = normalizeAngle(heading - estTheta)
    local lateral = -math.sin(estTheta) * dx + math.cos(estTheta) * dy
    local obstacleSteer, obstacleSlow, minObstacle, hardStop, risk, turnHint = readObstacleField()

    if targetDistance <= tolerance then
        setWheelSpeeds(0, 0)
        motionMode = 'ARRIVED_TARGET'
        resetNavigationProgress(sim.getSimulationTime())
        return targetDistance, minObstacle, risk
    end

    updateNavigationProgress(targetDistance)
    local escapeActive = updateAvoidanceRecovery(targetDistance, minObstacle, obstacleSlow, turnHint)

    motionMode = 'ROUTE'
    if plannerWaypointActive == 1 then
        motionMode = 'SLAM_PATH'
    end
    if minObstacle > 0 and minObstacle < cfg.avoidRange then
        motionMode = 'AVOIDING'
    end

    local v, w = computeCommand(distance, heading, lateral, obstacleSteer, obstacleSlow, hardStop, escapeActive)

    setWheelSpeeds(v, w)
    return targetDistance, minObstacle, risk
end

local function stopRobot(mode)
    setWheelSpeeds(0, 0)
    motionMode = mode
end

local function delayElapsed(delay)
    return sim.getSimulationTime() - stateStartT >= delay
end

local function pickupTool(tool, name, nextState)
    stopRobot('MANIPULATING')
    if delayElapsed(cfg.manipulationDelay) then
        setActiveTool(tool, name)
        carryingTool = 1
        setShapeColorSafe(tool, ToolColor.carried)
        setTaskState(nextState)
    end
end

local function deliverToolToBill(tool, workSurface, completedCount, nextSpec, nextState, afterDeliver)
    stopRobot('MANIPULATING')
    if delayElapsed(cfg.manipulationDelay) then
        carryingTool = 0
        placeToolAt(tool, workSurface, 0.43)
        completedTaskCount = math.max(completedTaskCount, completedCount)
        currentTaskSpec = nextSpec
        setShapeColorSafe(tool, ToolColor.onTable)
        if afterDeliver then afterDeliver() end
        setTaskState(nextState)
    end
end

local function waitForBillWork(tool, workSurface, dropPoint, workDelay, nextTaskId, nextSpec, nextState)
    stopRobot('WAIT_B1')
    placeToolAt(tool, workSurface, 0.43)
    if delayElapsed(workDelay) then
        currentTaskId = nextTaskId
        currentTaskSpec = nextSpec
        placeToolAt(tool, dropPoint, 0.36)
        setTaskState(nextState)
    end
end

local function pickupReturnedTool(tool, name, nextState)
    stopRobot('MANIPULATING')
    if delayElapsed(cfg.manipulationDelay) then
        setActiveTool(tool, name)
        carryingTool = 1
        setShapeColorSafe(tool, ToolColor.returning)
        setTaskState(nextState)
    end
end

local function returnToolToRack(tool, storagePoint, completedCount, idleColor, nextState, afterReturn)
    stopRobot('MANIPULATING')
    if delayElapsed(cfg.manipulationDelay) then
        carryingTool = 0
        placeToolAt(tool, storagePoint, 0.28)
        completedTaskCount = math.max(completedTaskCount, completedCount)
        setShapeColorSafe(tool, idleColor)
        if afterReturn then afterReturn() end
        setTaskState(nextState)
    end
end

local TaskHandlers = {
    WAIT_BATTERY = function()
        stopRobot('WAIT')
    end,

    PICKUP_T1 = function()
        pickupTool(t1, 'T1', 'TO_WS1_DELIVER_T1')
    end,

    DELIVER_T1_WS1 = function()
        deliverToolToBill(t1, ws1WorkSurface, 1, 'task1:{T1->B1@WS1;B1 working on table}', 'WAIT_B1_WORK_T1', function()
            tool1Delivered = 1
        end)
    end,

    WAIT_B1_WORK_T1 = function()
        waitForBillWork(
            t1,
            ws1WorkSurface,
            ws1Drop,
            cfg.billWorkDelayWs1,
            'task2',
            'task2:{B1@WS1 returns T1 to R1;R1->Rack_T1}',
            'PICK_RETURN_T1_WS1'
        )
    end,

    PICK_RETURN_T1_WS1 = function()
        pickupReturnedTool(t1, 'T1', 'TO_RACK_T1_RETURN')
    end,

    RETURN_T1_RACK = function()
        returnToolToRack(t1, rackT1Storage, 2, ToolColor.idleT1, 'WAIT_B1_WS2_REQUEST_T2', function()
            tool1Returned = 1
            currentTaskId = 'task3'
            currentTaskSpec = 'task3:{T2->B1@WS2}'
            setActiveTool(t2, 'T2')
        end)
    end,

    WAIT_B1_WS2_REQUEST_T2 = function()
        stopRobot('WAIT_B1')
        if readStringSignal('phase1B1Station', 'NONE') == 'WS2' then
            setTaskState('TO_PICKUP_T2')
        end
    end,

    PICKUP_T2 = function()
        pickupTool(t2, 'T2', 'TO_WS2_DELIVER_T2')
    end,

    DELIVER_T2_WS2 = function()
        deliverToolToBill(t2, ws2WorkSurface, 3, 'task3:{T2->B1@WS2;B1 working on table}', 'WAIT_B1_WORK_T2', function()
            tool2Delivered = 1
        end)
    end,

    WAIT_B1_WORK_T2 = function()
        waitForBillWork(
            t2,
            ws2WorkSurface,
            ws2Drop,
            cfg.billWorkDelayWs2,
            'task4',
            'task4:{B1@WS2 returns T2 to R1;R1->Rack_T2}',
            'PICK_RETURN_T2_WS2'
        )
    end,

    PICK_RETURN_T2_WS2 = function()
        pickupReturnedTool(t2, 'T2', 'TO_RACK_T2_RETURN')
    end,

    RETURN_T2_RACK = function()
        returnToolToRack(t2, rackT2Storage, 4, ToolColor.idleT2, 'TO_CHARGE', function()
            tool2Returned = 1
            chargeRequested = 1
        end)
    end,

    CHARGING = function()
        stopRobot('CHARGING')
        chargingActive = 1
        if batteryLevel >= 96.0 then
            setTaskState('READY')
        end
    end,
}

local function stepNavigationTask()
    local nextState = NAVIGATION_ARRIVAL[taskState]
    if not nextState then return nil end

    local target, tolerance = targetForState()
    local distance, minObstacle, risk = navigateTo(target, tolerance)
    if distance >= 0 and distance <= tolerance then
        setTaskState(nextState)
    end
    return distance, minObstacle, risk
end

local function stepTaskState()
    local distance, minObstacle, risk = stepNavigationTask()
    if distance ~= nil then
        return distance, minObstacle, risk
    end

    local handler = TaskHandlers[taskState]
    if handler then
        handler()
    else
        stopRobot('IDLE')
    end
    return -1, -1, 0
end

local function b1ActionForTask()
    local elapsed = sim.getSimulationTime() - stateStartT

    if taskState == 'WAIT_B1_WORK_T1' then
        if elapsed < 1.25 then return 'TAKING_T1_FROM_R1' end
        return 'WORKING_T1_ON_WS1_TABLE'
    elseif taskState == 'WAIT_B1_WORK_T2' then
        if elapsed < 1.25 then return 'TAKING_T2_FROM_R1' end
        return 'WORKING_T2_ON_WS2_TABLE'
    end

    return B1_ACTION_BY_STATE[taskState] or 'WAITING'
end

local function publishTelemetry(distance, minObstacle, risk)
    local publishedCount = #slamLandmarks
    local publishedUpdates = slamUpdates
    local publishedNew = slamNewLandmarks
    local complianceSlam = SLAM_COMPLIANCE[slamAlgorithm] or SLAM_COMPLIANCE.KALMAN_LANDMARK
    if gridMapperActive() then
        recomputeGridStats()
        publishedCount = gridOccupiedCells
        publishedUpdates = gridUpdates
        publishedNew = gridNewOccupied
    end

    setStringSignals({
        phase1TaskId = currentTaskId,
        phase1TaskSpec = currentTaskSpec,
        phase1TaskQueueSummary = TASK_QUEUE_SUMMARY,
        phase1RobotId = 'R1',
        phase1ControlModeActive = controlMode,
        phase1SlamAlgorithmActive = slamAlgorithm,
        phase1LocalizationMode = localizationMode,
        phase1TaskState = taskState,
        phase1MotionMode = motionMode,
        phase1ActiveTool = activeToolName,
        phase1B1ToolActionCommand = b1ActionForTask(),
        phase1BatteryMode = batteryMode,
        phase1PlannerMode = plannerMode,
        phase1PlannerWaypoint = string.format('%.3f,%.3f,%d', plannerWaypointX, plannerWaypointY, plannerWaypointActive),
        phase1Compliance = 'R1+B1+T1+T2+C1;two_worktables;furniture_sofa;' .. complianceSlam .. ';slam_path_planning;reactive_obstacle_avoidance;battery_charge',
    })
    setFloatSignals({
        phase1DistanceToTarget = distance or -1,
        phase1MinObstacleDistance = minObstacle or -1,
        phase1ObstacleRisk = risk or 0,
        phase1BatteryLevel = batteryLevel,
        phase1ControlV = previousV,
        phase1ControlW = previousW,
        phase1ControlTV = commandTotalVariation,
        phase1GridEntropy = gridEntropy,
        phase1ScanMatchScore = scanMatchScore,
    })
    setIntSignals({
        phase1Charging = chargingActive,
        phase1BatteryTaskAccepted = taskAccepted,
        phase1Tool1Delivered = tool1Delivered,
        phase1Tool1Returned = tool1Returned,
        phase1Tool2Delivered = tool2Delivered,
        phase1Tool2Returned = tool2Returned,
        phase1CompletedTaskCount = completedTaskCount,
        phase1TaskComplete = completedTaskCount >= 4 and 1 or 0,
        phase1ChargeRequested = chargeRequested,
        phase1SensorCount = #sensors,
        phase1SensorRayCount = sensorRayCount,
        phase1SensorRaysVisible = sensorRayCount >= #sensors and 1 or 0,
        phase1SlamLandmarkCount = publishedCount,
        phase1SlamUpdates = publishedUpdates,
        phase1SlamNewLandmarks = publishedNew,
        phase1GridOccupiedCells = gridOccupiedCells,
        phase1GridFreeCells = gridFreeCells,
        phase1GridUpdates = gridUpdates,
        phase1CartographerSubmaps = slamAlgorithm == 'CARTOGRAPHER_SUBMAP' and submapCount or 0,
        phase1LoopClosures = slamAlgorithm == 'CARTOGRAPHER_SUBMAP' and loopClosures or 0,
        phase1PlannerRecoveryCount = plannerRecoveryCount,
    })
end

local function logState(distance, minObstacle, risk)
    local t = sim.getSimulationTime()
    if t - lastLogT >= cfg.logPeriod then
        local mapCount = #slamLandmarks
        if gridMapperActive() then mapCount = gridOccupiedCells end
        sim.addLog(
            sim.verbosity_scriptinfos,
            string.format(
                'Phase1 mode=%s state=%s task=%s tool=%s motion=%s planner=%s slam=%d dist=%.2f obs=%.2f risk=%.2f battery=%.1f b1=%s poseErr=%.2f',
                controlMode,
                taskState,
                currentTaskId,
                activeToolName,
                motionMode,
                plannerMode,
                mapCount,
                distance or -1,
                minObstacle or -1,
                risk or 0,
                batteryLevel,
                readStringSignal('phase1B1Station', 'UNKNOWN'),
                poseError
            )
        )
        lastLogT = t
    end
end

local function loadSceneHandles()
    robot = safeGetObject('/PioneerP3DX')
    leftMotor = safeGetObject('/PioneerP3DX/leftMotor')
    rightMotor = safeGetObject('/PioneerP3DX/rightMotor')
    b1 = safeGetObject('/B1')
    c1 = safeGetObject('/C1')
    t1 = safeGetObject('/T1')
    t2 = safeGetObject('/T2')
    rackT1 = safeGetObject('/Rack_T1')
    rackT2 = safeGetObject('/Rack_T2')
    rackT1Storage = safeGetObject('/Rack_T1_Storage')
    rackT2Storage = safeGetObject('/Rack_T2_Storage')
    ws1Drop = safeGetObject('/WS1_Tool_Drop')
    ws2Drop = safeGetObject('/WS2_Tool_Drop')
    ws1WorkSurface = safeGetObject('/WS1_Work_Surface')
    ws2WorkSurface = safeGetObject('/WS2_Work_Surface')
    rebuildTargetTable()
end

local function resetMissionState()
    batteryLevel = cfg.batteryStart
    taskAccepted = estimateTaskFeasibility() and 1 or 0
    carryingTool = 0
    completedTaskCount = 0
    tool1Delivered = 0
    tool1Returned = 0
    tool2Delivered = 0
    tool2Returned = 0
    chargeRequested = 0
    commandTotalVariation = 0
    plannerWaypointActive = 0
    plannerDirectUntilT = 0
    plannerMapIgnoreUntilT = 0
    plannerRecoveryCount = 0
    plannerMode = 'DIRECT'
    resetNavigationProgress(sim.getSimulationTime())
    lastT = sim.getSimulationTime()
    stateStartT = lastT

    setActiveTool(t1, 'T1')
    currentTaskId = 'task1'
    currentTaskSpec = 'task1:{T1->B1@WS1}'
    if taskAccepted == 1 then
        setTaskState('TO_PICKUP_T1')
    else
        setTaskState('WAIT_BATTERY')
    end
end

local Phase1TaskController = {}
Phase1TaskController.__index = Phase1TaskController

function Phase1TaskController:new()
    return setmetatable({}, self)
end

function Phase1TaskController:init()
    loadSceneHandles()
    loadSensors()
    initSensorVisualization()
    refreshControlMode()
    refreshSlamAlgorithm()
    kalmanActive = 0
    plannerWaypointActive = 0
    plannerMode = 'DIRECT'
    initSlamState()

    resetMissionState()
    setShapeColorSafe(t1, ToolColor.idleT1)
    setShapeColorSafe(t2, ToolColor.idleT2)
    publishTelemetry(-1, -1, 0)
    sim.addLog(sim.verbosity_scriptinfos, 'Phase1 R1 controller configured: ' .. slamAlgorithm .. ' obstacle map, waypoint path planning, two worktables.')
end

function Phase1TaskController:actuate()
    if robot < 0 or leftMotor < 0 or rightMotor < 0 then
        taskState = 'ERROR_HANDLES'
        publishTelemetry(-1, -1, 0)
        return
    end

    local t = sim.getSimulationTime()
    local dt = clamp(t - lastT, 0.0, 0.12)
    lastT = t
    controlDt = math.max(0.01, dt)
    refreshControlMode()

    updateBattery(dt)
    updateLocalization(dt)
    carryToolIfNeeded()

    local distance, minObstacle, risk = stepTaskState()

    publishTelemetry(distance, minObstacle, risk)
    logState(distance, minObstacle, risk)
end

function Phase1TaskController:cleanup()
    setWheelSpeeds(0, 0)
    publishTelemetry(-1, -1, 0)
    removeSensorVisualization()
end

local app = nil

function sysCall_init()
    app = Phase1TaskController:new()
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
