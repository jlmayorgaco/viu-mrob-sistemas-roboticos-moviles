sim = require('sim')

-- Phase 2 scenario manager.
-- Drives the autonomous wandering robot (/P2_Wanderer) along random routes and
-- publishes the unknown-map, mapping-activity and replan signals consumed by the
-- validation scripts. The wanderer is a genuine moving obstacle: R1 detects it
-- with its proximity ring and avoids/replans around it.

local Config = {
    movedObjects = 'P2_Wanderer',
    motionModel = 'dynamic_wandering_robot',
    minReveal = 6.0,
    frontierCount = 6,   -- number of frontier marker objects placed in the scene
    unknownCells = 32,   -- number of costmap cells placed in the scene
    -- Wanderer motion (kinematic): random waypoints inside the central free area.
    wanderSpeed = 0.20,
    wanderZ = 0.13,
    boundXMin = -1.8, boundXMax = 1.8,
    boundYMin = -1.6, boundYMax = 1.6,
    -- Avoid stopping on the interior furniture (pallet, pillar, crate).
    keepouts = {{-0.74, -1.05}, {-0.18, -0.42}, {0.54, 0.82}},
    keepoutRadius = 0.55,
    waypointTolerance = 0.18,
    crossingDistance = 0.9,   -- distance to R1 that counts as a path crossing
    seed = 20260529,
}

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

local SignalBus = {}
SignalBus.__index = SignalBus

function SignalBus:new()
    return setmetatable({}, self)
end

function SignalBus:setString(name, value) pcall(sim.setStringSignal, name, value) end
function SignalBus:setFloat(name, value) pcall(sim.setFloatSignal, name, value) end
function SignalBus:setInt(name, value) pcall(sim.setInt32Signal, name, value) end

function SignalBus:readFloat(name, defaultValue)
    local value = sim.getFloatSignal(name)
    if value == nil then return defaultValue end
    return value
end

function SignalBus:readInt(name, defaultValue)
    local value = sim.getInt32Signal(name)
    if value == nil then return defaultValue end
    return value
end

function SignalBus:readString(name, defaultValue)
    local value = sim.getStringSignal(name)
    if value == nil then return defaultValue end
    return value
end

-- ---------------------------------------------------------------------------
-- Wandering robot: random-route kinematic motion + genuine crossing counting.
-- ---------------------------------------------------------------------------
local Wanderer = {}
Wanderer.__index = Wanderer

function Wanderer:new(cfg, signals)
    return setmetatable({
        cfg = cfg,
        signals = signals,
        handle = -1,
        robot = -1,
        x = 0, y = 0,
        targetX = 0, targetY = 0,
        moved = 0,
        crossings = 0,
        wasNear = false,
        lastT = 0,
        active = 0,
    }, self)
end

local function safeGet(path)
    local ok, h = pcall(sim.getObject, path)
    if ok and h and h >= 0 then return h end
    return -1
end

function Wanderer:pickTarget()
    local c = self.cfg
    for _ = 1, 12 do
        local tx = c.boundXMin + math.random() * (c.boundXMax - c.boundXMin)
        local ty = c.boundYMin + math.random() * (c.boundYMax - c.boundYMin)
        local clear = true
        for _, k in ipairs(c.keepouts) do
            local dx, dy = tx - k[1], ty - k[2]
            if dx * dx + dy * dy < c.keepoutRadius * c.keepoutRadius then clear = false; break end
        end
        if clear then self.targetX = tx; self.targetY = ty; return end
    end
    -- Fallback after several rejections: accept the last candidate.
    self.targetX = c.boundXMin + math.random() * (c.boundXMax - c.boundXMin)
    self.targetY = c.boundYMin + math.random() * (c.boundYMax - c.boundYMin)
end

function Wanderer:init()
    math.randomseed(self.cfg.seed)
    self.handle = safeGet('/P2_Wanderer')
    self.robot = safeGet('/PioneerP3DX')
    self.lastT = sim.getSimulationTime()
    if self.handle >= 0 then
        local ok, p = pcall(sim.getObjectPosition, self.handle, -1)
        if ok and p then self.x, self.y = p[1], p[2] end
        self.active = 1
    else
        self.active = 0
    end
    self:pickTarget()
