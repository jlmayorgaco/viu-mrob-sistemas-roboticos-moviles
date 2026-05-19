-- VIU SRM - Actividad 2
-- Scenario/event manager embedded in the final scene.
-- It exercises the controller with route start, moving obstacle, safety hold,
-- dynamic target, narrow passage, sensor degradation and low-battery events.

sim = require('sim')

local handles = {}
local lastScenario = ''

local function safeGetObject(path)
    local ok, handle = pcall(sim.getObject, path)
    if ok and handle and handle >= 0 then
        return handle
    end
    return -1
end

local function remember(alias)
    handles[alias] = safeGetObject('/' .. alias)
end

local function setPos(alias, p)
    local h = handles[alias] or safeGetObject('/' .. alias)
    if h >= 0 then
        sim.setObjectPosition(h, p)
    end
end

local function setColor(alias, rgb)
    local h = handles[alias] or safeGetObject('/' .. alias)
    if h >= 0 then
        pcall(sim.setShapeColor, h, nil, sim.colorcomponent_ambient_diffuse, rgb)
    end
end

local function setTraffic(mode)
    if mode == 'RED' then
        setColor('VIU_Traffic_Red', {0.95, 0.06, 0.04})
        setColor('VIU_Traffic_Yellow', {0.18, 0.15, 0.03})
        setColor('VIU_Traffic_Green', {0.03, 0.15, 0.05})
    elseif mode == 'YELLOW' then
        setColor('VIU_Traffic_Red', {0.18, 0.03, 0.03})
        setColor('VIU_Traffic_Yellow', {0.95, 0.68, 0.05})
        setColor('VIU_Traffic_Green', {0.03, 0.15, 0.05})
    else
        setColor('VIU_Traffic_Red', {0.18, 0.03, 0.03})
        setColor('VIU_Traffic_Yellow', {0.18, 0.15, 0.03})
        setColor('VIU_Traffic_Green', {0.02, 0.72, 0.18})
    end
end

local function stage(name, eventText)
    if name ~= lastScenario then
        sim.addLog(sim.verbosity_scriptinfos, 'Actividad 2 scenario: ' .. name .. ' - ' .. eventText)
        lastScenario = name
    end
    sim.setStringSignal('pioneerScenario', name)
    sim.setStringSignal('pioneerScenarioEvent', eventText)
end

function sysCall_init()
    local names = {
        'VIU_EventPallet_Moving',
        'VIU_EventGate_Left',
        'VIU_EventGate_Right',
        'VIU_Traffic_Red',
        'VIU_Traffic_Yellow',
        'VIU_Traffic_Green',
        'mannequin',
    }
    for _, alias in ipairs(names) do
        remember(alias)
    end

    sim.setInt32Signal('missionReady', 1)
    sim.setInt32Signal('pioneerUseWaypoints', 1)
    sim.setInt32Signal('pioneerSensorNoiseEnabled', 1)
    sim.setInt32Signal('pioneerSensorFaultMode', 0)
    sim.setFloatSignal('pioneerBatteryOverride', -1)
    if sim.getInt32Signal('pioneerScenarioEnabled') == nil then
        sim.setInt32Signal('pioneerScenarioEnabled', 1)
    end
    setTraffic('GREEN')
    stage('S0_BOOT', 'Scene initialized, mission ready')
end

