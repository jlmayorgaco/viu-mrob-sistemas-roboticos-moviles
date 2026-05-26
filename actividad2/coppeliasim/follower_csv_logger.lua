-- VIU SRM - Actividad 2.1
-- Runtime CSV logger for the Bill-following experiment.
-- The Python builder replaces __A2F_LOG_DIR__ with an absolute folder path.

sim = require('sim')

local robot = -1
local bill = -1
local file = nil
local lastWriteT = -1000
local logPeriod = 0.05
local outputDir = '__A2F_LOG_DIR__'

local function safeGetObject(path)
    local ok, handle = pcall(sim.getObject, path)
    if ok and handle and handle >= 0 then return handle end
    return -1
end

local function numberSignal(name, fallback)
    local value = sim.getFloatSignal(name)
    if value == nil then return fallback end
    return value
end

local function stringSignal(name, fallback)
    local value = sim.getStringSignal(name)
    if value == nil or value == '' then return fallback end
    return value
end

local function csvText(value)
    local s = tostring(value or '')
    s = string.gsub(s, '"', '""')
    return '"' .. s .. '"'
end

local function openFile()
    local mode = stringSignal('followerMode', stringSignal('followerControlMode', 'P'))
    local path = outputDir .. '/coppeliasim_runtime_' .. mode .. '.csv'
    file = io.open(path, 'w')
    if file then
        file:write('t,mode,bill_x,bill_y,pioneer_x,pioneer_y,distance,error,heading_error,control_v,control_w,integral,derivative,bill_state,bill_speed,wheel_left_linear,wheel_right_linear,wheel_left_omega,wheel_right_omega,u_left,u_right,du_left,du_right,wheel_left_power,wheel_right_power,yaw_power,total_power,energy_j\n')
        sim.setStringSignal('followerCsvPath', path)
        sim.addLog(sim.verbosity_scriptinfos, 'Follower CSV logger writing ' .. path)
    else
        sim.addLog(sim.verbosity_scripterrors, 'Follower CSV logger could not open ' .. path)
    end
end

function sysCall_init()
    robot = safeGetObject('/PioneerP3DX')
    bill = safeGetObject('/Bill')
    openFile()
end

function sysCall_sensing()
    if not file or robot < 0 or bill < 0 then return end

    local t = sim.getSimulationTime()
    if t - lastWriteT < logPeriod then return end
    lastWriteT = t

    local bp = sim.getObjectPosition(bill, -1)
    local rp = sim.getObjectPosition(robot, -1)
    local mode = stringSignal('followerMode', stringSignal('followerControlMode', 'P'))
    local billState = stringSignal('billPathState', 'UNKNOWN')

    file:write(string.format(
        '%.3f,%s,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%s,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f,%.5f\n',
        t,
        csvText(mode),
        bp[1],
        bp[2],
        rp[1],
        rp[2],
        numberSignal('followerDistance', -1),
        numberSignal('followerDistanceError', 0),
        numberSignal('followerHeadingError', 0),
        numberSignal('followerControlV', 0),
        numberSignal('followerControlW', 0),
        numberSignal('followerIntegralError', 0),
        numberSignal('followerDerivativeError', 0),
        csvText(billState),
        numberSignal('billSpeed', 0),
        numberSignal('followerWheelLeftLinear', 0),
        numberSignal('followerWheelRightLinear', 0),
        numberSignal('followerWheelLeftOmega', 0),
        numberSignal('followerWheelRightOmega', 0),
        numberSignal('followerWheelLeftU', 0),
        numberSignal('followerWheelRightU', 0),
        numberSignal('followerWheelLeftDeltaU', 0),
        numberSignal('followerWheelRightDeltaU', 0),
        numberSignal('followerWheelLeftPower', 0),
        numberSignal('followerWheelRightPower', 0),
        numberSignal('followerYawPower', 0),
        numberSignal('followerPowerTotal', 0),
        numberSignal('followerEnergyJ', 0)
    ))
end

function sysCall_cleanup()
    if file then
        file:flush()
        file:close()
        file = nil
    end
end