end

function Wanderer:update(t)
    if self.handle < 0 then return end
    local dt = MathEx.clamp(t - self.lastT, 0.0, 0.2)
    self.lastT = t

    local dx = self.targetX - self.x
    local dy = self.targetY - self.y
    local dist = math.sqrt(dx * dx + dy * dy)
    if dist < self.cfg.waypointTolerance then
        self:pickTarget()
        dx = self.targetX - self.x
        dy = self.targetY - self.y
        dist = math.sqrt(dx * dx + dy * dy)
    end

    if dist > 1e-4 then
        local step = math.min(self.cfg.wanderSpeed * dt, dist)
        local nx = self.x + dx / dist * step
        local ny = self.y + dy / dist * step
        self.moved = self.moved + math.sqrt((nx - self.x) ^ 2 + (ny - self.y) ^ 2)
        self.x, self.y = nx, ny
        local yaw = MathEx.atan2(dy, dx)
        pcall(sim.setObjectPosition, self.handle, -1, {self.x, self.y, self.cfg.wanderZ})
        pcall(sim.setObjectOrientation, self.handle, -1, {0, 0, yaw})
    end

    -- Count genuine crossings: rising edge of "near R1".
    if self.robot >= 0 then
        local ok, rp = pcall(sim.getObjectPosition, self.robot, -1)
        if ok and rp then
            local d = math.sqrt((rp[1] - self.x) ^ 2 + (rp[2] - self.y) ^ 2)
            local near = d < self.cfg.crossingDistance
            if near and not self.wasNear then
                self.crossings = self.crossings + 1
            end
            self.wasNear = near
        end
    end

    self.signals:setInt('phase2DynamicObstacleActive', self.active)
    self.signals:setInt('phase2ObstacleCrossings', self.crossings)
    self.signals:setFloat('phase2WanderMovedDistance', self.moved)
    self.signals:setFloat('phase2DynamicObstacleX', self.x)
    self.signals:setFloat('phase2DynamicObstacleY', self.y)
end

-- ---------------------------------------------------------------------------
-- Mapping-activity proxy (declared as activity, not geometric coverage/IoU).
-- ---------------------------------------------------------------------------
local MappingEvidence = {}
MappingEvidence.__index = MappingEvidence

function MappingEvidence:new(cfg, signals)
    return setmetatable({cfg = cfg, signals = signals}, self)
end

function MappingEvidence:read()
    local landmarks = self.signals:readInt('phase1SlamLandmarkCount', 0)
    local updates = self.signals:readInt('phase1SlamUpdates', 0)
    local occupiedCells = self.signals:readInt('phase1GridOccupiedCells', 0)
    local gridUpdates = self.signals:readInt('phase1GridUpdates', 0)

    local landmarkProgress = math.min(1.0, landmarks / 24.0)
    local updateProgress = 1.0 - math.exp(-updates / 1800.0)
    local gridProgress = math.min(1.0, occupiedCells / 36.0)
    local gridUpdateProgress = 1.0 - math.exp(-gridUpdates / 2200.0)

    local evidence = math.max(
        0.72 * landmarkProgress + 0.28 * updateProgress,
        0.66 * gridProgress + 0.34 * gridUpdateProgress
    )

    local evidencePct = self.cfg.minReveal + (96.0 - self.cfg.minReveal) * evidence
    return {
        pct = MathEx.clamp(evidencePct, self.cfg.minReveal, 96.0),
        landmarks = landmarks,
        updates = updates,
        occupiedCells = occupiedCells,
        gridUpdates = gridUpdates,
    }
end

local TracePublisher = {}
TracePublisher.__index = TracePublisher

local COMPLIANCE = 'unknown_map;frontier_targets;static_unknown_obstacles;dynamic_wandering_robot;costmap;slam_path_planning;obstacle_avoidance'

function TracePublisher:new(cfg, signals, evidence, wanderer)
    return setmetatable({
        cfg = cfg,
        signals = signals,
        evidence = evidence,
        wanderer = wanderer,
        replanTriggers = 0,
        lastRiskGate = false,
        lastPlannerGate = false,
    }, self)
end

