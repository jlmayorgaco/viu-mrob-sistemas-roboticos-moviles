-- VIU SRM - Actividad 2.1
-- Bill walking-room manager.
-- Bill walks a circular trajectory only. His tangential speed follows a
-- smooth acceleration/deceleration profile and then he stops at the start.

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
    baseSpeed = 0.22,
    speedAmplitude = 0.09,
    speedCycles = 4,
    laps = 2,
    z = 0.0,
    logPeriod = 1.2,
    circleRadius = 1.55,
    startAngle = math.pi / 4.0,
    gaitReferenceSpeed = 0.22,
    gaitPhaseRate = 8.8,
    maxTurnRate = 1.35,
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

    -- d(theta)/dt = baseOmega - ampOmega*cos(profileOmega*t). This starts
    -- slow, accelerates smoothly, decelerates smoothly, and integrates exactly
    -- to the requested number of complete laps when speedCycles is integer.
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
            sim.setJointTargetPosition(h, 0)
        end
        return
    end

    local speedScale = clamp(speed / cfg.gaitReferenceSpeed, 0.45, 1.35)
    walkPhase = walkPhase + dt * cfg.gaitPhaseRate * speedScale

    local swing = math.sin(walkPhase)
    local oppositeSwing = -swing
    local stance = math.cos(walkPhase)
    local leftKnee = math.max(0, -swing) * 0.38 + math.max(0, stance) * 0.05
    local rightKnee = math.max(0, swing) * 0.38 + math.max(0, -stance) * 0.05
    local leftHip = swing * 0.28 - 0.04
    local rightHip = oppositeSwing * 0.28 - 0.04
    local leftShoulder = oppositeSwing * 0.18
    local rightShoulder = swing * 0.18
    local leftAnkle = -leftKnee * 0.34
    local rightAnkle = -rightKnee * 0.34
    local leftElbow = math.max(0, swing) * 0.12
    local rightElbow = math.max(0, oppositeSwing) * 0.12

    if joints.leftLeg then sim.setJointTargetPosition(joints.leftLeg, leftHip) end
    if joints.rightLeg then sim.setJointTargetPosition(joints.rightLeg, rightHip) end
    if joints.leftKnee then sim.setJointTargetPosition(joints.leftKnee, leftKnee) end
    if joints.rightKnee then sim.setJointTargetPosition(joints.rightKnee, rightKnee) end
    if joints.leftAnkle then sim.setJointTargetPosition(joints.leftAnkle, leftAnkle) end
    if joints.rightAnkle then sim.setJointTargetPosition(joints.rightAnkle, rightAnkle) end
    if joints.leftShoulder then sim.setJointTargetPosition(joints.leftShoulder, leftShoulder) end
    if joints.rightShoulder then sim.setJointTargetPosition(joints.rightShoulder, rightShoulder) end
    if joints.leftElbow then sim.setJointTargetPosition(joints.leftElbow, leftElbow) end
    if joints.rightElbow then sim.setJointTargetPosition(joints.rightElbow, rightElbow) end
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
    sim.addLog(sim.verbosity_scriptinfos, 'Bill circular path ready: two laps with smooth acceleration/deceleration, then full stop.')
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
