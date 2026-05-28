-- Capture report screenshots from CoppeliaSim scenes.
-- Run with:
-- coppeliaSim.exe -h -GcaptureDir=<absolute-output-dir> -GcaptureTag=phase1 -s95000 -q -a<this-file> -f<scene.ttt>

local Capture = {}
Capture.__index = Capture

local function rad(deg)
    return deg * math.pi / 180.0
end

local function namedString(name, fallback)
    local ok, value = pcall(sim.getNamedStringParam, name)
    if ok and value then
        return tostring(value)
    end
    return fallback
end

local function joinPath(dir, fileName)
    if dir:sub(-1) == '/' or dir:sub(-1) == '\\' then
        return dir .. fileName
    end
    return dir .. '/' .. fileName
end

local function safeGet(path)
    local ok, handle = pcall(sim.getObject, path)
    if ok and handle then
        return handle
    end
    return -1
end

local function lookAtPose(position, target)
    local dx = target[1] - position[1]
    local dy = target[2] - position[2]
    local dz = target[3] - position[3]
    local norm = math.sqrt(dx * dx + dy * dy + dz * dz)
    if norm < 1e-9 then
        return sim.buildPose(position, {0, 0, -1}, 3)
    end
    return sim.buildPose(position, {dx / norm, dy / norm, dz / norm}, 3)
end

function Capture:new()
    local outDir = namedString(
        'captureDir',
        'C:/Users/walla/Documents/Master VIU/C9_SistRobMoviles/viu-mrob-sistemas-roboticos-moviles/actividad2/figures/phase1'
    )
    local tag = namedString('captureTag', 'phase1')
    local schedule
    if tag == 'phase2' then
        schedule = {
            {time = 1.0, file = 'coppeliasim_phase2_initial_unknown.png'},
            {time = 88.0, file = 'coppeliasim_phase2_replan_dynamic.png'},
        }
    else
        schedule = {
            {time = 1.0, file = 'coppeliasim_phase1_overview.png'},
            {time = 6.0, file = 'coppeliasim_phase1_handoff_t1.png'},
            {time = 45.0, file = 'coppeliasim_phase1_bill_working.png'},
            {time = 92.0, file = 'coppeliasim_phase1_sensor_rays_avoidance.png'},
        }
    end
    return setmetatable({
        outDir = outDir,
        tag = tag,
        schedule = schedule,
        nextIndex = 1,
        sensor = -1,
    }, self)
end

function Capture:createSensor()
    if self.sensor >= 0 then
        return
    end
    self.sensor = sim.createVisionSensor(
        1 + 2 + 4 + 64 + 128,
        {1280, 900, 0, 0},
        {0.01, 25.0, rad(62), 0.01, 0, 0, 0.88, 0.90, 0.94, 0, 0}
    )
    sim.setObjectAlias(self.sensor, 'Report_Capture_VisionSensor')
    sim.setObjectPose(self.sensor, lookAtPose({3.75, -4.70, 3.55}, {0.0, 0.0, 0.08}), sim.handle_world)
end

function Capture:saveCurrent(fileName)
    self:createSensor()
    sim.handleVisionSensor(self.sensor)
    local image, resolution = sim.getVisionSensorImg(self.sensor)
    image = sim.transformImage(image, resolution, 4)
    sim.saveImage(image, resolution, 0, joinPath(self.outDir, fileName), -1)
    sim.addLog(sim.verbosity_scriptinfos, 'Saved CoppeliaSim capture: ' .. fileName)
end

function Capture:update()
    if self.nextIndex > #self.schedule then
        sim.stopSimulation()
        return
    end

    local item = self.schedule[self.nextIndex]
    if sim.getSimulationTime() >= item.time then
        self:saveCurrent(item.file)
        self.nextIndex = self.nextIndex + 1
    end
end

local app

function sysCall_init()
    app = Capture:new()
    sim.addLog(sim.verbosity_scriptinfos, 'Screenshot capture configured: ' .. app.tag)
end

function sysCall_sensing()
    if app then
        app:update()
    end
end

function sysCall_cleanup()
    if app and app.sensor and app.sensor >= 0 then
        pcall(sim.removeObjects, {app.sensor})
    end
end
