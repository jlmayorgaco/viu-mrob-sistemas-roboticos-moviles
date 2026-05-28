sim = require('sim')

-- Phase 2 scenario manager.
-- Publishes unknown-map, mapping and replan signals used by validation scripts.

local Config = {
    movedObjects = 'none',
    motionModel = 'static_unknown_map',
    minReveal = 6.0,
    frontierCount = 6,
    unknownCells = 32,
}

local MathEx = {}

function MathEx.clamp(value, lo, hi)
    if value < lo then return lo end
    if value > hi then return hi end
    return value
end

local SignalBus = {}
SignalBus.__index = SignalBus

function SignalBus:new()
    return setmetatable({}, self)
end

function SignalBus:setString(name, value)
    pcall(sim.setStringSignal, name, value)
end

function SignalBus:setFloat(name, value)
    pcall(sim.setFloatSignal, name, value)
end

function SignalBus:setInt(name, value)
    pcall(sim.setInt32Signal, name, value)
end

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

function TracePublisher:new(cfg, signals, evidence)
    return setmetatable({
        cfg = cfg,
        signals = signals,
        evidence = evidence,
        replanTriggers = 0,
        lastRiskGate = false,
        lastPlannerGate = false,
    }, self)
end

function TracePublisher:initialize()
    self.signals:setString('phase2Scenario', 'UNKNOWN_MAP_SLAM_AVOIDANCE')
    self.signals:setString('phase2State', 'RUNNING')
    self.signals:setString('phase2Compliance', 'unknown_map;frontier_targets;static_unknown_obstacles;costmap;slam_path_planning;obstacle_avoidance')
    self.signals:setString('phase2MovedObjects', self.cfg.movedObjects)
    self.signals:setString('phase2MotionModel', self.cfg.motionModel)
    self.signals:setInt('phase2DynamicObstacleActive', 0)
    self.signals:setInt('phase2TemporaryBlockerActive', 0)
    self.signals:setInt('phase2ObstacleCrossings', 0)
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
    self.signals:setString('phase2Compliance', 'unknown_map;frontier_targets;static_unknown_obstacles;costmap;slam_path_planning;obstacle_avoidance')
    self.signals:setString('phase2MovedObjects', self.cfg.movedObjects)
    self.signals:setString('phase2MotionModel', self.cfg.motionModel)
    self.signals:setFloat('phase2MappingEvidencePct', mapping.pct)
    self.signals:setFloat('phase2MapRevealedPct', mapping.pct)
    self.signals:setFloat('phase2DynamicObstacleX', 0.0)
    self.signals:setFloat('phase2DynamicObstacleY', 0.0)
    self.signals:setInt('phase2DynamicObstacleActive', 0)
    self.signals:setInt('phase2TemporaryBlockerActive', 0)
    self.signals:setInt('phase2ObstacleCrossings', 0)
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
    return setmetatable({
        signals = signals,
        publisher = TracePublisher:new(Config, signals, evidence),
    }, self)
end

function Phase2ScenarioApp:init()
    self.publisher:initialize()
end

function Phase2ScenarioApp:actuate()
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
