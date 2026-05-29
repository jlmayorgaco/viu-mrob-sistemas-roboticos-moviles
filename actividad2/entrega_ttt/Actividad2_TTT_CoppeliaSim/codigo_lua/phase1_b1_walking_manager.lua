-- VIU SRM - Task 2 Phase 1
-- B1 walking manager. Bill moves between two worktables and publishes
-- station/action signals for R1.

sim = require('sim')

local Config = {
    speed = 0.360,
    gaitReferenceSpeed = 0.360,
    gaitPhaseRate = 10.2,
    z = 0.0,
    workPauseWs1 = 8.0,
    workPauseWs2 = 10.0,
    logPeriod = 1.5,
}

local Routes = {
    WS1_TO_WS2 = {
        {x = -2.12, y = 1.10},
        {x = -1.50, y = 1.10},
        {x = -1.50, y = -1.60},
        {x = -0.40, y = -1.60},
        {x = 0.80, y = -1.60},
        {x = 2.12, y = -1.10},
    },
    WS2_TO_WS1 = {
        {x = 2.12, y = -1.10},
        {x = 1.50, y = -1.10},
        {x = 1.50, y = 1.10},
        {x = 0.70, y = 1.10},
        {x = -0.70, y = 1.10},
        {x = -2.12, y = 1.10},
    },
}

