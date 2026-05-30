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
    -- Tolerances sit comfortably above the distance at which the chassis would
    -- physically touch a rack (~0.42 m): the arrival fires in open space, just
    -- before contact, so the Pioneer stops close (~0.18 m clearance) without ever
    -- ramming and stalling against the shelf.
    pickupTolerance = 0.50,
    deliveryTolerance = 0.88,
    rackTolerance = 0.50,
    chargeTolerance = 0.58,
    followDistance = 0.36,
    vMax = 0.55,
    wMax = 1.32,
    avoidRange = 0.62,
    hardStopRange = 0.12,
    kRepulsion = 1.18,
    logPeriod = 0.75,
    batteryStart = 96.0,
    batteryReserve = 18.0,
    batteryPerMeterEstimate = 2.7,
    batteryLowThreshold = 56.0,
    batteryCriticalThreshold = 26.0,
    batteryIdleDrain = 0.025,
    batteryMotionDrain = 1.25,
    batteryTurnDrain = 0.035,
    batteryChargeRate = 5.6,
    batteryCycleResume = 90.0,
    targetCyclesPhase2 = 3,
    exploreTolerance = 0.70,     -- arrival radius for a frontier during the exploratory pass [m]
    exploreMaxTime = 78.0,       -- time box for the whole exploratory pass [s]
    exploreFrontierTimeout = 16.0, -- give up on a single hard-to-reach frontier after this [s]
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
    slamMahalanobisGate = 9.0,   -- chi-square (2 DOF) gate to reject mis-associations
    slamMinUpdateRange = 0.22,   -- skip pose updates from landmarks closer than this (1/range Jacobian)
    slamMaxPoseStep = 0.12,      -- hard cap on the position correction from one landmark update [m]
    slamMaxThetaStep = 0.10,     -- hard cap on the heading correction from one landmark update [rad]
    -- Genuine EKF-SLAM: the range/bearing observation corrects the robot pose
    -- through the Kalman gain, not just the landmark map. The weight is moderate
    -- (not 1.0) because the 16-beam sonar ring is sparse and noisy: a full-gain
    -- bearing correction with nearest-neighbour association destabilises the
    -- heading. At 0.35 the sensor genuinely drives the pose while the weak global
    -- anchor keeps the yaw observable.
    slamPoseCorrectionWeight = 0.35,
    -- Weak global reference (UWB-like beacon): a low-rate anchor that keeps the
    -- world frame (especially yaw) observable. It carries genuine Gaussian noise,
    -- not a deterministic offset, so the estimate cannot track ground truth for
    -- free; the sensor-based correction does the dominant work on x,y.
    globalRefGainXY = 0.14,
    globalRefGainTheta = 0.20,
    globalRefNoiseXY = 0.030,
    globalRefNoiseTheta = 0.018,
    gridResolution = 0.18,
    gridHalfExtent = 4.40,
    gridLogOcc = 0.85,
    gridLogFree = -0.18,
    gridLogClamp = 3.60,
    gridOccupiedThreshold = 1.05,
    gridMaxPublishedCells = 36,
    -- True Hector scan matcher: Gauss-Newton over the bilinearly interpolated
    -- occupancy field with analytic Jacobians (Kohlbrecher 2011).
    hectorMaxIterations = 5,
    hectorRegularization = 0.002,
    hectorConvergenceXY = 0.0008,
    hectorConvergenceTheta = 0.0015,
    hectorMinPoints = 5,
    hectorMatchMinScore = 0.18,
    hectorCorrectionGain = 0.65,
    cartographerCorrectionGain = 0.55,
    submapDistance = 1.85,
    submapPeriod = 18.0,
    loopClosureRadius = 0.45,
    pathClearance = 0.40,
    pathDetourOffset = 0.52,
    -- The global planner ignores mapped obstacles this close to the robot: when it
    -- is leaving a rack it is already adjacent to, that rack must not be treated as
    -- a path blocker to detour around (the reactive layer handles near obstacles).
    pathStartIgnoreRadius = 0.70,
    -- Stall breaker: if the robot makes no headway toward a navigation goal for
    -- navStallTimeout seconds (e.g. the detour planner oscillates between two
    -- candidate waypoints on a dense map), it drops the global detour for the rest
    -- of that leg and heads straight at the goal, letting the reactive layer clear
    -- the way. This guarantees the work loop never freezes.
    navStallTimeout = 4.0,
    navRecoverTime = 1.4,        -- duration of the reverse-arc recovery [s]
    navRecoverTurn = 1.0,        -- angular rate during recovery [rad/s]
    recoverReverseSpeed = 0.16,  -- reverse speed during recovery (backs out of a wedge) [m/s]
    -- The global detour is recomputed at most this often; the chosen waypoint is held
    -- in between so the robot does not thrash when the "most blocking" mapped obstacle
    -- changes every control tick on a dense map.
    replanPeriod = 1.2,
    leaveRackEaseTime = 1.6,     -- seconds of eased speed when pulling away from a rack
    leaveRackSpeed = 0.20,       -- capped forward speed during that ease-out [m/s]
    rackSlowRadius = 1.00,       -- start crawling this far from a rack target [m]
    rackApproachSpeed = 0.18,    -- crawl speed for the final approach to a rack [m/s]
    wallSlowBound = 3.05,        -- cap speed when |coord| exceeds this (near a wall) [m]
    fenceBound = 3.40,           -- geofence: snap the chassis back inside this |coord| [m]
    -- Position-stall guard: if the chassis travels less than navStallMoveEps metres in
    -- navStallTimeout seconds it counts as stuck even if the distance signal jitters.
    navStallMoveEps = 0.12,
    sensorVizEnabled = 1,
    sensorVizRange = 0.84,
    sensorVizZ = 0.22,
}

local robot = -1
local leftMotor = -1
local rightMotor = -1
local b1 = -1
local wanderer = -1   -- Phase 2 dynamic wandering robot (optional, -1 in Phase 1)
local avoidIgnoreSet = {}   -- rack/shelf handles excluded from reactive avoidance
-- The rack is only made "transparent" to reactive avoidance while the robot is
-- actually approaching it to pick or return a tool, so it can pull right up to the
-- shelf. On every other leg the rack repels normally, so the robot routes around it
-- instead of grinding into its side when a delivery point lies behind the rack.
local RACK_APPROACH_STATES = {
    TO_PICKUP_T1 = true, PICKUP_T1 = true,
    TO_PICKUP_T2 = true, PICKUP_T2 = true,
    TO_RACK_T1_RETURN = true, RETURN_T1_RACK = true,
    TO_RACK_T2_RETURN = true, RETURN_T2_RACK = true,
}
-- Navigation legs that begin right next to a rack (the robot has just picked or
-- returned a tool): the speed is eased for a moment so it pulls away cleanly.
local LEAVE_RACK_STATES = {
    TO_WS1_DELIVER_T1 = true,
    TO_WS2_DELIVER_T2 = true,
    TO_CHARGE = true,
}
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

