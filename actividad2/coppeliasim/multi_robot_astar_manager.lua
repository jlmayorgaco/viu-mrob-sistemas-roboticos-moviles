-- VIU SRM - Actividad 2
-- Cooperative multi-robot A* fleet manager.
-- Adds three AMR agents with time-reserved A* paths, battery drain,
-- charging return and recharge cycles.

sim = require('sim')

local cfg = {
    originX = -2.18,
    originY = -2.20,
    cell = 0.38,
    z = 0.18,
    gridW = 12,
    gridH = 12,
    movePeriod = 0.34,
    lowBattery = 45.0,
    readyBattery = 78.0,
    fullBattery = 86.0,
    idleDrain = 0.035,
    moveDrain = 2.65,
    chargeRate = 12.0,
    maxSearchT = 72,
    publishPeriod = 0.5,
}

local robots = {
    {
        id = 'R1',
        alias = 'VIU_Fleet_Robot_1',
        start = {x = 2, y = 2},
        charger = {x = 2, y = 2},
        goal = {x = 10, y = 10},
        battery = 82.0,
    },
    {
        id = 'R2',
        alias = 'VIU_Fleet_Robot_2',
        start = {x = 3, y = 10},
        charger = {x = 2, y = 10},
        goal = {x = 10, y = 2},
        battery = 36.0,
    },
    {
        id = 'R3',
        alias = 'VIU_Fleet_Robot_3',
        start = {x = 6, y = 2},
        charger = {x = 6, y = 2},
        goal = {x = 9, y = 10},
        battery = 64.0,
    },
}

local blocked = {}
local reservations = {cells = {}, edges = {}}
local planCount = 0
local reservationConflictsAvoided = 0
local chargingEvents = 0
local plansReady = 0
local lastT = 0
local lastPublish = -1000

local function key(x, y)
    return tostring(x) .. ':' .. tostring(y)
end

local function tkey(t, x, y)
    return tostring(t) .. ':' .. tostring(x) .. ':' .. tostring(y)
end

local function ekey(t, ax, ay, bx, by)
    return tostring(t) .. ':' .. tostring(ax) .. ':' .. tostring(ay) .. '>' .. tostring(bx) .. ':' .. tostring(by)
end

local function cloneCell(c)
    return {x = c.x, y = c.y}
end

local function sameCell(a, b)
    return a and b and a.x == b.x and a.y == b.y
end

local function world(c)
    return {
        cfg.originX + (c.x - 1) * cfg.cell,
        cfg.originY + (c.y - 1) * cfg.cell,
        cfg.z,
    }
end

local function inBounds(c)
    return c.x >= 1 and c.x <= cfg.gridW and c.y >= 1 and c.y <= cfg.gridH
end

local function isReservedGoalOrCharger(c)
    for _, r in ipairs(robots) do
        if sameCell(c, r.goal) or sameCell(c, r.charger) then
            return true
        end
    end
    return false
end

local function isBlocked(c)
    if isReservedGoalOrCharger(c) then
        return false
    end
    return blocked[key(c.x, c.y)] == true
end

local function safeGetObject(path)
    local ok, handle = pcall(sim.getObject, path)
    if ok and handle and handle >= 0 then
        return handle
    end
    return -1
end

local function setColor(alias, rgb)
    local h = safeGetObject('/' .. alias)
    if h >= 0 then
        pcall(sim.setShapeColor, h, nil, sim.colorcomponent_ambient_diffuse, rgb)
    end
end

local function manhattan(a, b)
    return math.abs(a.x - b.x) + math.abs(a.y - b.y)
end

local function popBest(open)
    local best = 1
    for i = 2, #open do
        if open[i].f < open[best].f then
            best = i
        elseif open[i].f == open[best].f and open[i].h < open[best].h then
            best = i
        end
    end
    local node = open[best]
    table.remove(open, best)
    return node
end

local function reconstruct(node)
    local path = {}
    local n = node
    while n do
        table.insert(path, 1, {x = n.x, y = n.y})
        n = n.parent
    end
    return path
end

local function blockedByReservation(prev, nextCell, nextT)
    if reservations.cells[tkey(nextT, nextCell.x, nextCell.y)] then
        reservationConflictsAvoided = reservationConflictsAvoided + 1
        return true
    end
    if prev and reservations.edges[ekey(nextT, nextCell.x, nextCell.y, prev.x, prev.y)] then
        reservationConflictsAvoided = reservationConflictsAvoided + 1
        return true
    end
    return false
end

