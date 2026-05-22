local ok, err = pcall(function()
    local root = [[C:/Users/walla/Documents/Master VIU/C9_SistRobMoviles/viu-mrob-sistemas-roboticos-moviles]]
    local out = root .. [[/actividad1/figures/source/coppeliasim_youbot_render.png]]
    local floorTexture = root .. [[/actividad1/figures/source/coppeliasim_floor_texture.png]]
    local youbotModel = [[C:/Program Files/CoppeliaRobotics/CoppeliaSimEdu/models/robots/mobile/KUKA YouBot.ttm]]

    sim.addLog(sim.verbosity_scriptinfos, 'capture: creating richer CoppeliaSim validation scene')

    local function setColor(h, color)
        sim.setShapeColor(h, nil, sim.colorcomponent_ambient_diffuse, color)
    end

    local function box(name, pos, size, color)
        local h = sim.createPrimitiveShape(sim.primitiveshape_cuboid, size, 0)
        sim.setObjectPosition(h, -1, pos)
        sim.setObjectAlias(h, name, 1)
        setColor(h, color)
        return h
    end

    local function cyl(name, pos, size, color)
        local h = sim.createPrimitiveShape(sim.primitiveshape_cylinder, size, 0)
        sim.setObjectPosition(h, -1, pos)
        sim.setObjectAlias(h, name, 1)
        setColor(h, color)
        return h
    end

    local function cone(name, pos, size, color)
        local h = sim.createPrimitiveShape(sim.primitiveshape_cone, size, 0)
        sim.setObjectPosition(h, -1, pos)
        sim.setObjectAlias(h, name, 1)
        setColor(h, color)
        return h
    end

    local white = {0.91, 0.94, 0.96}
    local yellow = {1.00, 0.74, 0.28}
    local teal = {0.08, 0.48, 0.55}
    local cyan = {0.12, 0.64, 0.76}
    local red = {0.78, 0.10, 0.10}
    local orange = {0.97, 0.50, 0.18}
    local grey = {0.42, 0.48, 0.54}
    local dark = {0.12, 0.15, 0.18}
    local green = {0.12, 0.58, 0.42}

    local floor = nil
    if sim.createTexture then
        local texShape = sim.createTexture(floorTexture, 4 + 8, {7.4, 4.6}, {5.0, 3.4}, nil, 512)
        floor = texShape
        sim.setObjectAlias(floor, 'textured concrete floor - HTP 19.1 pilot', 1)
        sim.setObjectPosition(floor, -1, {0, 0, 0.001})
    else
        floor = box('concrete floor - HTP 19.1 pilot', {0, 0, -0.025}, {7.4, 4.6, 0.05}, {0.68, 0.70, 0.72})
    end

    -- Aisle markings and safety zones
    box('main aisle yellow stripe left', {-0.02, -1.62, 0.026}, {6.85, 0.035, 0.012}, yellow)
    box('main aisle yellow stripe right', {-0.02, 1.22, 0.026}, {6.85, 0.035, 0.012}, yellow)
    box('HTP station safety perimeter', {1.82, 1.03, 0.030}, {1.76, 0.040, 0.014}, red)
    box('HTP station safety perimeter', {1.82, 0.33, 0.030}, {1.76, 0.040, 0.014}, red)
    box('HTP station safety perimeter', {0.96, 0.68, 0.030}, {0.040, 0.72, 0.014}, red)
    box('HTP station safety perimeter', {2.68, 0.68, 0.030}, {0.040, 0.72, 0.014}, red)

    for i = -3, 3 do
        box('floor joint x ' .. i, {i * 0.92, -0.20, 0.024}, {0.012, 4.10, 0.010}, {0.55, 0.58, 0.61})
    end
    for i = -2, 2 do
        box('floor joint y ' .. i, {-0.05, i * 0.86, 0.024}, {6.90, 0.012, 0.010}, {0.55, 0.58, 0.61})
    end

    -- Logistics base with racks, pallets and kit boxes
    box('base logistics floor pad', {-2.35, -1.18, 0.035}, {1.70, 0.82, 0.020}, {0.08, 0.48, 0.55})
    for r = 0, 2 do
        local y = -1.70 + r * 0.40
        box('rack shelf ' .. r, {-2.78, y, 0.46}, {0.86, 0.08, 0.08}, dark)
        box('rack shelf ' .. r .. ' b', {-1.86, y, 0.46}, {0.86, 0.08, 0.08}, dark)
        box('kit crate left ' .. r, {-2.52, y, 0.24}, {0.30, 0.20, 0.22}, orange)
        box('kit crate right ' .. r, {-2.12, y, 0.24}, {0.28, 0.20, 0.22}, {0.16, 0.54, 0.66})
    end
    for x = -3.18, -1.48, 0.58 do
        for y = -2.02, 1.58, 2.02 do
            cyl('safety bollard', {x, y, 0.20}, {0.08, 0.08, 0.38}, orange)
        end
    end

    -- HTP station represented as a real workcell, not an abstract arrow.
    box('HTP station table', {1.82, 0.68, 0.18}, {1.44, 0.48, 0.24}, teal)
    box('HTP jig beam left', {1.32, 0.68, 0.42}, {0.86, 0.08, 0.14}, white)
    box('HTP jig beam right', {2.32, 0.68, 0.42}, {0.86, 0.08, 0.14}, white)
    box('HTP tailplane proxy', {1.82, 0.68, 0.58}, {1.18, 0.28, 0.08}, {0.78, 0.84, 0.88})
    box('tool trolley', {2.74, -0.35, 0.24}, {0.42, 0.32, 0.38}, {0.18, 0.52, 0.62})
    box('tool trolley drawer', {2.74, -0.35, 0.46}, {0.45, 0.34, 0.035}, yellow)

    -- Obstacles for the blocked-route test and FOD event.
    box('blocked aisle pallet', {0.00, 0.32, 0.18}, {0.82, 0.30, 0.30}, red)
    box('warning tape on blocked aisle', {0.00, 0.32, 0.36}, {0.86, 0.035, 0.035}, yellow)
    cone('traffic cone 1', {-0.58, 0.30, 0.20}, {0.14, 0.14, 0.34}, orange)
    cone('traffic cone 2', {0.58, 0.30, 0.20}, {0.14, 0.14, 0.34}, orange)
    box('FOD object', {2.48, 1.44, 0.07}, {0.20, 0.06, 0.05}, red)
    box('FOD capture marker', {2.48, 1.44, 0.10}, {0.34, 0.025, 0.025}, yellow)

    -- Planned and executed path traces as low raised strips.
    local pathColor = {0.05, 0.58, 0.66}
    box('planned route segment 1', {-1.20, -0.92, 0.045}, {1.35, 0.040, 0.018}, pathColor)
    box('planned route segment 2', {-0.55, -0.42, 0.045}, {0.040, 1.00, 0.018}, pathColor)
    box('planned route segment 3', {0.62, -0.02, 0.045}, {1.86, 0.040, 0.018}, pathColor)
    box('planned route segment 4', {1.58, 0.34, 0.045}, {0.040, 0.72, 0.018}, pathColor)
    box('return route dashed 1', {1.12, -1.22, 0.046}, {0.44, 0.034, 0.016}, green)
    box('return route dashed 2', {0.42, -1.22, 0.046}, {0.44, 0.034, 0.016}, green)
    box('return route dashed 3', {-0.28, -1.22, 0.046}, {0.44, 0.034, 0.016}, green)

    -- Robot and sensor hints
    sim.addLog(sim.verbosity_scriptinfos, 'capture: loading YouBot proxy model')
    local robot = sim.loadModel(youbotModel)
    if robot and robot >= 0 then
        sim.setObjectPosition(robot, -1, {-0.62, -0.56, 0.08})
        sim.setObjectOrientation(robot, -1, {0, 0, math.rad(28)})
        sim.setObjectAlias(robot, 'KUKA YouBot - CoppeliaSim proxy', 1)
    else
        box('AMR proxy body', {-0.62, -0.56, 0.22}, {0.58, 0.40, 0.24}, grey)
        box('AMR proxy top sensor', {-0.62, -0.56, 0.40}, {0.24, 0.20, 0.08}, cyan)
    end
    local footprint = cyl('LiDAR footprint', {-0.62, -0.56, 0.065}, {0.92, 0.92, 0.010}, {0.12, 0.74, 0.86})
    sim.setShapeColor(footprint, nil, sim.colorcomponent_transparency, {0.68})
    cyl('delivery waypoint', {1.80, 0.30, 0.06}, {0.20, 0.20, 0.012}, green)
    cyl('return waypoint', {-2.36, -1.10, 0.06}, {0.20, 0.20, 0.012}, teal)

    -- A few vertical references help the render look like a plant, not an empty plane.
    box('rear wall left', {-3.56, 0.0, 0.86}, {0.06, 4.55, 1.70}, {0.84, 0.87, 0.89})
    box('rear wall back', {0.0, 2.25, 0.86}, {7.20, 0.06, 1.70}, {0.82, 0.85, 0.88})
    for x = -2.8, 2.8, 1.4 do
        box('wall bay marker', {x, 2.205, 0.90}, {0.06, 0.08, 1.50}, {0.58, 0.64, 0.68})
    end

    sim.addLog(sim.verbosity_scriptinfos, 'capture: rendering vision sensor')
    local cam = sim.createVisionSensor(1 + 4, {1280, 720, 0, 0}, {0.05, 50, 5.9, 0.02, 0, 0, 0.78, 0.84, 0.90, 0, 0})
    sim.setObjectPosition(cam, -1, {0, -0.05, 7.4})
    sim.setObjectOrientation(cam, -1, {math.pi, 0, 0})
    sim.handleVisionSensor(cam)
    local img, res = sim.getVisionSensorImg(cam, 0)
    sim.saveImage(img, res, 0, out, -1)
    sim.addLog(sim.verbosity_scriptinfos, 'capture: saved render to ' .. out)
end)

if not ok then
    sim.addLog(sim.verbosity_scripterrors, 'capture failed: ' .. tostring(err))
end
sim.quitSimulator()
