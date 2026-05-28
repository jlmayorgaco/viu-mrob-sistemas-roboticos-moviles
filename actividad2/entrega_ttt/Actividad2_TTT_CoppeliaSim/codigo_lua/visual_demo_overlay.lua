-- VIU SRM - Actividad 2
-- Runtime scene labels. Physical plates remain in the scene if banners are unavailable.

sim = require('sim')

local Labels = {
    {'VIU_Label_GuideCompliance', 'GUIA A2: Pioneer + campos potenciales + anticolision + celda', 0.075},
    {'VIU_Label_PotentialFields', 'Pioneer: atraccion al mannequin por campos potenciales', 0.060},
    {'VIU_Label_AntiCollision', 'Anticolision: 16 ultrasonidos + 6 sensores virtuales', 0.060},
    {'VIU_Label_ChargingPolicy', 'Bateria: descarga, retorno y recarga automatica', 0.060},
    {'VIU_Label_HMIValidation', 'HMI: estado, bateria, zona, fallo sensorial y eventos', 0.055},
    {'VIU_Label_TaskSteps', 'Ejecucion: Play -> tareas T1/T2 -> CHARGING', 0.055},
}

local function safeGetObject(path)
    local ok, handle = pcall(sim.getObject, path)
    if ok and handle and handle >= 0 then return handle end
    return -1
end

local BannerOverlay = {}
BannerOverlay.__index = BannerOverlay

function BannerOverlay:new(labels)
    return setmetatable({labels = labels, banners = {}}, self)
end

function BannerOverlay:flag(name, fallback)
    local value = sim[name]
    if value then return value end
    return fallback
end

function BannerOverlay:options()
    return self:flag('banner_overlay', 8)
        + self:flag('banner_fullyfacingcamera', 256)
        + self:flag('banner_followparentvisibility', 16)
        + self:flag('banner_clickselectsparent', 32)
        + self:flag('banner_bitmapfont', 2048)
end

function BannerOverlay:addLabel(anchorAlias, text, size)
    local parent = safeGetObject('/' .. anchorAlias)
    if parent < 0 or sim.addBanner == nil then
        return
    end

    local ok, bannerId = pcall(
        sim.addBanner,
        text,
        size,
        self:options(),
        {0.0, 0.0, 0.0, 0.0, 0.0, 0.0},
        parent
    )
    if ok and bannerId then
        self.banners[#self.banners + 1] = bannerId
    end
end

function BannerOverlay:init()
    for _, spec in ipairs(self.labels) do
        self:addLabel(spec[1], spec[2], spec[3])
    end
    sim.setStringSignal('sceneLabelOverlayStatus', 'labels_ready:' .. tostring(#self.labels))
    sim.setInt32Signal('sceneLabelOverlayCount', #self.banners)
end

function BannerOverlay:cleanup()
    if sim.removeBanner ~= nil then
        for _, bannerId in ipairs(self.banners) do
            pcall(sim.removeBanner, bannerId)
        end
    end
end

local app = nil

function sysCall_init()
    app = BannerOverlay:new(Labels)
    app:init()
end

function sysCall_cleanup()
    if app then
        app:cleanup()
    end
end
