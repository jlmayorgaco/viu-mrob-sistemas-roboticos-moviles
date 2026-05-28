-- VIU SRM - Actividad 2.1
-- Bill walking-room manager.
-- Bill keeps a circular walk in the follower room, then stops at the start.
-- The speed profile includes acceleration and braking for controller tests.

sim = require('sim')

local bill = -1
local joints = {}
local stopped = false
local lastT = -1
local startT = 0
local walkPhase = 0
local currentState = 'WALKING'
local currentSpeed = 0
local currentYaw = 0
local totalPathTime = 0
local profileOmega = 0
local finalPosition = nil
local finalYaw = 0
local lapProgress = 0

local cfg = {
    baseSpeed = 0.42,
    speedAmplitude = 0.12,
    speedCycles = 4,
    laps = 2,
    z = 0.0,
    logPeriod = 1.2,
    circleRadius = 2.05,
    startAngle = math.pi / 4.0,
    gaitReferenceSpeed = 0.42,
    gaitPhaseRate = 10.8,
    maxTurnRate = 1.85,
}

local lastLogT = -1000

local function clamp(value, lo, hi)
    if value < lo then return lo end
    if value > hi then return hi end
    return value
end

local function normalizeAngle(angle)
    while angle > math.pi do angle = angle - 2.0 * math.pi end
    while angle < -math.pi do angle = angle + 2.0 * math.pi end
    return angle
end

local function approachAngle(current, target, maxStep)
    local delta = normalizeAngle(target - current)
    delta = clamp(delta, -maxStep, maxStep)
    return normalizeAngle(current + delta)
end

local function safeGetObject(path)
    local ok, handle = pcall(sim.getObject, path)
    if ok and handle and handle >= 0 then return handle end
    return -1
end

local function registerJoint(key, path)
    local h = safeGetObject(path)
    if h >= 0 then joints[key] = h end
end

local function setJointPose(handle, value)
    if handle then
        pcall(sim.setJointTargetPosition, handle, value)
        pcall(sim.setJointPosition, handle, value)
    end
end

local function publish(state, speed)
    sim.setStringSignal('billPathState', state)
    sim.setFloatSignal('billSpeed', speed or 0)
    sim.setFloatSignal('billLapProgress', lapProgress)
    sim.setInt32Signal('billStopped', stopped and 1 or 0)
end

local function configureCircleTiming()
    local circumference = 2.0 * math.pi * cfg.circleRadius
    totalPathTime = circumference * cfg.laps / cfg.baseSpeed
    profileOmega = 2.0 * math.pi * cfg.speedCycles / totalPathTime
    finalPosition = {
        cfg.circleRadius * math.cos(cfg.startAngle),
        cfg.circleRadius * math.sin(cfg.startAngle),
        cfg.z,
    }
    finalYaw = normalizeAngle(cfg.startAngle + 2.0 * math.pi * cfg.laps + math.pi / 2.0)
end

local function circlePoseAt(elapsed)
    if elapsed >= totalPathTime then
        lapProgress = 1.0
        return finalPosition, finalYaw, 'STOPPED', 0
    end

    local t = clamp(elapsed, 0.0, totalPathTime)
    local baseOmega = cfg.baseSpeed / cfg.circleRadius
    local ampOmega = cfg.speedAmplitude / cfg.circleRadius

    -- Keep the math explicit: the speed wave starts soft and still closes the
    -- circle exactly when speedCycles is an integer.
    local theta = cfg.startAngle + baseOmega * t - (ampOmega / profileOmega) * math.sin(profileOmega * t)
    local speed = cfg.baseSpeed - cfg.speedAmplitude * math.cos(profileOmega * t)
    speed = clamp(speed, cfg.baseSpeed - cfg.speedAmplitude, cfg.baseSpeed + cfg.speedAmplitude)
    lapProgress = t / totalPathTime

    local p = {
        cfg.circleRadius * math.cos(theta),
        cfg.circleRadius * math.sin(theta),
        cfg.z,
    }
    local yaw = normalizeAngle(theta + math.pi / 2.0)
    return p, yaw, 'WALKING', speed
end