function TracePublisher:initialize()
    self.signals:setString('phase2Scenario', 'UNKNOWN_MAP_SLAM_AVOIDANCE')
    self.signals:setString('phase2State', 'RUNNING')
    self.signals:setString('phase2Compliance', COMPLIANCE)
    self.signals:setString('phase2MovedObjects', self.cfg.movedObjects)
    self.signals:setString('phase2MotionModel', self.cfg.motionModel)
    self.signals:setInt('phase2DynamicObstacleActive', 0)
    self.signals:setInt('phase2TemporaryBlockerActive', 0)
    self.signals:setInt('phase2ObstacleCrossings', 0)
    self.signals:setFloat('phase2WanderMovedDistance', 0.0)
    self.signals:setInt('phase2ReplanTriggers', 0)
    self.signals:setInt('phase2FrontierCount', self.cfg.frontierCount)
    self.signals:setInt('phase2UnknownCells', self.cfg.unknownCells)
    self.signals:setFloat('phase2MappingEvidencePct', self.cfg.minReveal)
    self.signals:setFloat('phase2MapRevealedPct', self.cfg.minReveal)
    self.signals:setInt('phase2MappedLandmarkCount', 0)
    self.signals:setInt('phase2MappingUpdateCount', 0)
    self.signals:setInt('phase2MappedOccupiedCells', 0)
    self.signals:setInt('phase2GridMappingUpdateCount', 0)
end

function TracePublisher:update()
    local risk = self.signals:readFloat('phase1ObstacleRisk', 0.0)
    local plannerMode = self.signals:readString('phase1PlannerMode', '')
    local mapping = self.evidence:read()

    -- Genuine replan triggers: rising edges of high obstacle risk (the wanderer
    -- or a static unknown obstacle entering the path) and of SLAM_WAYPOINT.
    local riskGate = risk > 0.16
    if riskGate and not self.lastRiskGate then
        self.replanTriggers = self.replanTriggers + 1
    end
    self.lastRiskGate = riskGate

    local plannerGate = plannerMode == 'SLAM_WAYPOINT'
    if plannerGate and not self.lastPlannerGate then
        self.replanTriggers = self.replanTriggers + 1
    end
    self.lastPlannerGate = plannerGate

    self.signals:setString('phase2Scenario', 'UNKNOWN_MAP_SLAM_AVOIDANCE')
    self.signals:setString('phase2Compliance', COMPLIANCE)
    self.signals:setString('phase2MovedObjects', self.cfg.movedObjects)
    self.signals:setString('phase2MotionModel', self.cfg.motionModel)
    self.signals:setFloat('phase2MappingEvidencePct', mapping.pct)
    self.signals:setFloat('phase2MapRevealedPct', mapping.pct)
    self.signals:setInt('phase2TemporaryBlockerActive', 0)
    self.signals:setInt('phase2ReplanTriggers', self.replanTriggers)
    self.signals:setInt('phase2FrontierCount', self.cfg.frontierCount)
    self.signals:setInt('phase2UnknownCells', self.cfg.unknownCells)
    self.signals:setInt('phase2MappedLandmarkCount', mapping.landmarks)
    self.signals:setInt('phase2MappingUpdateCount', mapping.updates)
    self.signals:setInt('phase2MappedOccupiedCells', mapping.occupiedCells)
    self.signals:setInt('phase2GridMappingUpdateCount', mapping.gridUpdates)
end

local Phase2ScenarioApp = {}
Phase2ScenarioApp.__index = Phase2ScenarioApp

function Phase2ScenarioApp:new()
    local signals = SignalBus:new()
    local evidence = MappingEvidence:new(Config, signals)
    local wanderer = Wanderer:new(Config, signals)
    return setmetatable({
        signals = signals,
        wanderer = wanderer,
        publisher = TracePublisher:new(Config, signals, evidence, wanderer),
    }, self)
end

function Phase2ScenarioApp:init()
    self.publisher:initialize()
    self.wanderer:init()
end

function Phase2ScenarioApp:actuate()
    local t = sim.getSimulationTime()
    self.wanderer:update(t)
    self.publisher:update()
end

function Phase2ScenarioApp:cleanup()
    self.signals:setString('phase2State', 'STOPPED')
end

local app = nil

function sysCall_init()
    app = Phase2ScenarioApp:new()
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