function sysCall_actuation()
    local enabled = sim.getInt32Signal('pioneerScenarioEnabled')
    if enabled ~= nil and enabled == 0 then
        sim.setInt32Signal('missionReady', 1)
        sim.setInt32Signal('pioneerSensorFaultMode', 0)
        sim.setFloatSignal('pioneerBatteryOverride', -1)
        setTraffic('GREEN')
        stage('S_MANUAL', 'Scenario manager disabled')
        return
    end

    local t = sim.getSimulationTime()
    if t < 5.0 then
        sim.setInt32Signal('missionReady', 1)
        sim.setInt32Signal('pioneerSensorFaultMode', 0)
        sim.setFloatSignal('pioneerBatteryOverride', -1)
        setTraffic('GREEN')
        setPos('VIU_EventPallet_Moving', {-0.35, -0.34, 0.15})
        setPos('VIU_EventGate_Left', {0.52, -0.28, 0.23})
        setPos('VIU_EventGate_Right', {0.98, -0.28, 0.23})
        setPos('mannequin', {1.45, 1.20, 0.28})
        stage('S1_ROUTE_START', 'Waypoint route and nominal target')
    elseif t < 10.5 then
        sim.setInt32Signal('missionReady', 1)
        sim.setInt32Signal('pioneerSensorFaultMode', 0)
        sim.setFloatSignal('pioneerBatteryOverride', -1)
        setTraffic('YELLOW')
        local u = (t - 5.0) / 5.5
        setPos('VIU_EventPallet_Moving', {-0.16 + 0.62 * u, -1.20 + 0.10 * math.sin(4.0 * u), 0.15})
        stage('S2_MOVING_OBSTACLE', 'Moving pallet crosses the approach lane')
    elseif t < 13.5 then
        sim.setInt32Signal('missionReady', 0)
        sim.setInt32Signal('pioneerSensorFaultMode', 0)
        sim.setFloatSignal('pioneerBatteryOverride', -1)
        setTraffic('RED')
        setPos('VIU_EventPallet_Moving', {0.72, -0.84, 0.15})
        stage('S3_SAFETY_HOLD', 'Cell interlock pauses the robot')
    elseif t < 20.0 then
        sim.setInt32Signal('missionReady', 1)
        sim.setInt32Signal('pioneerSensorFaultMode', 0)
        sim.setFloatSignal('pioneerBatteryOverride', -1)
        setTraffic('GREEN')
        local u = t - 13.5
        setPos('mannequin', {1.45 + 0.18 * math.sin(0.65 * u), 1.20 + 0.14 * math.cos(0.55 * u), 0.28})
        setPos('VIU_EventPallet_Moving', {0.20, -0.55, 0.15})
        stage('S4_DYNAMIC_TARGET', 'Target dummy moves inside the final station')
    elseif t < 27.0 then
        sim.setInt32Signal('missionReady', 1)
        sim.setInt32Signal('pioneerSensorFaultMode', 0)
        sim.setFloatSignal('pioneerBatteryOverride', -1)
        setTraffic('YELLOW')
        setPos('mannequin', {1.45, 1.20, 0.28})
        setPos('VIU_EventGate_Left', {0.48, -0.46, 0.23})
        setPos('VIU_EventGate_Right', {1.02, -0.46, 0.23})
        setPos('VIU_EventPallet_Moving', {0.30, -0.84, 0.15})
        stage('S5_NARROW_PASSAGE', 'Temporary narrow passage near the cell entrance')
    elseif t < 32.5 then
        sim.setInt32Signal('missionReady', 1)
        sim.setInt32Signal('pioneerSensorFaultMode', 1)
        sim.setFloatSignal('pioneerBatteryOverride', -1)
        setTraffic('YELLOW')
        setPos('mannequin', {1.45, 1.20, 0.28})
        setPos('VIU_EventGate_Left', {0.52, -0.28, 0.23})
        setPos('VIU_EventGate_Right', {0.98, -0.28, 0.23})
        setPos('VIU_EventPallet_Moving', {0.18 + 0.16 * math.sin(1.6 * t), -0.70, 0.15})
        stage('S6_SENSOR_DEGRADATION', 'Noisy sensor plus one intermittent front-left sensor')
    elseif t < 38.0 then
        sim.setInt32Signal('missionReady', 1)
        sim.setInt32Signal('pioneerSensorFaultMode', 0)
        sim.setFloatSignal('pioneerBatteryOverride', 52.0)
        setTraffic('YELLOW')
        setPos('mannequin', {1.45, 1.20, 0.28})
        setPos('VIU_EventPallet_Moving', {-0.35, -0.34, 0.15})
        stage('S7_LOW_BATTERY_SPEED_LIMIT', 'Battery policy limits speed and updates HMI')
    else
        sim.setInt32Signal('missionReady', 1)
        sim.setInt32Signal('pioneerSensorFaultMode', 0)
        sim.setFloatSignal('pioneerBatteryOverride', 68.0)
        setTraffic('GREEN')
        setPos('mannequin', {1.45, 1.20, 0.28})
        setPos('VIU_EventPallet_Moving', {-0.35, -0.34, 0.15})
        setPos('VIU_EventGate_Left', {0.52, -0.28, 0.23})
        setPos('VIU_EventGate_Right', {0.98, -0.28, 0.23})
        stage('S8_FINAL_APPROACH', 'Final station restored after battery and sensor tests')
    end
end
