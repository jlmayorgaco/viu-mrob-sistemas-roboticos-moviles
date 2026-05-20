-- VIU SRM - Actividad 2
-- Runtime demo overlay: camera-facing labels for the evaluator.
-- The scene also contains physical sign plates, so the .ttt remains readable
-- even if banners are disabled in a specific CoppeliaSim installation.

sim = require('sim')

local banners = {}

local function safeGetObject(path)
    local ok, handle = pcall(sim.getObject, path)
    if ok and handle and handle >= 0 then
        return handle
    end
    return -1
end

local function flag(name, fallback)
    local value = sim[name]
    if value then
        return value
    end
    return fallback
end

local function addLabel(anchorAlias, text, size)
    local parent = safeGetObject('/' .. anchorAlias)
    if parent < 0 or sim.addBanner == nil then
        return
    end
    local options =
        flag('banner_overlay', 8) +
        flag('banner_fullyfacingcamera', 256) +
        flag('banner_followparentvisibility', 16) +
        flag('banner_clickselectsparent', 32) +
        flag('banner_bitmapfont', 2048)
    local ok, bannerId = pcall(
        sim.addBanner,
        text,
        size,
        options,
        {0.0, 0.0, 0.0, 0.0, 0.0, 0.0},
        parent
    )
    if ok and bannerId then
        table.insert(banners, bannerId)
    end
end

function sysCall_init()
    local labels = {
        {'VIU_Label_GuideCompliance', 'GUIA A2: Pioneer + campos potenciales + anticolision + celda', 0.075},
        {'VIU_Label_PotentialFields', 'Pioneer: atraccion al mannequin por campos potenciales', 0.060},
        {'VIU_Label_AntiCollision', 'Anticolision: 16 ultrasonidos + 6 sensores virtuales', 0.060},
        {'VIU_Label_AStarFleet', '3 AMR: A* cooperativo con reservas celda-tiempo', 0.060},
        {'VIU_Label_ChargingPolicy', 'Bateria: descarga, retorno y recarga automatica', 0.060},
        {'VIU_Label_HMIValidation', 'HMI: estado, bateria, zona, fallo sensorial y eventos', 0.055},
        {'VIU_Label_DemoSteps', 'Demo: Play -> S1-S8 -> ARRIVED + flota READY', 0.055},
    }
    for _, spec in ipairs(labels) do
        addLabel(spec[1], spec[2], spec[3])
    end
    sim.setStringSignal('demoOverlayLabels', 'labels_ready:' .. tostring(#labels))
    sim.setInt32Signal('demoOverlayBannerCount', #banners)
end

function sysCall_cleanup()
    if sim.removeBanner ~= nil then
        for _, bannerId in ipairs(banners) do
            pcall(sim.removeBanner, bannerId)
        end
    end
end