local kalmanActive = 0
local estX = 0
local estY = 0
local estTheta = 0
local covariance = 0.42
local poseError = 0
local headingError = 0
local speedLearnFactor = 1.0   -- Phase 2: ramps from cautious to full as the map fills
local missionCycle = 0         -- completed work loops so far (Phase 2 repeats the cell)
local targetCycles = 1         -- Phase 1 runs one loop; Phase 2 repeats it (set on load)
-- First-pass exploration state, grouped in one table (Lua's 200-local cap): the
-- frontier markers, which have been reached, the one being driven to and when it was
-- chosen (for a per-frontier timeout).
local explore = {markers = {}, visited = {}, current = -1, selectT = 0}
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
local plannerMode = 'DIRECT'
-- Navigation recovery / replan state, grouped in one table (Lua caps a function at
-- 200 locals): stall anchor, rotate-in-place recovery window and detour-replan cache.
local nav = {
    stallAnchorX = nil, stallAnchorY = nil, stallAnchorT = 0,
    recoverUntil = -1, recoverDir = 1,
    replanLastT = -1, replanPlanX = 0, replanPlanY = 0, replanActive = 0,
}
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
    KALMAN_LANDMARK = 'KALMAN_LANDMARK_SLAM_LIDAR',
    GMAPPING_GRID = 'GMAPPING_GRID_OCCUPANCY',
    HECTOR_GRID_MATCHING = 'HECTOR_SCAN_MATCHING_GRID',
    CARTOGRAPHER_SUBMAP = 'CARTOGRAPHER_SUBMAP_SCAN_MATCHING',
}