local Stations = {
    WS1 = {
        state = 'WORKING_WS1',
        station = 'WS1',
        tableName = 'WORKTABLE_1',
        requestTool = 'T1',
        pose = {x = -2.12, y = 1.10},
        tablePose = {x = -2.12, y = 1.76},
        pause = Config.workPauseWs1,
        returnedSignal = 'phase1Tool1Returned',
        walkAction = 'WALKING_TO_WS2',
        transitState = 'TRANSIT_TO_WS2',
        route = Routes.WS1_TO_WS2,
    },
    WS2 = {
        state = 'WORKING_WS2',
        station = 'WS2',
        tableName = 'WORKTABLE_2',
        requestTool = 'T2',
        pose = {x = 2.12, y = -1.10},
        tablePose = {x = 2.12, y = -1.76},
        pause = Config.workPauseWs2,
        returnedSignal = 'phase1Tool2Returned',
        walkAction = 'WALKING_TO_WS1',
        transitState = 'TRANSIT_TO_WS1',
        route = Routes.WS2_TO_WS1,
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

function MathEx.distance2d(a, b)
    local dx = b.x - a.x
    local dy = b.y - a.y
    return math.sqrt(dx * dx + dy * dy)
end

function MathEx.yawToFacePoint(fromPoint, toPoint)
    return MathEx.atan2(toPoint.y - fromPoint.y, toPoint.x - fromPoint.x)
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

function SignalBus:readString(name, defaultValue)
    local value = sim.getStringSignal(name)
    if value == nil then return defaultValue end
    return value
end

function SignalBus:publish(state, action, movedDistance, speed, handle)
    local p = {0, 0, 0}
    if handle >= 0 then p = sim.getObjectPosition(handle, -1) end

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

    sim.setStringSignal('phase1B1State', state)
    sim.setStringSignal('phase1B1Station', station)
    sim.setStringSignal('phase1B1WorkTable', tableName)
    sim.setStringSignal('phase1B1RequestTool', requestTool)
    sim.setStringSignal('phase1B1Action', action)
    sim.setInt32Signal('phase1B1AtWs1', atWs1)
    sim.setInt32Signal('phase1B1AtWs2', atWs2)
    sim.setFloatSignal('phase1B1Speed', speed or 0)
    sim.setFloatSignal('phase1B1X', p[1] or 0)
    sim.setFloatSignal('phase1B1Y', p[2] or 0)
    sim.setFloatSignal('phase1B1MovedDistance', movedDistance)
end

local BillBody = {}
BillBody.__index = BillBody

function BillBody:new(cfg)
    return setmetatable({cfg = cfg, handle = -1, lastPosition = nil, movedDistance = 0}, self)
end

function BillBody:resolve()
    self.handle = safeGetObject('/B1')
end

function BillBody:setPose(x, y, yaw)
    if self.handle >= 0 then
        sim.setObjectPosition(self.handle, {x, y, self.cfg.z})
        sim.setObjectOrientation(self.handle, {0, 0, yaw})
    end

    if self.lastPosition then
        local dx = x - self.lastPosition[1]
        local dy = y - self.lastPosition[2]
        self.movedDistance = self.movedDistance + math.sqrt(dx * dx + dy * dy)
    end
    self.lastPosition = {x, y}
end

function BillBody:setAtStation(station)
    self:setPose(station.pose.x, station.pose.y, MathEx.yawToFacePoint(station.pose, station.tablePose))
end

local JointAnimator = {}
JointAnimator.__index = JointAnimator

function JointAnimator:new()
    return setmetatable({joints = {}, phase = 0}, self)
end

function JointAnimator:register(key, path)
    local handle = safeGetObject(path)
    if handle >= 0 then self.joints[key] = handle end
end

function JointAnimator:load()
    self:register('leftLeg', '/B1/leftLegJoint')
    self:register('rightLeg', '/B1/rightLegJoint')
    self:register('leftKnee', '/B1/leftKneeJoint')
    self:register('rightKnee', '/B1/rightKneeJoint')
    self:register('leftShoulder', '/B1/leftShoulderJoint')
    self:register('rightShoulder', '/B1/rightShoulderJoint')
    self:register('leftElbow', '/B1/leftElbowJoint')
    self:register('rightElbow', '/B1/rightElbowJoint')
end

function JointAnimator:setTarget(key, target)
    local handle = self.joints[key]
    if handle then
        pcall(sim.setJointTargetPosition, handle, target)
        pcall(sim.setJointPosition, handle, target)
    end
end

function JointAnimator:setTargets(targets)
    for key, value in pairs(targets) do
        self:setTarget(key, value)
    end
end

function JointAnimator:actionContains(action, text)
    return string.find(action, text, 1, true) ~= nil
end

function JointAnimator:tableWorkPose(action, state)
    local t = self.phase
    local slow   = math.sin(t * 0.50)
    local altL   = math.sin(t)
    local altR   = math.sin(t + math.pi)
    local tapL   = math.sin(t * 1.4)
    local tapR   = math.sin(t * 1.4 + math.pi)

    local pose = {
        leftLeg = 0,
        rightLeg = 0,
        leftKnee = 0,
        rightKnee = 0,
        leftShoulder = 0,
        rightShoulder = 0,
        leftElbow = 0,
        rightElbow = 0,
    }

    if self:actionContains(action, 'READY_TO_TAKE') or self:actionContains(action, 'TAKING') then
        pose.leftShoulder  =  0.70 + 0.04 * altL
        pose.rightShoulder =  0.68 + 0.04 * altR
        pose.leftElbow     =  0.28 + 0.04 * math.abs(tapL)
        pose.rightElbow    =  0.26 + 0.04 * math.abs(tapR)
        pose.leftKnee      =  0.05
        pose.rightKnee     =  0.05
    elseif self:actionContains(action, 'WORKING') then
        pose.leftShoulder  =  0.72 + 0.06 * altL
        pose.rightShoulder =  0.70 + 0.06 * altR
        pose.leftElbow     =  0.38 + 0.06 * math.abs(tapL)
        pose.rightElbow    =  0.36 + 0.06 * math.abs(tapR)
        pose.leftKnee      =  0.06 + 0.02 * math.abs(slow)
        pose.rightKnee     =  0.06 + 0.02 * math.abs(slow)
    elseif self:actionContains(action, 'GIVING') then
        pose.leftShoulder  =  0.74 + 0.03 * altL
        pose.rightShoulder =  0.20 + 0.03 * slow
        pose.leftElbow     =  0.20 + 0.03 * math.abs(tapL)
        pose.rightElbow    =  0.14
        pose.leftKnee      =  0.03
        pose.rightKnee     =  0.03
    elseif StationByState[state] then
        pose.leftShoulder  =  0.18 + 0.04 * altL
        pose.rightShoulder =  0.18 + 0.04 * altR
        pose.leftElbow     =  0.10 + 0.02 * math.abs(tapL)
        pose.rightElbow    =  0.10 + 0.02 * math.abs(tapR)
    end

    return pose
end

function JointAnimator:animateAtTable(dt, action, state)
    self.phase = self.phase + dt * 2.8
    self:setTargets(self:tableWorkPose(action, state))
end

function JointAnimator:animateWalking(dt, speed, action, state)
    if speed <= 0.001 then
        self:animateAtTable(dt, action, state)
        return
    end

    local speedScale = MathEx.clamp(speed / Config.gaitReferenceSpeed, 0.65, 1.35)
    self.phase = self.phase + dt * Config.gaitPhaseRate * speedScale
    local step = math.sin(self.phase)
    self:setTargets({
        leftLeg = step * 0.30,
        rightLeg = -step * 0.30,
        leftKnee = math.max(0, step) * 0.38,
        rightKnee = math.max(0, -step) * 0.38,
        leftShoulder = -0.08 + math.sin(self.phase + math.pi) * 0.10,
        rightShoulder = -0.08 - math.sin(self.phase + math.pi) * 0.10,
        leftElbow = 0.08 + math.max(0, -step) * 0.06,
        rightElbow = 0.08 + math.max(0, step) * 0.06,
    })
end

local RouteWalker = {}
RouteWalker.__index = RouteWalker

function RouteWalker:new(cfg, body)
    return setmetatable({cfg = cfg, body = body, route = {}, index = 1, segmentU = 0}, self)
end

function RouteWalker:start(station)
    self.route = station.route
    self.index = 1
    self.segmentU = 0
end

function RouteWalker:update()
    local a = self.route[self.index]
    local b = self.route[self.index + 1]
    if not a or not b then
        return false, 0
    end

    return true, a, b
end

function RouteWalker:advance(dt)
    local active, a, b = self:update()
    if not active then
        return false, 0
    end

    local segmentLength = math.max(0.001, MathEx.distance2d(a, b))
    self.segmentU = self.segmentU + self.cfg.speed * dt / segmentLength

    while self.segmentU >= 1.0 do
        self.segmentU = self.segmentU - 1.0
        self.index = self.index + 1
        active, a, b = self:update()
        if not active then
            return false, 0
        end
        segmentLength = math.max(0.001, MathEx.distance2d(a, b))
    end

    local dx = b.x - a.x
    local dy = b.y - a.y
    self.body:setPose(a.x + dx * self.segmentU, a.y + dy * self.segmentU, MathEx.atan2(dy, dx))
    return true, self.cfg.speed
end

local B1Manager = {}
B1Manager.__index = B1Manager

function B1Manager:new()
    local body = BillBody:new(Config)
    return setmetatable({
        body = body,
        signals = SignalBus:new(),
        animator = JointAnimator:new(),
        walker = RouteWalker:new(Config, body),
        state = Stations.WS1.state,
        stateStartT = 0,
        lastT = -1,
        currentAction = 'WAITING_FOR_T1',
        lastLogT = -1000,
    }, self)
end

function B1Manager:startTransit(station)
    self.state = station.transitState
    self.walker:start(station)
    self.stateStartT = sim.getSimulationTime()
    self.currentAction = station.walkAction
end

function B1Manager:arriveFromTransit()
    local station = ArrivalByTransitState[self.state] or Stations.WS1
    self.state = station.state
    self.stateStartT = sim.getSimulationTime()
    self.body:setAtStation(station)
    return 0
end

function B1Manager:updateTransit(dt)
    local active, speed = self.walker:advance(dt)
    if not active then
        return self:arriveFromTransit()
    end
    return speed
end

function B1Manager:updateWorkingAt(station, t)
    self.body:setAtStation(station)
    if t - self.stateStartT >= station.pause
        and self.signals:readInt(station.returnedSignal, 0) == 1 then
        self:startTransit(station)
        return Config.speed
    end
    return 0
end

function B1Manager:update(dt)
    local t = sim.getSimulationTime()
    self.currentAction = self.signals:readString('phase1B1ToolActionCommand', self.currentAction)

    local station = StationByState[self.state]
    if station then
        return self:updateWorkingAt(station, t)
    end

    return self:updateTransit(dt)
end

function B1Manager:publish(speed)
    self.signals:publish(self.state, self.currentAction, self.body.movedDistance, speed, self.body.handle)
end

function B1Manager:reset()
    self.state = Stations.WS1.state
    self.walker.route = {}
    self.walker.index = 1
    self.walker.segmentU = 0
    self.body.movedDistance = 0
    self.animator.phase = 0
    self.lastT = sim.getSimulationTime()
    self.stateStartT = self.lastT
    self.body.lastPosition = {Stations.WS1.pose.x, Stations.WS1.pose.y}
    self.currentAction = 'WAITING_FOR_T1'
    self.body:setAtStation(Stations.WS1)
end

function B1Manager:init()
    self.body:resolve()
    self.animator:load()
    self:reset()
    self:publish(0)
    sim.addLog(sim.verbosity_scriptinfos, 'Phase1 B1 configured: working between WorkTable 1 and WorkTable 2.')
end

function B1Manager:actuate()
    if self.body.handle < 0 then
        self:publish(0)
        return
    end

    local t = sim.getSimulationTime()
    local dt = MathEx.clamp(t - self.lastT, 0.0, 0.12)
    self.lastT = t

    local speed = self:update(dt)
    self.animator:animateWalking(dt, speed, self.currentAction, self.state)
    self:publish(speed)

    if t - self.lastLogT >= Config.logPeriod then
        sim.addLog(
            sim.verbosity_scriptinfos,
            string.format(
                'Phase1 B1 state=%s station=%s action=%s moved=%.2f m',
                self.state,
                sim.getStringSignal('phase1B1Station') or 'NONE',
                self.currentAction,
                self.body.movedDistance
            )
        )
        self.lastLogT = t
    end
end

function B1Manager:cleanup()
    self:publish(0)
end

local app = nil

function sysCall_init()
    app = B1Manager:new()
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