local function astar(start, goal)
    local open = {}
    local bestG = {}
    local h = manhattan(start, goal)
    local startNode = {x = start.x, y = start.y, t = 0, g = 0, h = h, f = h, parent = nil}
    table.insert(open, startNode)
    bestG[tkey(0, start.x, start.y)] = 0

    local moves = {
        {x = 1, y = 0},
        {x = -1, y = 0},
        {x = 0, y = 1},
        {x = 0, y = -1},
        {x = 0, y = 0},
    }

    local iterations = 0
    while #open > 0 and iterations < 2600 do
        iterations = iterations + 1
        local node = popBest(open)
        if node.x == goal.x and node.y == goal.y then
            return reconstruct(node)
        end
        if node.t < cfg.maxSearchT then
            for _, m in ipairs(moves) do
                local nc = {x = node.x + m.x, y = node.y + m.y}
                local nt = node.t + 1
                if inBounds(nc) and not isBlocked(nc) and not blockedByReservation({x = node.x, y = node.y}, nc, nt) then
                    local g = node.g + 1
                    if m.x == 0 and m.y == 0 then
                        g = g + 0.18
                    end
                    local nk = tkey(nt, nc.x, nc.y)
                    if bestG[nk] == nil or g < bestG[nk] then
                        local nh = manhattan(nc, goal)
                        bestG[nk] = g
                        table.insert(open, {
                            x = nc.x,
                            y = nc.y,
                            t = nt,
                            g = g,
                            h = nh,
                            f = g + nh,
                            parent = node,
                        })
                    end
                end
            end
        end
    end
    return {cloneCell(start)}
end