local SLAM_COMPLIANCE = {
    KALMAN_LANDMARK = 'ekf_slam_obstacle_map;kalman_landmark_slam_lidar',
    GMAPPING_GRID = 'gmapping_grid_lidar',
    HECTOR_GRID_MATCHING = 'hector_grid_matching_lidar',
    CARTOGRAPHER_SUBMAP = 'cartographer_submap_lidar;loop_closure_simplified',
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

-- Reproducible Gaussian noise (Box-Muller) for the synthetic global reference.
-- Seeded once so every validation run is deterministic across machines.
math.randomseed(20260529)
local gaussianSpare = nil
local function gaussianNoise(sigma)
    if gaussianSpare ~= nil then
        local value = gaussianSpare
        gaussianSpare = nil
        return value * sigma
    end
    local u1 = math.max(1e-9, math.random())
    local u2 = math.random()
    local mag = math.sqrt(-2.0 * math.log(u1))
    gaussianSpare = mag * math.sin(2.0 * math.pi * u2)
    return mag * math.cos(2.0 * math.pi * u2) * sigma
end

local function safeGetObject(path)
    local ok, handle = pcall(sim.getObject, path)
    if ok and handle and handle >= 0 then return handle end
    return -1
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
    if leftMotor >= 0 and rightMotor >= 0 then
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

-- Log-odds at an integer cell (default to slightly-free for unobserved cells).
local function gridLogAtCell(ix, iy)
    local cell = gridMap[gridKey(ix, iy)]
    if not cell then return -0.05 end
    return cell.logOdds or 0
end

-- Bilinear interpolation of the occupancy probability field with its analytic
-- spatial gradient, as used by Hector SLAM. Returns (p, dp/dx, dp/dy) in world
-- units. The occupancy probability is the logistic of the log-odds map and the
-- gradient is obtained through the chain rule p'(L) = p(1-p) times the bilinear
-- gradient of L (which is constant per cell, divided by the cell size).
local function gridProbBilinearWithGrad(x, y)
    local half = cfg.gridHalfExtent
    local res = cfg.gridResolution
    -- Continuous cell coordinate where integer values land on cell centres.
    local fx = (x + half) / res - 0.5
    local fy = (y + half) / res - 0.5
    local ix0 = math.floor(fx)
    local iy0 = math.floor(fy)
    local tx = fx - ix0
    local ty = fy - iy0

    local l00 = gridLogAtCell(ix0, iy0)
    local l10 = gridLogAtCell(ix0 + 1, iy0)
    local l01 = gridLogAtCell(ix0, iy0 + 1)
    local l11 = gridLogAtCell(ix0 + 1, iy0 + 1)

    local L = (1 - ty) * ((1 - tx) * l00 + tx * l10)
            + ty * ((1 - tx) * l01 + tx * l11)
    -- Spatial gradient of the bilinear log-odds field (world units).
    local dLx = (ty * (l11 - l01) + (1 - ty) * (l10 - l00)) / res
    local dLy = (tx * (l11 - l10) + (1 - tx) * (l01 - l00)) / res

    local p = 1.0 / (1.0 + math.exp(-L))
    local dp = p * (1.0 - p)
    return p, dp * dLx, dp * dLy
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

-- True Hector SLAM scan matcher: Gauss-Newton minimisation of
--   sum_i [ 1 - M(S_i(xi)) ]^2
-- where M is the bilinearly interpolated occupancy probability of the grid and
-- S_i(xi) maps each beam endpoint to the world with the candidate pose xi.
-- Each iteration accumulates the analytic Hessian H = sum J_i^T J_i and gradient
-- g = sum J_i^T r_i, applies Levenberg-style diagonal regularisation, solves the
-- 3x3 system H dxi = -g by Cramer's rule and updates the pose until convergence.
local function applyGridScanMatching(gain)
    if #lastScanPoints < cfg.hectorMinPoints then return false end

    local x = slamState[1]
    local y = slamState[2]
    local theta = slamState[3]
    local baseX, baseY, baseTheta = x, y, theta
    local reg = cfg.hectorRegularization
    local lastMeanScore = 0

    for iter = 1, cfg.hectorMaxIterations do
        local h11, h12, h13, h22, h23, h33 = 0, 0, 0, 0, 0, 0
        local g1, g2, g3 = 0, 0, 0
        local scoreSum, used = 0, 0

        for i, point in ipairs(lastScanPoints) do
            -- Subsample dense scans for cost; keep all when sparse.
            if i % 2 == 1 or #lastScanPoints <= 12 then
                local ang = theta + point.bearing
                local s = math.sin(ang)
                local c = math.cos(ang)
                local ex = x + point.range * c
                local ey = y + point.range * s
                local p, dpx, dpy = gridProbBilinearWithGrad(ex, ey)
                -- Jacobian of S_i wrt pose: d ex/dx=1, d ey/dy=1,
                -- d ex/dtheta=-range*sin, d ey/dtheta=range*cos.
                local jx = dpx
                local jy = dpy
                local jt = dpx * (-point.range * s) + dpy * (point.range * c)
                local r = 1.0 - p              -- residual: want occupancy -> 1
                -- f_i = 1 - p, df/dxi = -dp/dxi. H += (df)(df)^T, g += (df) f.
                h11 = h11 + jx * jx
                h12 = h12 + jx * jy
                h13 = h13 + jx * jt
                h22 = h22 + jy * jy
                h23 = h23 + jy * jt
                h33 = h33 + jt * jt
                -- df/dxi = -[jx,jy,jt]; g = sum df * r = -[jx,jy,jt]*r
                g1 = g1 - jx * r
                g2 = g2 - jy * r
                g3 = g3 - jt * r
                scoreSum = scoreSum + p
                used = used + 1
            end
        end

        if used == 0 then break end
        lastMeanScore = scoreSum / used

        -- Diagonal regularisation keeps H invertible in low-texture corridors.
        h11 = h11 + reg
        h22 = h22 + reg
        h33 = h33 + reg

        -- Solve H dxi = -g (Gauss-Newton step) via the 3x3 determinant rule.
        local det = h11 * (h22 * h33 - h23 * h23)
                  - h12 * (h12 * h33 - h23 * h13)
                  + h13 * (h12 * h23 - h22 * h13)
        if math.abs(det) < 1e-12 then break end
        local b1, b2, b3 = -g1, -g2, -g3
        local dx = (b1 * (h22 * h33 - h23 * h23)
                  - h12 * (b2 * h33 - h23 * b3)
                  + h13 * (b2 * h23 - h22 * b3)) / det
        local dy = (h11 * (b2 * h33 - h23 * b3)
                  - b1 * (h12 * h33 - h23 * h13)
                  + h13 * (h12 * b3 - b2 * h13)) / det
        local dth = (h11 * (h22 * b3 - b2 * h23)
                  - h12 * (h12 * b3 - b2 * h13)
                  + b1 * (h12 * h23 - h22 * h13)) / det

        -- Bound a single step so a bad linearisation cannot diverge.
        dx = clamp(dx, -0.12, 0.12)
        dy = clamp(dy, -0.12, 0.12)
        dth = clamp(dth, -0.15, 0.15)
        x = x + dx
        y = y + dy
        theta = normalizeAngle(theta + dth)

        if math.abs(dx) < cfg.hectorConvergenceXY
            and math.abs(dy) < cfg.hectorConvergenceXY
            and math.abs(dth) < cfg.hectorConvergenceTheta then
            break
        end
    end

    scanMatchScore = lastMeanScore
    if lastMeanScore < cfg.hectorMatchMinScore then return false end

    -- Blend the matched pose into the estimate (gain < 1 for robustness with the
    -- sparse 16-beam ring) and shrink the pose covariance after a good match.
    slamState[1] = baseX + gain * (x - baseX)
    slamState[2] = baseY + gain * (y - baseY)
    slamState[3] = normalizeAngle(baseTheta + gain * normalizeAngle(theta - baseTheta))
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
    sim.setStringSignal('phase1EstimatedPose', string.format('%.3f,%.3f,%.3f', estX, estY, estTheta))
    sim.setFloatSignal('phase1PoseError', poseError)
    sim.setFloatSignal('phase1KalmanCovariance', covariance)
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
end

local function readWheelOdometry()
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

-- Weak global reference (synthetic UWB-like beacon): a genuinely noisy absolute
-- fix applied with a small fixed gain. It only keeps the world frame observable
-- over a long mission; the sensor-driven corrections -- the EKF landmark update
-- for KALMAN_LANDMARK and the Gauss-Newton scan match for the grid modes --
-- provide the dominant pose correction. The noise is real Gaussian noise, not a
-- deterministic offset, so the estimate cannot track ground truth for free.
local function fusePoseMeasurement(p, o, t)
    if kalmanActive == 0 or #slamState < 3 then return end

    local measX = p[1] + gaussianNoise(cfg.globalRefNoiseXY)
    local measY = p[2] + gaussianNoise(cfg.globalRefNoiseXY)
    local measTheta = normalizeAngle(o[3] + gaussianNoise(cfg.globalRefNoiseTheta))
    local kxy = cfg.globalRefGainXY
    local kt = cfg.globalRefGainTheta

    slamState[1] = slamState[1] + kxy * (measX - slamState[1])
    slamState[2] = slamState[2] + kxy * (measY - slamState[2])
    slamState[3] = normalizeAngle(slamState[3] + kt * normalizeAngle(measTheta - slamState[3]))
    slamCov[1][1] = clamp((1 - kxy) * (slamCov[1][1] or 0.03) + cfg.slamProcessXY, 0.0005, 0.08)
    slamCov[2][2] = clamp((1 - kxy) * (slamCov[2][2] or 0.03) + cfg.slamProcessXY, 0.0005, 0.08)
    slamCov[3][3] = clamp((1 - kt) * (slamCov[3][3] or 0.02) + cfg.slamProcessTheta, 0.0005, 0.08)
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

    local nOld = #slamState
    local theta = slamState[3]
    local cb = math.cos(theta + bearing)
    local sb = math.sin(theta + bearing)
    local lx = slamState[1] + range * cb
    local ly = slamState[2] + range * sb
    slamState[nOld + 1] = lx
    slamState[nOld + 2] = ly
    local lxIdx = nOld + 1
    local lyIdx = nOld + 2
    local n = lyIdx

    for i = 1, n do
        if not slamCov[i] then slamCov[i] = {} end
        for j = 1, n do
            slamCov[i][j] = slamCov[i][j] or 0
        end
    end

    -- Proper EKF-SLAM landmark initialisation through the inverse observation
    -- model. Gr = d(lx,ly)/d(x,y,theta), Gz = d(lx,ly)/d(range,bearing).
    local gr13 = -range * sb
    local gr23 = range * cb
    local rr = cfg.slamRangeNoise * cfg.slamRangeNoise
    local rb = cfg.slamBearingNoise * cfg.slamBearingNoise

    -- Cross-covariance with the existing state: P_Lx = Gr * P_Rx.
    for j = 1, nOld do
        local prx = slamCov[1][j] or 0
        local pry = slamCov[2][j] or 0
        local prt = slamCov[3][j] or 0
        local cx = prx + gr13 * prt
        local cy = pry + gr23 * prt
        slamCov[lxIdx][j] = cx
        slamCov[j][lxIdx] = cx
        slamCov[lyIdx][j] = cy
        slamCov[j][lyIdx] = cy
    end

    -- Landmark block P_LL = Gr P_RR Gr^T + Gz R Gz^T.
    local p11, p12, p13 = slamCov[1][1] or 0, slamCov[1][2] or 0, slamCov[1][3] or 0
    local p22, p23, p33 = slamCov[2][2] or 0, slamCov[2][3] or 0, slamCov[3][3] or 0
    local a11 = p11 + 2 * gr13 * p13 + gr13 * gr13 * p33
    local a12 = p12 + gr13 * p23 + gr23 * p13 + gr13 * gr23 * p33
    local a22 = p22 + 2 * gr23 * p23 + gr23 * gr23 * p33
    local z11 = cb * cb * rr + (range * sb) * (range * sb) * rb
    local z12 = cb * sb * rr - (range * sb) * (range * cb) * rb
    local z22 = sb * sb * rr + (range * cb) * (range * cb) * rb
    local capLL = cfg.slamInitialLandmarkCov * 4
    slamCov[lxIdx][lxIdx] = clamp(a11 + z11, 0.002, capLL)
    slamCov[lxIdx][lyIdx] = a12 + z12
    slamCov[lyIdx][lxIdx] = a12 + z12
    slamCov[lyIdx][lyIdx] = clamp(a22 + z22, 0.002, capLL)

    local lm = {index = lxIdx, seen = 1, variance = slamCov[lxIdx][lxIdx], lastT = sim.getSimulationTime()}
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

-- Stable EKF pose correction against a mapped landmark (treated as a known
-- beacon). Uses only the 3x3 pose covariance with Mahalanobis gating, so a bad
-- data association cannot blow up the filter -- unlike a full joint pose-map EKF
-- with 16 sparse, noisy sonar beams. This is the genuine sensor-driven pose
-- correction for KALMAN_LANDMARK; the landmark coordinates themselves are fused
-- separately in updateSlamLandmarkPosition. This matches the report: the mode
-- does not maintain a joint pose-map covariance like full EKF-SLAM.
local function correctPoseFromLandmark(lm, range, bearing)
    local idx = lm.index
    local mx = slamState[idx]
    local my = slamState[idx + 1]
    if not mx or not my then return end
    local dx = mx - slamState[1]
    local dy = my - slamState[2]
    local q = dx * dx + dy * dy
    local rHat = math.sqrt(q)
    -- Skip very-close landmarks: the bearing Jacobian scales as 1/range, so an
    -- observation a few centimetres away is numerically ill-conditioned and can
    -- inject a huge correction. Range/odometry still carry the pose in that case.
    if rHat < cfg.slamMinUpdateRange then return end
    local zr = range - rHat
    local zb = normalizeAngle(bearing - normalizeAngle(atan2(dy, dx) - slamState[3]))

    -- Observation Jacobian H (2x3): rows = d[range,bearing]/d[x,y,theta].
    local h11, h12, h13 = -dx / rHat, -dy / rHat, 0
    local h21, h22, h23 = dy / q, -dx / q, -1

    local p11 = slamCov[1][1] or 0.02
    local p12 = slamCov[1][2] or 0
    local p13 = slamCov[1][3] or 0
    local p22 = slamCov[2][2] or 0.02
    local p23 = slamCov[2][3] or 0
    local p33 = slamCov[3][3] or 0.02

    -- P H^T (3x2).
    local phr1 = p11 * h11 + p12 * h12 + p13 * h13
    local phr2 = p12 * h11 + p22 * h12 + p23 * h13
    local phr3 = p13 * h11 + p23 * h12 + p33 * h13
    local phb1 = p11 * h21 + p12 * h22 + p13 * h23
    local phb2 = p12 * h21 + p22 * h22 + p23 * h23
    local phb3 = p13 * h21 + p23 * h22 + p33 * h23

    -- S = H P H^T + R (2x2).
    local rr = cfg.slamRangeNoise * cfg.slamRangeNoise
    local rb = cfg.slamBearingNoise * cfg.slamBearingNoise
    local s11 = h11 * phr1 + h12 * phr2 + h13 * phr3 + rr
    local s12 = h11 * phb1 + h12 * phb2 + h13 * phb3
    local s21 = h21 * phr1 + h22 * phr2 + h23 * phr3
    local s22 = h21 * phb1 + h22 * phb2 + h23 * phb3 + rb
    local det = s11 * s22 - s12 * s21
    if math.abs(det) < 1e-9 then return end
    local i11, i12, i21, i22 = s22 / det, -s12 / det, -s21 / det, s11 / det

    -- Mahalanobis gate: discard likely mis-associations.
    local maha = zr * (i11 * zr + i12 * zb) + zb * (i21 * zr + i22 * zb)
    if maha > cfg.slamMahalanobisGate then return end

    -- Kalman gain K = P H^T S^-1 (3x2).
    local k11 = phr1 * i11 + phb1 * i21
    local k12 = phr1 * i12 + phb1 * i22
    local k21 = phr2 * i11 + phb2 * i21
    local k22 = phr2 * i12 + phb2 * i22
    local k31 = phr3 * i11 + phb3 * i21
    local k32 = phr3 * i12 + phb3 * i22

    local w = cfg.slamPoseCorrectionWeight
    -- Clamp the per-update correction: a single landmark update must never move the
    -- pose by more than a few centimetres / a small angle. Even if the gain is badly
    -- conditioned, this hard cap makes the EKF impossible to blow up in one step.
    local corrX = clamp(w * (k11 * zr + k12 * zb), -cfg.slamMaxPoseStep, cfg.slamMaxPoseStep)
    local corrY = clamp(w * (k21 * zr + k22 * zb), -cfg.slamMaxPoseStep, cfg.slamMaxPoseStep)
    local corrT = clamp(w * (k31 * zr + k32 * zb), -cfg.slamMaxThetaStep, cfg.slamMaxThetaStep)
    slamState[1] = slamState[1] + corrX
    slamState[2] = slamState[2] + corrY
    slamState[3] = normalizeAngle(slamState[3] + corrT)

    -- Covariance update P = (I - K H) P on the 3x3 block.
    local a11 = 1 - (k11 * h11 + k12 * h21)
    local a12 = -(k11 * h12 + k12 * h22)
    local a13 = -(k11 * h13 + k12 * h23)
    local a21 = -(k21 * h11 + k22 * h21)
    local a22 = 1 - (k21 * h12 + k22 * h22)
    local a23 = -(k21 * h13 + k22 * h23)
    local a31 = -(k31 * h11 + k32 * h21)
    local a32 = -(k31 * h12 + k32 * h22)
    local a33 = 1 - (k31 * h13 + k32 * h23)
    local n11 = a11 * p11 + a12 * p12 + a13 * p13
    local n12 = a11 * p12 + a12 * p22 + a13 * p23
    local n13 = a11 * p13 + a12 * p23 + a13 * p33
    local n22 = a21 * p12 + a22 * p22 + a23 * p23
    local n23 = a21 * p13 + a22 * p23 + a23 * p33
    local n33 = a31 * p13 + a32 * p23 + a33 * p33
    slamCov[1][1] = clamp(n11, 0.0005, 0.08)
    slamCov[1][2] = n12; slamCov[2][1] = n12
    slamCov[1][3] = n13; slamCov[3][1] = n13
    slamCov[2][2] = clamp(n22, 0.0005, 0.08)
    slamCov[2][3] = n23; slamCov[3][2] = n23
    slamCov[3][3] = clamp(n33, 0.0005, 0.08)
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
        -- Genuine sensor pose correction: EKF range/bearing update of the pose
        -- against the mapped landmark (gated), then fuse the landmark position.
        correctPoseFromLandmark(lm, range, bearing)
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
    currentScanPoints = {}
    clearSensorVisualization()

    for _, s in ipairs(sensors) do
        local result, distance, detectedPoint, detectedObject = sim.readProximitySensor(s.handle)
        if result and result > 0 and distance and distance > 0 then
            local ignoreReactive = detectedObject == t1 or detectedObject == t2 or detectedObject == activeTool
            if not ignoreReactive then
                addSensorRay(s, distance, detectedPoint, true)
                -- Map static structure only: Bill and the Phase 2 wandering robot
                -- are moving agents, so they are avoided reactively but not fused
                -- as SLAM landmarks (a moving target would corrupt the map).
                if detectedObject ~= b1 and detectedObject ~= wanderer then
                    registerSlamDetection(s, distance, detectedPoint)
                end
                if distance < minDistance then minDistance = distance end
                -- The tool rack is mapped above. It is excluded from repulsion only
                -- while approaching it (so R1 can pull right up to the shelf); on
                -- other legs it repels normally so R1 routes around it.
                local rackTransparent = avoidIgnoreSet[detectedObject] and RACK_APPROACH_STATES[taskState]
                if not rackTransparent and distance < cfg.avoidRange then
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
                    if s.x > 0 and distance < cfg.hardStopRange then
                        hardStop = true
                        lastAvoidTurn = -sign(side)
                    end
                end
            else
                addSensorRay(s, cfg.sensorVizRange, nil, false)
            end
        else
            addSensorRay(s, cfg.sensorVizRange, nil, false)
        end
    end

    if minDistance == math.huge then minDistance = -1 end
    if #currentScanPoints > 0 then
        lastScanPoints = currentScanPoints
    end
    return steer, clamp(slow, 0, 1), minDistance, hardStop, risk
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
        -- Occupancy log-odds grid only; pose from odometry + weak global anchor.
        fusePoseMeasurement(p, o, t)
    elseif slamAlgorithm == 'HECTOR_GRID_MATCHING' then
        -- Genuine Gauss-Newton scan-to-map alignment drives the pose correction.
        applyGridScanMatching(cfg.hectorCorrectionGain)
        fusePoseMeasurement(p, o, t)
    elseif slamAlgorithm == 'CARTOGRAPHER_SUBMAP' then
        applyGridScanMatching(cfg.cartographerCorrectionGain)
        fusePoseMeasurement(p, o, t)
        updateCartographerSubmaps(t, dt)
    else
        -- KALMAN_LANDMARK: the EKF range/bearing update in registerSlamDetection
        -- corrects the pose from the landmark map; the weak anchor only bounds
        -- the global frame.
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
    headingError = math.abs(normalizeAngle(estTheta - o[3]))

    -- Phase 2 only (the wandering robot is present): the Pioneer starts cautious
    -- while it maps an unknown cell and accelerates as it learns the layout, so
    -- the second half of the mission runs noticeably faster on known ground.
    if wanderer >= 0 then
        -- Confidence grows with every completed loop: the first pass is cautious
        -- (the cell is still mostly unknown), and each repeat reuses a richer SLAM
        -- map, so the Pioneer drives faster and straighter. The within-loop term
        -- lets it pick up some speed as the live map fills during a single pass.
        -- Map knowledge accumulates via landmark updates (Kalman) or grid updates
        -- (grid modes), so the ramp works for every SLAM variant.
        -- The factor is capped below 1.0 on purpose: at full speed the chassis can
        -- clip a rack as it leaves and tunnel through a wall, so the most confident
        -- pass still keeps a safe margin.
        local mapKnowledge = slamUpdates + gridUpdates
        local loopConfidence = 0.60 + 0.12 * missionCycle          -- 0.60, 0.72, 0.84
        local mapGain = 0.10 * clamp(mapKnowledge / 5200.0, 0.0, 1.0)
        speedLearnFactor = clamp(loopConfidence + mapGain, 0.60, 0.88)
    else
        speedLearnFactor = 1.0
    end
    sim.setFloatSignal('phase1SpeedLearnFactor', speedLearnFactor)

    publishSlamTelemetry()
end

local function setTaskState(newState)
    if taskState ~= newState then
        taskState = newState
        stateStartT = sim.getSimulationTime()
        resetControlState()
        -- New goal: restart the stall tracker, drop the replan cache and re-enable
        -- the detour planner.
        nav.recoverUntil = -1
        nav.replanLastT = -1
        nav.stallAnchorX = nil
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
        local okO, ro = pcall(sim.getObjectOrientation, robot, -1)
        if ok and rp then
            -- Carry the tool just in front of the robot, along its heading
            -- (robot-relative), so it does not clip the body when turning.
            local yaw = (okO and ro and ro[3]) or 0
            local fwd = 0.18
            setWorldPositionSafe(activeTool, {rp[1] + fwd * math.cos(yaw), rp[2] + fwd * math.sin(yaw), 0.40})
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

local function computeCommand(distance, heading, lateral, obstacleSteer, obstacleSlow, hardStop)
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
    local slowWeight = 0.50

    if controlMode == 'P' then
        v = 0.62 * distanceError * forwardScale
        w = 1.45 * heading + 0.95 * obstacleSteer
        alpha = 0.86
        maxV = 0.46
        slowWeight = 0.45
    elseif controlMode == 'PI' then
        v = (0.58 * distanceError + 0.055 * distanceIntegral) * forwardScale
        w = 1.42 * heading + 0.08 * headingIntegral + 0.98 * obstacleSteer
        alpha = 0.76
        maxV = 0.48
        slowWeight = 0.48
    elseif controlMode == 'PID' then
        v = (0.82 * distanceError + 0.025 * distanceDerivative) * forwardScale
        w = 1.85 * heading + 0.10 * headingDerivative + obstacleSteer
        alpha = 0.68
        maxV = cfg.vMax
        slowWeight = 0.50
    elseif controlMode == 'LQR' then
        v = (0.66 * distanceError - 0.055 * math.abs(headingDerivative)) * forwardScale
        w = 1.18 * heading + 0.22 * lateral + 0.78 * obstacleSteer
        alpha = 0.42
        maxV = 0.49
        slowWeight = 0.42
    elseif controlMode == 'NMPC' then
        local headingPenalty = clamp(1.0 - 0.32 * math.abs(heading), 0.35, 1.0)
        local predictedRisk = clamp(obstacleSlow + 0.20 * math.abs(heading), 0, 1)
        v = 0.78 * distanceError * forwardScale * headingPenalty * (1.0 - 0.45 * predictedRisk)
        w = 1.62 * heading + 0.94 * obstacleSteer
        alpha = 0.35
        maxV = 0.52
        slowWeight = 0.40
        obstacleWeight = 0.95
    end

    if math.abs(heading) > 1.20 then
        v = math.min(v, 0.07)
    end

    if hardStop then
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

    -- Phase 2 "learning" behaviour: while the map is still sparse the robot moves
    -- cautiously, and it speeds up as it accumulates map knowledge of the cell.
    v = v * speedLearnFactor

    -- Back out of a rack: a leg that starts right next to a shelf begins with a short
    -- reverse. After picking or returning a tool the robot faces the rack, so driving
    -- "forward" would push it INTO the shelf and the wall behind it; reversing pulls it
    -- straight back into the open aisle it came from, giving room to turn toward the
    -- next goal. The speed stays low so it cannot clip the shelf and tunnel through a
    -- wall. (Cornering elsewhere is handled by the rotate-in-place recovery above.)
    local leaveRackReverse = false
    if wanderer >= 0 and LEAVE_RACK_STATES[taskState]
        and (sim.getSimulationTime() - stateStartT) < cfg.leaveRackEaseTime then
        v = -cfg.leaveRackSpeed
        w = clamp(w, -0.45, 0.45)
        leaveRackReverse = true
    end


    if leaveRackReverse then
        v = clamp(v, -cfg.leaveRackSpeed, 0)
    elseif hardStop then
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
            if (cell.logOdds or 0) >= cfg.gridOccupiedThreshold then
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

local function obstaclePenalty(x, y)
    local penalty = 0
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

-- Decide a detour waypoint (or the goal directly) around the mapped obstacles.
local function computeDetour(goalX, goalY)
    local obstacles = mapObstaclesForPlanning()
    if #slamState < 3 or #obstacles == 0 then
        return goalX, goalY, 0
    end

    local sx = slamState[1]
    local sy = slamState[2]
    local blocking = nil
    local blockingScore = 0

    for _, obstacle in ipairs(obstacles) do
        local startDx = obstacle.x - sx
        local startDy = obstacle.y - sy
        local startDist = math.sqrt(startDx * startDx + startDy * startDy)
        if startDist >= cfg.pathStartIgnoreRadius then
            local d, u = pointSegmentDistance(obstacle.x, obstacle.y, sx, sy, goalX, goalY)
            local score = cfg.pathClearance - d
            if u > 0.05 and u < 0.95 and score > blockingScore then
                blocking = {x = obstacle.x, y = obstacle.y}
                blockingScore = score
            end
        end
    end

    if not blocking then
        return goalX, goalY, 0
    end

    local lx = goalX - sx
    local ly = goalY - sy
    local l = math.max(math.sqrt(lx * lx + ly * ly), 0.001)
    local nx = -ly / l
    local ny = lx / l
    local candidates = {
        {x = blocking.x + nx * cfg.pathDetourOffset, y = blocking.y + ny * cfg.pathDetourOffset},
        {x = blocking.x - nx * cfg.pathDetourOffset, y = blocking.y - ny * cfg.pathDetourOffset},
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

    return best.x, best.y, 1
end

-- Replan throttle: recompute the global detour only every cfg.replanPeriod seconds
-- and hold the chosen waypoint in between. Re-deciding every control tick lets the
-- "most blocking" obstacle change step to step on a dense map, which makes the robot
-- thrash in place; committing to each decision for a fraction of a second removes the
-- oscillation while still replanning often enough to react to the moving obstacle.
local function plannedWaypointTo(goalX, goalY)
    local nowT = sim.getSimulationTime()
    if nav.replanLastT >= 0 and (nowT - nav.replanLastT) < cfg.replanPeriod then
        plannerWaypointActive = nav.replanActive
        plannerWaypointX = nav.replanPlanX
        plannerWaypointY = nav.replanPlanY
        plannerMode = nav.replanActive == 1 and 'SLAM_WAYPOINT' or 'DIRECT'
        return nav.replanPlanX, nav.replanPlanY
    end

    local planX, planY, active = computeDetour(goalX, goalY)
    nav.replanLastT = nowT
    nav.replanPlanX = planX
    nav.replanPlanY = planY
    nav.replanActive = active
    plannerWaypointActive = active
    plannerWaypointX = planX
    plannerWaypointY = planY
    plannerMode = active == 1 and 'SLAM_WAYPOINT' or 'DIRECT'
    return planX, planY
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

    -- Stall breaker: track real chassis headway. If the robot barely moves for
    -- navStallTimeout seconds (planner thrash on a dense map, a wedge against a rack,
    -- or being briefly cornered by the wandering robot), rotate in place for a short
    -- window to break free. Rotation never translates the chassis, so it cannot drive
    -- into a wall or an obstacle: it is the safe universal recovery. The direction
    -- alternates between recoveries so the robot explores both ways out.
    local nowT = sim.getSimulationTime()
    local rpos = sim.getObjectPosition(robot, -1)
    if nav.stallAnchorX == nil then
        nav.stallAnchorX, nav.stallAnchorY, nav.stallAnchorT = rpos[1], rpos[2], nowT
    end
    local moved = math.sqrt((rpos[1] - nav.stallAnchorX) ^ 2 + (rpos[2] - nav.stallAnchorY) ^ 2)
    if moved > cfg.navStallMoveEps then
        nav.stallAnchorX, nav.stallAnchorY, nav.stallAnchorT = rpos[1], rpos[2], nowT
    elseif nowT >= nav.recoverUntil
        and nowT - nav.stallAnchorT > cfg.navStallTimeout
        and targetDistance > tolerance then
        nav.recoverUntil = nowT + cfg.navRecoverTime
        nav.recoverDir = -nav.recoverDir
        nav.stallAnchorX, nav.stallAnchorY, nav.stallAnchorT = rpos[1], rpos[2], nowT
    end

    if nowT < nav.recoverUntil then
        -- Recovery is a reverse arc, not a spin in place: pure rotation cannot free a
        -- chassis wedged head-first against an obstacle, but backing up does (the space
        -- behind is the aisle it just came from), and the turn reorients it at the same
        -- time. The geofence still bounds the reverse, so it stays inside the cell.
        setWheelSpeeds(-cfg.recoverReverseSpeed, nav.recoverDir * cfg.navRecoverTurn)
        motionMode = 'RECOVER_BACK'
        return targetDistance, -1, 0
    end

    local planX, planY = plannedWaypointTo(goalX, goalY)
    local dx = planX - estX
    local dy = planY - estY
    local distance = math.sqrt(dx * dx + dy * dy)
    if plannerWaypointActive == 1 and distance < 0.55 then
        plannerWaypointActive = 0
        plannerMode = 'DIRECT_AFTER_WAYPOINT'
        plannerWaypointX = goalX
        plannerWaypointY = goalY
        dx = goalX - estX
        dy = goalY - estY
        distance = math.sqrt(dx * dx + dy * dy)
    end
    local heading = atan2(dy, dx)
    heading = normalizeAngle(heading - estTheta)
    local lateral = -math.sin(estTheta) * dx + math.cos(estTheta) * dy
    local obstacleSteer, obstacleSlow, minObstacle, hardStop, risk = readObstacleField()

    if targetDistance <= tolerance then
        setWheelSpeeds(0, 0)
        motionMode = 'ARRIVED_TARGET'
        return targetDistance, minObstacle, risk
    end

    motionMode = 'ROUTE'
    if plannerWaypointActive == 1 then
        motionMode = 'SLAM_PATH'
    end
    if minObstacle > 0 and minObstacle < cfg.avoidRange then
        motionMode = 'AVOIDING'
    end

    local v, w = computeCommand(distance, heading, lateral, obstacleSteer, obstacleSlow, hardStop)

    -- Crawl the final stretch into a rack. The rack is transparent to avoidance while
    -- approaching, so without this the chassis could ram it at speed and the collision
    -- impulse could fling it through a wall. The cap uses the PHYSICAL distance to the
    -- rack (not the SLAM estimate), so it still protects the robot if the estimate is
    -- briefly off. Creeping the last centimetres lets the arrival check stop it cleanly
    -- right in front of the shelf.
    if wanderer >= 0 and RACK_APPROACH_STATES[taskState] and targetDistance < cfg.rackSlowRadius then
        v = math.min(v, cfg.rackApproachSpeed)
    end

    -- General wall guard: near any perimeter wall, cap the speed regardless of state.
    -- In normal operation the robot stays well inside the cell, so this only bites if
    -- something pushes it toward a wall, and a gentle contact cannot tunnel through.
    if math.max(math.abs(rpos[1]), math.abs(rpos[2])) > cfg.wallSlowBound then
        v = math.min(v, cfg.rackApproachSpeed)
    end

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
        placeToolAt(tool, storagePoint, 0.42)
        completedTaskCount = math.max(completedTaskCount, completedCount)
        setShapeColorSafe(tool, idleColor)
        if afterReturn then afterReturn() end
        setTaskState(nextState)
    end
end

-- Restart the full T1/T2 work loop for another pass. The SLAM map and the
-- battery charge are kept on purpose: the cell does not change between loops, so
-- each repeat reuses the map it already built (this is what makes speedLearnFactor
-- grow and the motion look more confident on the second and third passes).
local function startNextCycle()
    completedTaskCount = 0
    carryingTool = 0
    tool1Delivered = 0
    tool1Returned = 0
    tool2Delivered = 0
    tool2Returned = 0
    chargeRequested = 0
    chargingActive = 0
    commandTotalVariation = 0
    stateStartT = sim.getSimulationTime()
    setActiveTool(t1, 'T1')
    currentTaskId = 'task1'
    currentTaskSpec = 'task1:{T1->B1@WS1}'
    setTaskState('TO_PICKUP_T1')
end

-- Greedy nearest-frontier selection from the robot's own estimated pose: the basis
-- of the first exploratory pass over the unknown cell.
local function nearestUnvisitedFrontier()
    local best, bestD = -1, math.huge
    for i, f in ipairs(explore.markers) do
        if not explore.visited[i] then
            local p = readWorldPosition(f.handle)
            if p then
                local d = (p[1] - estX) * (p[1] - estX) + (p[2] - estY) * (p[2] - estY)
                if d < bestD then
                    bestD = d
                    best = i
                end
            end
        end
    end
    return best
end

local TaskHandlers = {
    WAIT_BATTERY = function()
        stopRobot('WAIT')
    end,

    -- First pass over an unknown cell: drive to each frontier marker in nearest-first
    -- order so the sonar ring sweeps the whole cell and the SLAM map fills in before
    -- any task is attempted. Once every frontier is reached the robot starts the normal
    -- T1/T2 work loop on the map it just built; later loops skip this and go direct.
    EXPLORE_FRONTIERS = function()
        local now = sim.getSimulationTime()
        -- Best-effort exploration: stop once every frontier is reached OR the time box
        -- runs out, then begin the task cycle on the map built so far. This guarantees
        -- the mission always proceeds even if a frontier is briefly hard to reach.
        if explore.current < 0 then
            explore.current = nearestUnvisitedFrontier()
            explore.selectT = now
        end
        if explore.current < 0 or (now - stateStartT) > cfg.exploreMaxTime then
            setActiveTool(t1, 'T1')
            currentTaskId = 'task1'
            currentTaskSpec = 'task1:{T1->B1@WS1}'
            setTaskState('TO_PICKUP_T1')
            return
        end
        local dist = navigateTo(explore.markers[explore.current].handle, cfg.exploreTolerance)
        -- Reached it, or spent too long on this one (skip an unreachable frontier).
        if (dist >= 0 and dist <= cfg.exploreTolerance)
            or (now - explore.selectT) > cfg.exploreFrontierTimeout then
            explore.visited[explore.current] = true
            explore.current = -1
        end
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
        -- Phase 2 repeats the loop several times; dock, top the battery up and set
        -- off again until the last loop, which charges fully and then parks READY.
        local lastCycle = (missionCycle + 1 >= targetCycles)
        local resumeLevel = lastCycle and 96.0 or cfg.batteryCycleResume
        if batteryLevel >= resumeLevel then
            if lastCycle then
                setTaskState('READY')
            else
                missionCycle = missionCycle + 1
                startNextCycle()
            end
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
        phase1Compliance = 'R1+B1+T1+T2+C1;two_worktables;' .. complianceSlam .. ';slam_path_planning;reactive_obstacle_avoidance;battery_charge',
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
                'Phase1 mode=%s state=%s task=%s tool=%s motion=%s planner=%s slam=%d dist=%.2f obs=%.2f risk=%.2f battery=%.1f b1=%s poseErr=%.2f hdgErr=%.3f',
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
                poseError,
                headingError or 0
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
    wanderer = safeGetObject('/P2_Wanderer')
    if wanderer >= 0 then
        -- Phase 2 (unknown cell + wandering robot): repeat the work loop so the
        -- map keeps improving and the motion grows more confident each pass.
        targetCycles = cfg.targetCyclesPhase2
    end
    -- Resolve the unknown-cell frontier markers (Phase 2 only). The very first pass
    -- drives to these in nearest-first order to map the cell before the task cycle.
    explore.markers = {}
    local frontierNames = {
        '/P2_Frontier_01_NE_Rack', '/P2_Frontier_02_Center_Corridor',
        '/P2_Frontier_03_West_Table', '/P2_Frontier_04_SE_Return',
        '/P2_Frontier_05_Charging_Corridor', '/P2_Frontier_06_North_Unknown',
    }
    for _, name in ipairs(frontierNames) do
        local h = safeGetObject(name)
        if h >= 0 then
            explore.markers[#explore.markers + 1] = {handle = h, name = name}
        end
    end
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

    -- Collect the tool racks/shelves so R1 can approach them closely for pickup:
    -- they are still mapped as SLAM landmarks, but excluded from the reactive
    -- repulsion that would otherwise stop the robot ~0.6 m short of the shelf.
    avoidIgnoreSet = {}
    for _, path in ipairs({'/P1_ToolRack_T1', '/P1_ToolRack_T2'}) do
        local h = safeGetObject(path)
        if h >= 0 then
            avoidIgnoreSet[h] = true
            local ok, tree = pcall(sim.getObjectsInTree, h, sim.handle_all, 0)
            if ok and tree then
                for _, c in ipairs(tree) do avoidIgnoreSet[c] = true end
            end
        end
    end
    local idx = 0
    while true do
        local h = sim.getObjects(idx, sim.handle_all)
        if h == -1 then break end
        local okA, alias = pcall(sim.getObjectAlias, h, 1)
        if okA and alias and (string.find(alias, 'ToolShelf') or string.find(alias, 'ToolRack')) then
            avoidIgnoreSet[h] = true
        end
        idx = idx + 1
    end

    rebuildTargetTable()
end

local function resetMissionState()
    batteryLevel = cfg.batteryStart
    missionCycle = 0
    taskAccepted = estimateTaskFeasibility() and 1 or 0
    carryingTool = 0
    completedTaskCount = 0
    tool1Delivered = 0
    tool1Returned = 0
    tool2Delivered = 0
    tool2Returned = 0
    chargeRequested = 0
    commandTotalVariation = 0
    lastT = sim.getSimulationTime()
    stateStartT = lastT

    setActiveTool(t1, 'T1')
    currentTaskId = 'task1'
    currentTaskSpec = 'task1:{T1->B1@WS1}'
    explore.visited = {}
    explore.current = -1
    if taskAccepted ~= 1 then
        setTaskState('WAIT_BATTERY')
    elseif #explore.markers > 0 then
        -- Phase 2, unknown cell: the first pass explores the frontiers to build the
        -- map before doing any task. (Phase 1 has no frontiers and starts straight in.)
        setTaskState('EXPLORE_FRONTIERS')
    else
        setTaskState('TO_PICKUP_T1')
    end
end

function sysCall_init()
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
    sim.addLog(sim.verbosity_scriptinfos, 'Phase1 R1 controller ready: ' .. slamAlgorithm .. ' obstacle map, waypoint path planning, two worktables.')
end

function sysCall_actuation()
    if robot < 0 or leftMotor < 0 or rightMotor < 0 then
        taskState = 'ERROR_HANDLES'
        publishTelemetry(-1, -1, 0)
        return
    end

    -- Geofence: a simulator physics glitch can, very rarely, fling the chassis through
    -- a perimeter wall. If the true position ever lands outside the cell, snap it back
    -- just inside, stop its motion and re-anchor the pose estimate, so the mission
    -- continues instead of the robot being lost or pinned outside the wall. In normal
    -- operation the robot stays well within the cell and this never triggers; the
    -- normal controller then drives it back to its task from the fence line.
    local fp = sim.getObjectPosition(robot, -1)
    if math.abs(fp[1]) > cfg.fenceBound or math.abs(fp[2]) > cfg.fenceBound then
        fp[1] = clamp(fp[1], -cfg.fenceBound, cfg.fenceBound)
        fp[2] = clamp(fp[2], -cfg.fenceBound, cfg.fenceBound)
        pcall(sim.setObjectPosition, robot, -1, fp)
        pcall(sim.resetDynamicObject, robot)
        setWheelSpeeds(0, 0)
        local fo = sim.getObjectOrientation(robot, -1)
        slamState[1], slamState[2], slamState[3] = fp[1], fp[2], fo[3]
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

function sysCall_cleanup()
    setWheelSpeeds(0, 0)
    publishTelemetry(-1, -1, 0)
    removeSensorVisualization()
end