local function animateWalking(dt, speed)
    if speed <= 0.001 then
        for _, h in pairs(joints) do
            setJointPose(h, 0)
        end
        return
    end

    local speedScale = clamp(speed / cfg.gaitReferenceSpeed, 0.55, 1.45)
    walkPhase = walkPhase + dt * cfg.gaitPhaseRate * speedScale

    local step = math.sin(walkPhase)
    local leftKnee = math.max(0, step) * 0.34
    local rightKnee = math.max(0, -step) * 0.34
    local leftHip = step * 0.25
    local rightHip = -step * 0.25
    local leftShoulder = -0.08 - step * 0.10
    local rightShoulder = -0.08 + step * 0.10
    local leftElbow = 0.06 + math.max(0, -step) * 0.07
    local rightElbow = 0.06 + math.max(0, step) * 0.07

    setJointPose(joints.leftLeg, leftHip)
    setJointPose(joints.rightLeg, rightHip)
    setJointPose(joints.leftKnee, leftKnee)
    setJointPose(joints.rightKnee, rightKnee)
    setJointPose(joints.leftAnkle, 0)
    setJointPose(joints.rightAnkle, 0)
    setJointPose(joints.leftShoulder, leftShoulder)
    setJointPose(joints.rightShoulder, rightShoulder)
    setJointPose(joints.leftElbow, leftElbow)
    setJointPose(joints.rightElbow, rightElbow)
end

local function logPath(state, speed)
    local t = sim.getSimulationTime()
    if t - lastLogT >= cfg.logPeriod then
        local lap = math.min(cfg.laps, math.floor(lapProgress * cfg.laps) + 1)
        sim.addLog(
            sim.verbosity_scriptinfos,
            string.format('Bill circle state=%s lap=%d/%d speed=%.2f progress=%.1f%%', state, lap, cfg.laps, speed, 100.0 * lapProgress)
        )
        lastLogT = t
    end
end

function sysCall_init()
    bill = safeGetObject('/Bill')
    registerJoint('leftLeg', '/Bill/leftLegJoint')
    registerJoint('rightLeg', '/Bill/rightLegJoint')
    registerJoint('leftKnee', '/Bill/leftKneeJoint')
    registerJoint('rightKnee', '/Bill/rightKneeJoint')
    registerJoint('leftAnkle', '/Bill/leftAnkleJoint')
    registerJoint('rightAnkle', '/Bill/rightAnkleJoint')
    registerJoint('leftShoulder', '/Bill/leftShoulderJoint')
    registerJoint('rightShoulder', '/Bill/rightShoulderJoint')
    registerJoint('leftElbow', '/Bill/leftElbowJoint')
    registerJoint('rightElbow', '/Bill/rightElbowJoint')

    stopped = false
    walkPhase = 0
    currentState = 'WALKING'
    configureCircleTiming()
    startT = sim.getSimulationTime()
    lastT = sim.getSimulationTime()

    local p, yaw, state, speed = circlePoseAt(0)
    currentYaw = yaw
    currentSpeed = speed
    currentState = state

    if bill >= 0 then
        sim.setObjectPosition(bill, p)
        sim.setObjectOrientation(bill, {0, 0, currentYaw})
    end

    publish(currentState, currentSpeed)
    sim.addLog(sim.verbosity_scriptinfos, 'Bill circular path ready: two laps with variable speed, then stop.')
end

function sysCall_actuation()
    if bill < 0 then
        publish('ERROR_BILL_HANDLE', 0)
        return
    end

    local t = sim.getSimulationTime()
    local rawDt = t - lastT
    if rawDt <= 0.000001 then
        publish(currentState, currentSpeed)
        return
    end
    local dt = clamp(rawDt, 0.0, 0.12)
    lastT = t

    local elapsed = math.max(0, t - startT)
    local p, yaw, state, speed = circlePoseAt(elapsed)

    stopped = state == 'STOPPED'
    currentYaw = approachAngle(currentYaw, yaw, cfg.maxTurnRate * dt)
    sim.setObjectPosition(bill, p)
    sim.setObjectOrientation(bill, {0, 0, currentYaw})

    animateWalking(dt, speed)
    currentState = state
    currentSpeed = speed
    publish(currentState, currentSpeed)
    logPath(state, speed)
end

function sysCall_cleanup()
    stopped = true
    currentState = 'STOPPED'
    currentSpeed = 0
    lapProgress = 1.0
    publish(currentState, currentSpeed)
    animateWalking(0.05, 0)
end