local function reservePath(robot, path)
    if not path or #path == 0 then
        return
    end
    local hold = 18
    for t = 1, #path + hold do
        local idx = math.min(t, #path)
        local c = path[idx]
        reservations.cells[tkey(t, c.x, c.y)] = robot.id
        if idx > 1 then
            local prev = path[idx - 1]
            reservations.edges[ekey(t, prev.x, prev.y, c.x, c.y)] = robot.id
        end
    end
end

local function planFleet()
    reservations = {cells = {}, edges = {}}
    local activePlans = 0
    for _, r in ipairs(robots) do
        if r.target and r.state ~= 'CHARGING' and r.state ~= 'READY' then
            r.path = astar(r.current, r.target)
            r.pathIndex = 1
            r.pathTimer = 0
            planCount = planCount + 1
            activePlans = activePlans + 1
            reservePath(r, r.path)
        end
    end
    if activePlans > 0 then
        plansReady = 1
    end
end

local function setRobotPose(r, c, nextCell, frac)
    if r.handle < 0 then
        return
    end
    local a = world(c)
    local p = a
    local yaw = 0
    if nextCell then
        local b = world(nextCell)
        p = {
            a[1] + (b[1] - a[1]) * frac,
            a[2] + (b[2] - a[2]) * frac,
            cfg.z,
        }
        yaw = math.atan(b[2] - a[2], b[1] - a[1])
    end
    sim.setObjectPosition(r.handle, p)
    sim.setObjectOrientation(r.handle, {0, 0, yaw})
end

local function enterCharging(r)
    r.state = 'CHARGING'
    r.path = {cloneCell(r.current)}
    r.pathIndex = 1
    r.pathTimer = 0
    chargingEvents = chargingEvents + 1
    setColor('VIU_Fleet_Status_' .. r.id, {0.08, 0.44, 0.90})
end

local function beginTarget(r, state, target)
    r.state = state
    r.target = cloneCell(target)
    r.needsPlan = true
    if state == 'MISSION' then
        setColor('VIU_Fleet_Status_' .. r.id, {0.03, 0.70, 0.20})
    elseif state == 'TO_CHARGE' or state == 'RETURN_CHARGE' then
        setColor('VIU_Fleet_Status_' .. r.id, {0.95, 0.68, 0.05})
    end
end

local function updateRobot(r, dt)
    if r.state == 'READY' then
        r.battery = math.max(0, r.battery - cfg.idleDrain * dt)
        setRobotPose(r, r.current, nil, 0)
        return
    end

    if r.state == 'CHARGING' then
        r.battery = math.min(100, r.battery + cfg.chargeRate * dt)
        setRobotPose(r, r.current, nil, 0)
        if r.doneMission and r.battery >= cfg.fullBattery then
            r.state = 'READY'
            r.recharged = true
            r.target = nil
            setColor('VIU_Fleet_Status_' .. r.id, {0.03, 0.70, 0.20})
        elseif (not r.doneMission) and r.battery >= cfg.readyBattery then
            beginTarget(r, 'MISSION', r.goal)
        end
        return
    end

    if r.state == 'MISSION' and r.battery <= cfg.lowBattery then
        beginTarget(r, 'TO_CHARGE', r.charger)
        return
    end

    r.battery = math.max(0, r.battery - (cfg.idleDrain + cfg.moveDrain) * dt)

    if not r.path or #r.path == 0 then
        r.needsPlan = true
        return
    end

    if r.pathIndex >= #r.path then
        r.current = cloneCell(r.path[#r.path])
        setRobotPose(r, r.current, nil, 0)
        if r.state == 'MISSION' then
            r.doneMission = true
            beginTarget(r, 'RETURN_CHARGE', r.charger)
        elseif r.state == 'TO_CHARGE' or r.state == 'RETURN_CHARGE' then
            enterCharging(r)
        end
        return
    end

    r.pathTimer = r.pathTimer + dt
    while r.pathTimer >= cfg.movePeriod and r.pathIndex < #r.path do
        r.pathTimer = r.pathTimer - cfg.movePeriod
        r.pathIndex = r.pathIndex + 1
        r.current = cloneCell(r.path[r.pathIndex])
    end

    local nextCell = nil
    if r.pathIndex < #r.path then
        nextCell = r.path[r.pathIndex + 1]
    end
    setRobotPose(r, r.path[r.pathIndex], nextCell, math.min(1, r.pathTimer / cfg.movePeriod))
end

local function publishFleet()
    local minBattery = 100
    local readyCount = 0
    local missionCount = 0
    local rechargedCount = 0
    local summary = {}

    for _, r in ipairs(robots) do
        minBattery = math.min(minBattery, r.battery)
        if r.state == 'READY' then
            readyCount = readyCount + 1
        end
        if r.doneMission then
            missionCount = missionCount + 1
        end
        if r.recharged then
            rechargedCount = rechargedCount + 1
        end
        table.insert(summary, string.format('%s:%s:%.1f', r.id, r.state, r.battery))
    end

    sim.setInt32Signal('fleetRobotsTotal', #robots)
    sim.setInt32Signal('fleetAStarPlansReady', plansReady)
    sim.setInt32Signal('fleetAStarPlanCount', planCount)
    sim.setInt32Signal('fleetReservationConflictsAvoided', reservationConflictsAvoided)
    sim.setInt32Signal('fleetChargingEvents', chargingEvents)
    sim.setInt32Signal('fleetMissionComplete', missionCount)
    sim.setInt32Signal('fleetRechargedCount', rechargedCount)
    sim.setInt32Signal('fleetAllComplete', readyCount == #robots and 1 or 0)
    sim.setFloatSignal('fleetMinBattery', minBattery)
    sim.setStringSignal('fleetStateSummary', table.concat(summary, ' | '))
end

function sysCall_init()
    local obstacleCells = {
        {x = 6, y = 5}, {x = 6, y = 6}, {x = 7, y = 5}, {x = 7, y = 6},
        {x = 8, y = 6}, {x = 5, y = 8}, {x = 6, y = 8},
    }
    for _, c in ipairs(obstacleCells) do
        blocked[key(c.x, c.y)] = true
    end

    for _, r in ipairs(robots) do
        r.handle = safeGetObject('/' .. r.alias)
        r.current = cloneCell(r.start)
        r.state = 'INIT'
        r.path = {}
        r.pathIndex = 1
        r.pathTimer = 0
        r.doneMission = false
        r.recharged = false
        r.needsPlan = false
        setRobotPose(r, r.current, nil, 0)

        if r.battery <= cfg.lowBattery then
            beginTarget(r, 'TO_CHARGE', r.charger)
        else
            beginTarget(r, 'MISSION', r.goal)
        end
    end

    planFleet()
    lastT = sim.getSimulationTime()
    publishFleet()
    sim.addLog(sim.verbosity_scriptinfos, 'Actividad 2 multi-robot A* manager ready: 3 robots, reservations, battery drain and recharge.')
end

function sysCall_actuation()
    local t = sim.getSimulationTime()
    local dt = math.max(0.01, math.min(0.12, t - lastT))
    lastT = t

    local needsReplan = false
    for _, r in ipairs(robots) do
        updateRobot(r, dt)
        if r.needsPlan then
            needsReplan = true
            r.needsPlan = false
        end
    end

    if needsReplan then
        planFleet()
    end

    if (t - lastPublish) >= cfg.publishPeriod then
        publishFleet()
        lastPublish = t
    end
end

function sysCall_cleanup()
    publishFleet()
end
