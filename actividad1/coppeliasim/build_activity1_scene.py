"""Build the CoppeliaSim scene for Actividad 1 SRM.

The scene is a visual and technical support for the AMR-FOD-Kitting proposal:
an industrial HTP A320 work area, logistics/kitting zone, RFID/QR gate,
FOD inspection point and one animated CoppeliaSim YouBot pilot.
It is meant to be opened in CoppeliaSim so screenshots can be taken for the
report and slide deck.
"""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
COPPELIA_DIR = Path(r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu")
MODELS_DIR = COPPELIA_DIR / "models"
OUTPUT_DIR = ROOT / "actividad1" / "coppeliasim"
OUTPUT_SCENE = OUTPUT_DIR / "Actividad1_AMR_FOD_Kitting_HTP_Alestis.ttt"
VALIDATION_JSON = OUTPUT_DIR / "Actividad1_AMR_FOD_Kitting_HTP_Alestis_validation.json"
FLOOR_SIZE = (24.0, 16.0)
FLOOR_MARGIN = 0.45
MISSION_ROUTE_POINTS = [
    (-7.10, -3.75, "Dock"),
    (-7.10, -1.20, "Kitting"),
    (-3.35, -0.55, "RFID"),
    (-1.30, -0.55, "StopHumano"),
    (-1.05, 0.76, "EsquivaHumano1"),
    (0.62, 0.76, "EsquivaHumano2"),
    (1.55, -0.55, "PasilloLibre"),
    (2.25, -1.05, "Aproximacion"),
    (5.60, -1.05, "Entrega"),
    (5.85, -0.92, "FOD"),
    (5.70, 0.72, "Salida"),
    (3.35, 1.35, "Bypass"),
    (0.50, 1.35, "Retorno"),
    (-3.35, 0.55, "RFID-retorno"),
    (-7.10, -3.75, "Dock-retorno"),
]
PILOT_MISSION_STEPS = [
    ("1", "Carga kit", "operario coloca kit y confirma HMI"),
    ("2", "RFID/QR", "lectura de kit y orden"),
    ("3", "Humano", "parada segura y esquiva"),
    ("4", "Pasillo", "replanificacion local AMR"),
    ("5", "Entrega HTP", "aproximacion lateral segura"),
    ("6", "FOD", "captura visual y revision"),
    ("7", "Retorno", "util o bandeja vuelve a dock"),
]
HUMAN_AVOIDANCE_POINT = (-0.55, -0.55)
HUMAN_SAFETY_RADIUS_M = 0.62


def load_coppeliasim():
    os.add_dll_directory(str(COPPELIA_DIR))
    sys.path.append(str(COPPELIA_DIR / "programming" / "coppeliaSimClientPython"))
    import builtins

    builtins.coppeliasim_library = str(COPPELIA_DIR / "coppeliaSimHeadless.dll")

    from coppeliasim.lib import appDir, simDeinitialize, simInitialize, simLoop
    import coppeliasim.bridge

    simInitialize(appDir().encode("utf-8"), 0)
    coppeliasim.bridge.load()
    sim = coppeliasim.bridge.require("sim")
    return sim, simLoop, simDeinitialize


def safe_get(sim, path: str) -> int:
    try:
        handle = sim.getObject(path)
    except Exception:
        return -1
    return handle if handle is not None else -1


def all_objects(sim) -> list[int]:
    handles: list[int] = []
    i = 0
    while True:
        handle = sim.getObjects(i, sim.handle_all)
        if handle == -1:
            break
        handles.append(handle)
        i += 1
    return handles


def set_color(sim, handle: int, color: Iterable[float]) -> None:
    try:
        sim.setShapeColor(handle, None, sim.colorcomponent_ambient_diffuse, list(color))
    except Exception:
        try:
            sim.setObjectColor(handle, 0, sim.colorcomponent_ambient_diffuse, list(color))
        except Exception:
            pass


def set_static_shape(sim, handle: int, *, respondable: bool, detectable: bool) -> None:
    try:
        sim.setObjectInt32Param(handle, sim.shapeintparam_static, 1)
        sim.setObjectInt32Param(handle, sim.shapeintparam_respondable, 1 if respondable else 0)
    except Exception:
        return

    special = sim.objectspecialproperty_renderable
    if detectable:
        special += sim.objectspecialproperty_collidable
        special += sim.objectspecialproperty_measurable
        special += sim.objectspecialproperty_detectable_all
    try:
        sim.setObjectSpecialProperty(handle, special)
    except Exception:
        pass


def create_box(
    sim,
    alias: str,
    size: tuple[float, float, float],
    position: tuple[float, float, float],
    color: tuple[float, float, float],
    parent: int,
    *,
    respondable: bool = True,
    detectable: bool = True,
    orientation: tuple[float, float, float] | None = None,
) -> int:
    handle = sim.createPrimitiveShape(sim.primitiveshape_cuboid, list(size), 2)
    sim.setObjectAlias(handle, alias)
    sim.setObjectPosition(handle, list(position))
    if orientation is not None:
        sim.setObjectOrientation(handle, list(orientation))
    set_color(sim, handle, color)
    set_static_shape(sim, handle, respondable=respondable, detectable=detectable)
    sim.setObjectParent(handle, parent, True)
    return handle


def create_box_local(
    sim,
    alias: str,
    size: tuple[float, float, float],
    local_position: tuple[float, float, float],
    color: tuple[float, float, float],
    parent: int,
    *,
    respondable: bool = False,
    detectable: bool = True,
    orientation: tuple[float, float, float] | None = None,
) -> int:
    handle = sim.createPrimitiveShape(sim.primitiveshape_cuboid, list(size), 2)
    sim.setObjectAlias(handle, alias)
    sim.setObjectParent(handle, parent, False)
    sim.setObjectPosition(handle, list(local_position), parent)
    if orientation is not None:
        sim.setObjectOrientation(handle, list(orientation), parent)
    set_color(sim, handle, color)
    set_static_shape(sim, handle, respondable=respondable, detectable=detectable)
    return handle


def create_cylinder(
    sim,
    alias: str,
    size: tuple[float, float, float],
    position: tuple[float, float, float],
    color: tuple[float, float, float],
    parent: int,
    *,
    respondable: bool = True,
    detectable: bool = True,
    orientation: tuple[float, float, float] | None = None,
) -> int:
    handle = sim.createPrimitiveShape(sim.primitiveshape_cylinder, list(size), 2)
    sim.setObjectAlias(handle, alias)
    sim.setObjectPosition(handle, list(position))
    if orientation is not None:
        sim.setObjectOrientation(handle, list(orientation))
    set_color(sim, handle, color)
    set_static_shape(sim, handle, respondable=respondable, detectable=detectable)
    sim.setObjectParent(handle, parent, True)
    return handle


def create_cylinder_local(
    sim,
    alias: str,
    size: tuple[float, float, float],
    local_position: tuple[float, float, float],
    color: tuple[float, float, float],
    parent: int,
    *,
    respondable: bool = False,
    detectable: bool = True,
    orientation: tuple[float, float, float] | None = None,
) -> int:
    handle = sim.createPrimitiveShape(sim.primitiveshape_cylinder, list(size), 2)
    sim.setObjectAlias(handle, alias)
    sim.setObjectParent(handle, parent, False)
    sim.setObjectPosition(handle, list(local_position), parent)
    if orientation is not None:
        sim.setObjectOrientation(handle, list(orientation), parent)
    set_color(sim, handle, color)
    set_static_shape(sim, handle, respondable=respondable, detectable=detectable)
    return handle


def create_sphere(
    sim,
    alias: str,
    size: tuple[float, float, float],
    position: tuple[float, float, float],
    color: tuple[float, float, float],
    parent: int,
    *,
    respondable: bool = False,
    detectable: bool = False,
) -> int:
    handle = sim.createPrimitiveShape(sim.primitiveshape_spheroid, list(size), 2)
    sim.setObjectAlias(handle, alias)
    sim.setObjectPosition(handle, list(position))
    set_color(sim, handle, color)
    set_static_shape(sim, handle, respondable=respondable, detectable=detectable)
    sim.setObjectParent(handle, parent, True)
    return handle


def create_sphere_local(
    sim,
    alias: str,
    size: tuple[float, float, float],
    local_position: tuple[float, float, float],
    color: tuple[float, float, float],
    parent: int,
    *,
    respondable: bool = False,
    detectable: bool = True,
) -> int:
    handle = sim.createPrimitiveShape(sim.primitiveshape_spheroid, list(size), 2)
    sim.setObjectAlias(handle, alias)
    sim.setObjectParent(handle, parent, False)
    sim.setObjectPosition(handle, list(local_position), parent)
    set_color(sim, handle, color)
    set_static_shape(sim, handle, respondable=respondable, detectable=detectable)
    return handle


def create_dummy(sim, alias: str, position: tuple[float, float, float], parent: int, size: float = 0.06) -> int:
    handle = sim.createDummy(size, None)
    sim.setObjectAlias(handle, alias)
    sim.setObjectPosition(handle, list(position))
    sim.setObjectParent(handle, parent, True)
    return handle


def create_dummy_oriented(
    sim,
    alias: str,
    position: tuple[float, float, float],
    yaw_deg: float,
    parent: int,
    size: float = 0.06,
) -> int:
    handle = create_dummy(sim, alias, position, parent, size=size)
    sim.setObjectOrientation(handle, [0.0, 0.0, math.radians(yaw_deg)])
    return handle


def set_tree_static(sim, root: int, *, respondable: bool = False, detectable: bool = True) -> int:
    try:
        handles = sim.getObjectsInTree(root, sim.handle_all, 0)
    except Exception:
        handles = [root]
    count = 0
    for handle in handles:
        try:
            if sim.getObjectType(int(handle)) != sim.object_shape_type:
                continue
            set_static_shape(sim, int(handle), respondable=respondable, detectable=detectable)
            count += 1
        except Exception:
            pass
    return count


def remove_tree_scripts(sim, root: int) -> int:
    try:
        handles = sim.getObjectsInTree(root, sim.object_script_type, 0)
    except Exception:
        handles = []
    removed = 0
    for handle in handles:
        try:
            sim.removeObjects([int(handle)])
            removed += 1
        except Exception:
            pass
    return removed


def get_model_aabb(sim, root: int) -> tuple[float, float, float, float, float, float] | None:
    try:
        shapes = sim.getObjectsInTree(root, sim.object_shape_type, 0)
    except Exception:
        shapes = []
    if not shapes:
        return None

    xs: list[float] = []
    ys: list[float] = []
    zs: list[float] = []
    for shape in shapes:
        try:
            min_x = sim.getObjectFloatParam(int(shape), sim.objfloatparam_objbbox_min_x)
            min_y = sim.getObjectFloatParam(int(shape), sim.objfloatparam_objbbox_min_y)
            min_z = sim.getObjectFloatParam(int(shape), sim.objfloatparam_objbbox_min_z)
            max_x = sim.getObjectFloatParam(int(shape), sim.objfloatparam_objbbox_max_x)
            max_y = sim.getObjectFloatParam(int(shape), sim.objfloatparam_objbbox_max_y)
            max_z = sim.getObjectFloatParam(int(shape), sim.objfloatparam_objbbox_max_z)
            matrix = sim.getObjectMatrix(int(shape), sim.handle_world)
        except Exception:
            continue
        for x in (min_x, max_x):
            for y in (min_y, max_y):
                for z in (min_z, max_z):
                    xs.append(matrix[0] * x + matrix[1] * y + matrix[2] * z + matrix[3])
                    ys.append(matrix[4] * x + matrix[5] * y + matrix[6] * z + matrix[7])
                    zs.append(matrix[8] * x + matrix[9] * y + matrix[10] * z + matrix[11])

    if not zs:
        return None
    return min(xs), max(xs), min(ys), max(ys), min(zs), max(zs)


def place_model_on_floor(sim, root: int, target_z: float = 0.045) -> None:
    aabb = get_model_aabb(sim, root)
    if aabb is None:
        return
    _, _, _, _, min_z, _ = aabb
    position = sim.getObjectPosition(root, sim.handle_world)
    position[2] += target_z - min_z
    sim.setObjectPosition(root, position, sim.handle_world)


def create_text(
    sim,
    alias: str,
    text: str,
    position: tuple[float, float, float],
    parent: int,
    *,
    height: float = 0.18,
    color: tuple[float, float, float] = (0.04, 0.07, 0.10),
    orientation: tuple[float, float, float] = (0.0, 0.0, 0.0),
) -> int:
    try:
        handle = sim.generateTextShape(text, list(color), height, True, None)
        sim.setObjectAlias(handle, alias)
        sim.setObjectPosition(handle, list(position))
        sim.setObjectOrientation(handle, list(orientation))
        sim.setObjectParent(handle, parent, True)
        return handle
    except Exception:
        return create_box(
            sim,
            alias,
            (0.40, 0.04, 0.08),
            position,
            color,
            parent,
            respondable=False,
            detectable=False,
        )


def create_route_segment(
    sim,
    alias: str,
    start: tuple[float, float],
    end: tuple[float, float],
    parent: int,
    *,
    width: float = 0.16,
    color: tuple[float, float, float] = (0.04, 0.43, 0.72),
    z: float = 0.025,
    arrow: bool = True,
    dashed: bool = False,
) -> int:
    sx, sy = start
    ex, ey = end
    dx = ex - sx
    dy = ey - sy
    length = math.hypot(dx, dy)
    angle = math.atan2(dy, dx)
    if dashed and length > 0.30:
        dash_len = min(0.46, max(0.24, length * 0.22))
        gap = dash_len * 0.55
        step = dash_len + gap
        count = max(1, int(math.floor(length / step)))
        segment = -1
        for i in range(count + 1):
            center_dist = min(length - dash_len / 2.0, dash_len / 2.0 + i * step)
            if center_dist <= 0.0 or center_dist >= length:
                continue
            cx = sx + math.cos(angle) * center_dist
            cy = sy + math.sin(angle) * center_dist
            handle = create_box(
                sim,
                f"{alias}_Dash_{i + 1:02d}",
                (dash_len, width, 0.018),
                (cx, cy, z),
                color,
                parent,
                respondable=False,
                detectable=False,
                orientation=(0.0, 0.0, angle),
            )
            if segment == -1:
                segment = handle
    else:
        segment = create_box(
            sim,
            alias,
            (length, width, 0.025),
            ((sx + ex) / 2.0, (sy + ey) / 2.0, z),
            color,
            parent,
            respondable=False,
            detectable=False,
            orientation=(0.0, 0.0, angle),
        )
    if arrow and length > 0.8:
        tip_x = sx + 0.72 * dx
        tip_y = sy + 0.72 * dy
        arm_len = 0.32
        for side, sign in (("L", 1), ("R", -1)):
            arm_angle = angle + math.pi + sign * math.radians(34.0)
            cx = tip_x + 0.5 * arm_len * math.cos(arm_angle)
            cy = tip_y + 0.5 * arm_len * math.sin(arm_angle)
            create_box(
                sim,
                f"{alias}_Arrow_{side}",
                (arm_len, max(0.035, width * 0.35), 0.032),
                (cx, cy, z + 0.026),
                color,
                parent,
                respondable=False,
                detectable=False,
                orientation=(0.0, 0.0, arm_angle),
            )
    return segment


def create_pallet_stack(sim, alias: str, x: float, y: float, parent: int, color: tuple[float, float, float]) -> None:
    create_box(sim, f"{alias}_BasePallet", (0.80, 0.55, 0.12), (x, y, 0.09), (0.56, 0.35, 0.16), parent)
    for i in range(3):
        create_box(
            sim,
            f"{alias}_Crate_{i + 1}",
            (0.68 - i * 0.05, 0.42, 0.24),
            (x, y, 0.26 + i * 0.23),
            color,
            parent,
        )


def add_warehouse_shell(sim, group: int) -> None:
    floor_x, floor_y = FLOOR_SIZE
    half_x = floor_x / 2.0
    half_y = floor_y / 2.0
    create_box(sim, "A1_Floor_Alestis_HTP_Cell", (floor_x, floor_y, 0.04), (0.0, 0.0, -0.02), (0.70, 0.72, 0.70), group, respondable=True, detectable=True)
    create_box(sim, "A1_Floor_Boundary_North", (floor_x - 0.40, 0.05, 0.035), (0.0, half_y - 0.35, 0.032), (0.86, 0.16, 0.10), group, respondable=False, detectable=False)
    create_box(sim, "A1_Floor_Boundary_South", (floor_x - 0.40, 0.05, 0.035), (0.0, -half_y + 0.35, 0.032), (0.86, 0.16, 0.10), group, respondable=False, detectable=False)
    create_box(sim, "A1_Floor_Boundary_West", (0.05, floor_y - 0.80, 0.035), (-half_x + 0.32, 0.0, 0.032), (0.86, 0.16, 0.10), group, respondable=False, detectable=False)
    create_box(sim, "A1_Floor_Boundary_East", (0.05, floor_y - 0.80, 0.035), (half_x - 0.32, 0.0, 0.032), (0.86, 0.16, 0.10), group, respondable=False, detectable=False)
    create_box(sim, "A1_Wall_North", (floor_x, 0.08, 2.2), (0.0, half_y - 0.05, 1.10), (0.74, 0.78, 0.80), group)
    create_box(sim, "A1_Wall_South_Low", (floor_x, 0.05, 0.55), (0.0, -half_y + 0.03, 0.275), (0.52, 0.58, 0.62), group)
    create_box(sim, "A1_Wall_West", (0.08, floor_y, 2.2), (-half_x, 0.0, 1.10), (0.74, 0.78, 0.80), group)
    create_box(sim, "A1_Wall_East", (0.08, floor_y, 2.2), (half_x, 0.0, 1.10), (0.74, 0.78, 0.80), group)

    for x in (-10.0, -6.0, -2.0, 2.0, 6.0, 10.0):
        for y in (-half_y + 1.05, half_y - 1.05):
            create_box(sim, f"A1_SteelColumn_{x}_{y}", (0.16, 0.16, 2.65), (x, y, 1.325), (0.19, 0.23, 0.25), group)
    for y in (-half_y + 1.20, half_y - 1.20):
        create_box(sim, f"A1_OverheadCrane_Rail_{y}", (floor_x - 2.0, 0.10, 0.10), (0.0, y, 2.75), (0.08, 0.10, 0.12), group, respondable=False, detectable=False)
    create_box(sim, "A1_OverheadCrane_Bridge", (0.18, floor_y - 3.0, 0.16), (3.15, 0.0, 2.62), (0.90, 0.66, 0.12), group, respondable=False, detectable=False)
    create_box(sim, "A1_OverheadCrane_Hoist", (0.32, 0.30, 0.24), (3.15, -0.85, 2.32), (0.18, 0.20, 0.22), group, respondable=False, detectable=False)
    create_cylinder(sim, "A1_OverheadCrane_Hook", (0.08, 0.08, 0.38), (3.15, -0.85, 2.02), (0.04, 0.04, 0.05), group, respondable=False, detectable=False)

    for i, x in enumerate((-9.6, -5.8, -2.0, 1.8, 5.6, 9.4)):
        create_box(sim, f"A1_CeilingLight_{i + 1}", (1.35, 0.22, 0.03), (x, -half_y + 0.65, 2.45), (1.00, 0.96, 0.72), group, respondable=False, detectable=False)
        create_box(sim, f"A1_CeilingLight_N_{i + 1}", (1.35, 0.22, 0.03), (x, half_y - 0.65, 2.45), (1.00, 0.96, 0.72), group, respondable=False, detectable=False)


def add_logistics_area(sim, group: int) -> None:
    create_box(sim, "A1_Logistics_Zone_Floor", (5.2, 4.4, 0.03), (-6.1, 1.20, 0.015), (0.56, 0.62, 0.58), group, respondable=False, detectable=False)
    create_text(sim, "A1_Label_Logistics", "LOGISTICA / KITTING", (-6.3, 3.20, 0.08), group, height=0.22, color=(0.03, 0.13, 0.18))

    for i, y in enumerate((-0.25, 0.90, 2.05)):
        create_box(sim, f"A1_Rack_Frame_{i + 1}", (3.5, 0.18, 1.55), (-6.25, y, 0.78), (0.18, 0.22, 0.25), group)
        create_box(sim, f"A1_Rack_Shelf_Low_{i + 1}", (3.4, 0.58, 0.06), (-6.25, y, 0.36), (0.90, 0.64, 0.24), group)
        create_box(sim, f"A1_Rack_Shelf_High_{i + 1}", (3.4, 0.58, 0.06), (-6.25, y, 1.02), (0.90, 0.64, 0.24), group)
        for j, x in enumerate((-7.25, -6.30, -5.35)):
            create_box(sim, f"A1_Kit_Box_{i + 1}_{j + 1}", (0.54, 0.32, 0.24), (x, y, 0.53), (0.14, 0.42, 0.56), group)
            create_box(sim, f"A1_Tool_Box_{i + 1}_{j + 1}", (0.48, 0.30, 0.22), (x, y, 1.18), (0.68, 0.18, 0.12), group)

    create_pallet_stack(sim, "A1_Consumables_Pallet", -4.35, 3.45, group, (0.20, 0.50, 0.72))
    create_pallet_stack(sim, "A1_Sealant_Pallet", -7.85, 3.55, group, (0.76, 0.52, 0.18))

    create_box(sim, "A1_RFID_Gate_Left_Post", (0.12, 0.12, 1.45), (-3.35, -0.55, 0.725), (0.04, 0.20, 0.32), group)
    create_box(sim, "A1_RFID_Gate_Right_Post", (0.12, 0.12, 1.45), (-3.35, 0.55, 0.725), (0.04, 0.20, 0.32), group)
    create_box(sim, "A1_RFID_Gate_Top", (0.16, 1.24, 0.12), (-3.35, 0.0, 1.40), (0.04, 0.20, 0.32), group)
    create_box(sim, "A1_RFID_Status_Green", (0.05, 0.25, 0.12), (-3.42, 0.0, 1.55), (0.04, 0.70, 0.24), group, respondable=False, detectable=False)
    create_text(sim, "A1_Label_RFID", "RFID / QR", (-3.55, -1.05, 0.08), group, height=0.16, color=(0.04, 0.15, 0.25))

    create_box(sim, "A1_HMI_Desk", (1.0, 0.55, 0.72), (-8.45, -2.15, 0.36), (0.20, 0.22, 0.24), group)
    create_box(sim, "A1_HMI_Screen", (0.74, 0.05, 0.46), (-8.45, -1.83, 0.96), (0.02, 0.06, 0.08), group, respondable=False, detectable=False)
    create_box(sim, "A1_HMI_Screen_Route", (0.48, 0.055, 0.055), (-8.45, -1.86, 1.03), (0.02, 0.50, 0.68), group, respondable=False, detectable=False)
    create_text(sim, "A1_Label_HMI", "HMI / SUPERVISION", (-8.35, -2.95, 0.08), group, height=0.15, color=(0.02, 0.10, 0.16))


def add_htp_workstation(sim, group: int) -> None:
    create_box(sim, "A1_Station_19_1_Floor", (8.4, 7.6, 0.03), (4.65, 0.35, 0.016), (0.60, 0.63, 0.66), group, respondable=False, detectable=False)
    create_box(sim, "A1_Station_19_1_Safety_Border_N", (8.4, 0.07, 0.05), (4.65, 4.15, 0.06), (0.96, 0.76, 0.12), group, respondable=False, detectable=False)
    create_box(sim, "A1_Station_19_1_Safety_Border_S", (8.4, 0.07, 0.05), (4.65, -3.45, 0.06), (0.96, 0.76, 0.12), group, respondable=False, detectable=False)
    create_box(sim, "A1_Station_19_1_Safety_Border_W", (0.07, 7.6, 0.05), (0.45, 0.35, 0.06), (0.96, 0.76, 0.12), group, respondable=False, detectable=False)
    create_box(sim, "A1_Station_19_1_Safety_Border_E", (0.07, 7.6, 0.05), (8.85, 0.35, 0.06), (0.96, 0.76, 0.12), group, respondable=False, detectable=False)
    create_text(sim, "A1_Label_Station_19_1", "SECCION 19.1 / HTP A320", (4.55, 3.70, 0.09), group, height=0.22, color=(0.05, 0.11, 0.17))

    create_cylinder(
        sim,
        "A1_A320_Section_19_1_Fuselage_Proxy",
        (1.25, 1.25, 1.75),
        (2.20, 0.15, 1.05),
        (0.63, 0.66, 0.68),
        group,
        orientation=(0.0, math.radians(90), 0.0),
    )
    create_cylinder(
        sim,
        "A1_A320_TailCone_Construction_Section",
        (0.85, 0.85, 1.35),
        (1.15, 0.15, 1.05),
        (0.56, 0.59, 0.61),
        group,
        respondable=False,
        orientation=(0.0, math.radians(90), 0.0),
    )
    for i, x in enumerate((1.48, 1.92, 2.36, 2.80), start=1):
        create_cylinder(
            sim,
            f"A1_A320_Bulkhead_Frame_{i}",
            (1.34, 1.34, 0.035),
            (x, 0.15, 1.05),
            (0.18, 0.22, 0.25),
            group,
            respondable=False,
            orientation=(0.0, math.radians(90), 0.0),
        )
    for i, (x, z) in enumerate(((1.70, 1.72), (2.25, 1.76), (2.80, 1.70)), start=1):
        create_box(
            sim,
            f"A1_A320_Open_Skin_Panel_{i}",
            (0.36, 0.035, 0.22),
            (x, -0.48, z),
            (0.10, 0.13, 0.15),
            group,
            respondable=False,
            orientation=(0.0, 0.0, math.radians(0.0)),
        )
    create_box(sim, "A1_HTP_Center_Box", (1.55, 1.10, 0.16), (4.15, 0.15, 1.10), (0.82, 0.84, 0.84), group)
    create_box(sim, "A1_HTP_Left_Panel", (1.25, 2.60, 0.12), (4.25, -1.62, 1.09), (0.78, 0.80, 0.81), group)
    create_box(sim, "A1_HTP_Right_Panel", (1.25, 2.60, 0.12), (4.25, 1.92, 1.09), (0.78, 0.80, 0.81), group)
    create_box(sim, "A1_HTP_Left_Tip", (0.92, 0.58, 0.10), (4.25, -3.20, 1.08), (0.72, 0.75, 0.76), group)
    create_box(sim, "A1_HTP_Right_Tip", (0.92, 0.58, 0.10), (4.25, 3.50, 1.08), (0.72, 0.75, 0.76), group)
    create_box(sim, "A1_HTP_Trailing_Edge", (0.10, 6.30, 0.06), (3.42, 0.15, 1.17), (0.26, 0.30, 0.32), group)
    create_box(sim, "A1_HTP_Leading_Edge", (0.12, 6.20, 0.06), (4.98, 0.15, 1.17), (0.38, 0.42, 0.44), group)
    create_cylinder(
        sim,
        "A1_HTP_Rounded_Leading_Edge_Tube",
        (0.16, 0.16, 6.05),
        (5.05, 0.15, 1.18),
        (0.68, 0.71, 0.73),
        group,
        respondable=False,
        orientation=(math.radians(90), 0.0, 0.0),
    )
    create_cylinder(
        sim,
        "A1_HTP_Trailing_Edge_Slim_Tube",
        (0.07, 0.07, 6.15),
        (3.34, 0.15, 1.18),
        (0.20, 0.24, 0.27),
        group,
        respondable=False,
        orientation=(math.radians(90), 0.0, 0.0),
    )
    for idx, y in enumerate((-2.95, -2.35, -1.75, -1.15, -0.55, 0.85, 1.45, 2.05, 2.65, 3.25), start=1):
        create_box(
            sim,
            f"A1_HTP_Internal_Rib_{idx:02d}",
            (1.34, 0.035, 0.18),
            (4.22, y, 1.23),
            (0.28, 0.32, 0.35),
            group,
            respondable=False,
        )
    for idx, y in enumerate((-2.40, -1.30, 1.30, 2.40), start=1):
        create_box(
            sim,
            f"A1_HTP_Removable_Skin_Panel_{idx}",
            (0.72, 0.32, 0.028),
            (4.62, y, 1.32),
            (0.92, 0.76, 0.26),
            group,
            respondable=False,
        )

    for y in (-2.55, -0.95, 0.95, 2.55):
        create_box(sim, f"A1_HTP_Jig_Base_{y}", (0.44, 0.22, 0.88), (4.25, y, 0.54), (0.06, 0.18, 0.30), group)
        create_box(sim, f"A1_HTP_Jig_Cradle_{y}", (1.10, 0.18, 0.10), (4.25, y, 1.00), (0.90, 0.62, 0.14), group)

    for i, y in enumerate((-2.05, -1.55, 1.55, 2.05)):
        create_box(sim, f"A1_Work_Platform_{i + 1}", (0.92, 0.36, 0.36), (6.20, y, 0.18), (0.30, 0.34, 0.36), group)
        create_box(sim, f"A1_Work_Platform_Rail_{i + 1}", (0.92, 0.045, 0.52), (6.20, y + 0.22, 0.60), (0.90, 0.72, 0.12), group)

    create_box(sim, "A1_Quality_Table", (0.85, 0.55, 0.70), (7.35, -1.75, 0.35), (0.30, 0.28, 0.25), group)
    create_box(sim, "A1_Tablet_QA", (0.32, 0.04, 0.24), (7.35, -1.45, 0.90), (0.03, 0.05, 0.06), group, respondable=False, detectable=False)
    create_box(sim, "A1_Tool_Trolley", (0.55, 0.42, 0.70), (7.45, 1.78, 0.35), (0.70, 0.24, 0.16), group)

    create_sphere(sim, "A1_FOD_Object_Red_Bit", (0.09, 0.09, 0.04), (5.85, -0.92, 0.085), (0.90, 0.08, 0.06), group)
    create_box(sim, "A1_FOD_Inspection_Marker", (0.46, 0.46, 0.018), (5.85, -0.92, 0.035), (0.96, 0.76, 0.12), group, respondable=False, detectable=False)
    create_text(sim, "A1_Label_FOD", "FOD", (6.25, -0.92, 0.10), group, height=0.15, color=(0.58, 0.04, 0.03))


def create_simple_operator(sim, alias: str, x: float, y: float, yaw_deg: float, group: int, vest: tuple[float, float, float]) -> int:
    frame = create_dummy_oriented(sim, f"{alias}_Frame", (x, y, 0.0), yaw_deg, group, size=0.05)
    create_cylinder_local(sim, f"{alias}_Torso", (0.28, 0.28, 0.78), (0.0, 0.0, 0.92), vest, frame, respondable=False)
    create_sphere_local(sim, f"{alias}_Head", (0.23, 0.23, 0.23), (0.0, 0.0, 1.42), (0.72, 0.55, 0.42), frame, respondable=False)
    create_box_local(sim, f"{alias}_Helmet", (0.30, 0.26, 0.07), (0.0, 0.0, 1.58), (0.96, 0.82, 0.12), frame, respondable=False)
    create_box_local(sim, f"{alias}_Leg_L", (0.08, 0.08, 0.65), (-0.08, 0.0, 0.36), (0.08, 0.10, 0.13), frame, respondable=False)
    create_box_local(sim, f"{alias}_Leg_R", (0.08, 0.08, 0.65), (0.08, 0.0, 0.36), (0.08, 0.10, 0.13), frame, respondable=False)
    create_box_local(sim, f"{alias}_Arm_L", (0.06, 0.06, 0.50), (-0.22, 0.0, 0.92), (0.72, 0.55, 0.42), frame, respondable=False, orientation=(0.0, math.radians(14), 0.0))
    create_box_local(sim, f"{alias}_Arm_R", (0.06, 0.06, 0.50), (0.22, 0.0, 0.92), (0.72, 0.55, 0.42), frame, respondable=False, orientation=(0.0, math.radians(-14), 0.0))
    return frame


def add_operator_model(
    sim,
    alias: str,
    model_name: str,
    position: tuple[float, float, float],
    yaw_deg: float,
    group: int,
    fallback_vest: tuple[float, float, float],
) -> int:
    path = MODELS_DIR / "people" / model_name
    if path.exists():
        try:
            model = int(sim.loadModel(str(path)))
            if model >= 0:
                sim.setObjectAlias(model, alias)
                sim.setObjectPosition(model, list(position))
                sim.setObjectOrientation(model, [0.0, 0.0, math.radians(yaw_deg)])
                try:
                    sim.setObjectParent(model, group, True)
                except Exception:
                    pass
                set_tree_static(sim, model, respondable=False, detectable=True)
                return model
        except Exception:
            pass
    return create_simple_operator(sim, alias, position[0], position[1], yaw_deg, group, fallback_vest)


def add_tool_handoff_visuals(sim, group: int) -> int:
    """Small moving tool used to show human -> AMR -> human handoff."""
    tool_frame = create_dummy(sim, "A1_Tool_Handoff_TorqueWrench_Frame", (-4.05, 0.90, 1.18), group, size=0.045)
    create_box_local(
        sim,
        "A1_Tool_Handoff_TorqueWrench_Handle",
        (0.42, 0.055, 0.055),
        (0.0, 0.0, 0.0),
        (0.05, 0.07, 0.08),
        tool_frame,
        respondable=False,
        detectable=True,
    )
    create_box_local(
        sim,
        "A1_Tool_Handoff_TorqueWrench_Head",
        (0.12, 0.18, 0.06),
        (0.24, 0.0, 0.0),
        (0.88, 0.55, 0.08),
        tool_frame,
        respondable=False,
        detectable=True,
    )
    create_box(sim, "A1_Tool_Handoff_LoadZone", (0.70, 0.44, 0.025), (-6.96, -1.24, 0.082), (0.04, 0.62, 0.34), group, respondable=False, detectable=False)
    create_text(sim, "A1_Label_ToolLoad", "1. operario carga herramienta", (-7.55, -0.72, 0.10), group, height=0.11, color=(0.02, 0.28, 0.12))
    create_box(sim, "A1_Tool_Handoff_PickupZone", (0.78, 0.48, 0.025), (5.55, -1.18, 0.082), (0.03, 0.36, 0.52), group, respondable=False, detectable=False)
    create_text(sim, "A1_Label_ToolPickup", "2. operario recoge herramienta", (5.02, -0.58, 0.10), group, height=0.11, color=(0.02, 0.16, 0.24))
    return tool_frame


def add_human_task_paths(sim, group: int) -> None:
    task_paths = {
        "A1_Human_Path_Logistics": [(-5.55, -1.45), (-4.55, -1.05), (-3.35, -0.55), (-4.55, -1.05), (-5.55, -1.45)],
        "A1_Human_Path_Kitting_Handoff": [(-4.05, 0.90), (-5.20, 0.30), (-6.85, -1.10), (-5.25, -0.30), (-4.05, 0.90)],
        "A1_Human_Path_QA_Delivery": [(7.10, -1.35), (6.30, -1.06), (5.55, -1.05), (6.22, -1.52), (7.10, -1.35)],
        "A1_Human_Path_FOD_Check": [(6.35, -0.55), (5.85, -0.92), (5.82, 0.08), (6.28, 0.42), (6.35, -0.55)],
        "A1_Human_Path_Supervisor": [(-8.05, -2.00), (-7.20, -3.30), (-7.88, -1.30), (-8.05, -2.00)],
        "A1_Human_Path_Crossing": [(-0.55, -1.35), (-0.55, -0.55), (-0.55, 0.38), (0.08, 0.38)],
    }
    colors = {
        "A1_Human_Path_Logistics": (0.12, 0.52, 0.18),
        "A1_Human_Path_Kitting_Handoff": (0.02, 0.45, 0.70),
        "A1_Human_Path_QA_Delivery": (0.86, 0.64, 0.08),
        "A1_Human_Path_FOD_Check": (0.70, 0.23, 0.10),
        "A1_Human_Path_Supervisor": (0.18, 0.34, 0.22),
        "A1_Human_Path_Crossing": (0.90, 0.18, 0.12),
    }
    for alias, points in task_paths.items():
        for idx, (start, end) in enumerate(zip(points, points[1:]), start=1):
            create_route_segment(sim, f"{alias}_{idx}", start, end, group, width=0.045, color=colors[alias], z=0.070, dashed=True)
    create_text(sim, "A1_Label_HumanTaskPaths", "rutas humanas: carga, entrega, calidad, FOD y cruce", (-3.65, 1.92, 0.10), group, height=0.12, color=(0.05, 0.20, 0.12))


def add_human_task_animation(sim, group: int) -> int:
    """Animate people and the handoff tool during simulation playback."""
    script = """-- Human task choreography for the AMR-FOD-Kitting pilot.
-- People move as plant operators: kitting loads a tool, the AMR carries it,
-- another operator collects it at HTP, and a crossing operator forces stop/avoidance.
local function get(path)
  local ok, h = pcall(sim.getObject, path)
  if ok then return h end
  return -1
end

local function lerp(a, b, u)
  if u < 0 then u = 0 end
  if u > 1 then u = 1 end
  return a + (b - a) * u
end

local function setPose(h, x, y, yaw)
  if h < 0 then return end
  sim.setObjectPosition(h, {x, y, 0.0}, sim.handle_world)
  sim.setObjectOrientation(h, {0.0, 0.0, yaw}, sim.handle_world)
end

local function setTool(x, y, z, yaw)
  if tool < 0 then return end
  sim.setObjectPosition(tool, {x, y, z}, sim.handle_world)
  sim.setObjectOrientation(tool, {0.0, 0.0, yaw}, sim.handle_world)
end

local function segmentPose(points, t, period, offset)
  local tt = (t + offset) % period
  local n = #points
  local seg = period / (n - 1)
  local idx = math.floor(tt / seg) + 1
  if idx >= n then idx = n - 1 end
  local u = (tt - (idx - 1) * seg) / seg
  local p = points[idx]
  local q = points[idx + 1]
  local x = lerp(p[1], q[1], u)
  local y = lerp(p[2], q[2], u)
  local yaw = math.atan2(q[2] - p[2], q[1] - p[1])
  return x, y, yaw
end

function sysCall_init()
  logistics = get('/A1_Operator_Logistics_Walking')
  qa = get('/A1_Operator_QA_Tablet')
  fod = get('/A1_Operator_FOD_Check')
  kitting = get('/A1_Operator_Kitting_Rack')
  supervisor = get('/A1_Operator_HMI_Supervisor')
  crossing = get('/A1_Operator_Human_Crossing')
  amr = get('/A1_AMR_Pilot_01_RB_KAIROS_Class_Frame')
  tool = get('/A1_Tool_Handoff_TorqueWrench_Frame')

  logisticsPts = {{-5.55,-1.45},{-4.55,-1.05},{-3.35,-0.55},{-4.55,-1.05},{-5.55,-1.45}}
  kittingPts = {{-4.05,0.90},{-5.20,0.30},{-6.85,-1.10},{-5.25,-0.30},{-4.05,0.90}}
  qaPts = {{7.10,-1.35},{6.30,-1.06},{5.55,-1.05},{6.22,-1.52},{7.10,-1.35}}
  fodPts = {{6.35,-0.55},{5.85,-0.92},{5.82,0.08},{6.28,0.42},{6.35,-0.55}}
  supervisorPts = {{-8.05,-2.00},{-7.20,-3.30},{-7.88,-1.30},{-8.05,-2.00}}
end

function sysCall_actuation()
  local t = sim.getSimulationTime()

  local x,y,yaw = segmentPose(logisticsPts, t, 18.0, 2.0)
  setPose(logistics, x, y, yaw)

  x,y,yaw = segmentPose(kittingPts, t, 22.0, 0.0)
  setPose(kitting, x, y, yaw)

  x,y,yaw = segmentPose(qaPts, t, 20.0, 11.0)
  setPose(qa, x, y, yaw)

  x,y,yaw = segmentPose(fodPts, t, 16.0, 5.0)
  setPose(fod, x, y, yaw)

  x,y,yaw = segmentPose(supervisorPts, t, 24.0, 7.0)
  setPose(supervisor, x, y, yaw)

  local c = t % 24.0
  if c < 9.5 then
    setPose(crossing, -0.55, -1.35, math.rad(90))
  elseif c < 13.5 then
    local u = (c - 9.5) / 4.0
    setPose(crossing, -0.55, lerp(-1.35, 0.38, u), math.rad(90))
  elseif c < 17.0 then
    setPose(crossing, lerp(-0.55, 0.08, (c - 13.5) / 3.5), 0.38, math.rad(0))
  elseif c < 21.5 then
    local u = (c - 17.0) / 4.5
    setPose(crossing, lerp(0.08, -0.55, u), lerp(0.38, -1.35, u), math.rad(-112))
  else
    setPose(crossing, -0.55, -1.35, math.rad(90))
  end

  if tool >= 0 then
    if t < 5.8 then
      local xh,yh,yawh = segmentPose(kittingPts, t, 22.0, 0.0)
      setTool(xh + 0.18 * math.cos(yawh), yh + 0.18 * math.sin(yawh), 1.12, yawh)
    elseif t < 8.0 then
      local u = (t - 5.8) / 2.2
      setTool(lerp(-6.85, -7.10, u), lerp(-1.10, -1.20, u), lerp(1.12, 0.76, u), math.rad(88))
    elseif t < 30.5 and amr >= 0 then
      local p = sim.getObjectPosition(amr, sim.handle_world)
      local e = sim.getObjectOrientation(amr, sim.handle_world)
      setTool(p[1], p[2], 0.82, e[3])
    elseif t < 34.5 then
      local u = (t - 30.5) / 4.0
      setTool(lerp(5.60, 5.55, u), lerp(-1.05, -1.05, u), lerp(0.82, 1.12, u), math.rad(178))
    else
      local xq,yq,yawq = segmentPose(qaPts, t, 20.0, 11.0)
      setTool(xq - 0.16 * math.cos(yawq), yq - 0.16 * math.sin(yawq), 1.12, yawq)
    end
  end
end
"""
    script_handle = sim.createScript(sim.scripttype_simulation, script, 0, "lua")
    sim.setObjectAlias(script_handle, "A1_Human_Task_Animation_Script")
    sim.setObjectParent(script_handle, group, True)
    return script_handle


def add_human_operators(sim, group: int) -> list[int]:
    operators: list[int] = []
    operators.append(add_operator_model(sim, "A1_Operator_Logistics_Walking", "Walking Bill.ttm", (-4.95, -2.05, 0.0), 45.0, group, (0.06, 0.35, 0.82)))
    operators.append(add_operator_model(sim, "A1_Operator_QA_Tablet", "Working Bill.ttm", (7.10, -1.35, 0.0), -122.0, group, (0.92, 0.76, 0.12)))
    operators.append(add_operator_model(sim, "A1_Operator_FOD_Check", "Working Bill.ttm", (6.35, -0.55, 0.0), -158.0, group, (0.92, 0.76, 0.12)))
    operators.append(add_operator_model(sim, "A1_Operator_Kitting_Rack", "Standing Bill.ttm", (-4.05, 0.90, 0.0), 180.0, group, (0.06, 0.35, 0.82)))
    operators.append(add_operator_model(sim, "A1_Operator_HMI_Supervisor", "Standing Bill.ttm", (-8.05, -2.00, 0.0), -70.0, group, (0.16, 0.42, 0.22)))
    operators.append(add_operator_model(sim, "A1_Operator_Human_Crossing", "Standing Bill.ttm", (HUMAN_AVOIDANCE_POINT[0], HUMAN_AVOIDANCE_POINT[1], 0.0), 88.0, group, (0.90, 0.18, 0.12)))

    create_cylinder(
        sim,
        "A1_Human_Safety_Stop_Zone",
        (HUMAN_SAFETY_RADIUS_M * 2.0, HUMAN_SAFETY_RADIUS_M * 2.0, 0.018),
        (HUMAN_AVOIDANCE_POINT[0], HUMAN_AVOIDANCE_POINT[1], 0.062),
        (0.92, 0.22, 0.10),
        group,
        respondable=False,
        detectable=False,
    )
    create_cylinder(
        sim,
        "A1_Human_Clearance_Envelope",
        (HUMAN_SAFETY_RADIUS_M * 2.65, HUMAN_SAFETY_RADIUS_M * 2.65, 0.012),
        (HUMAN_AVOIDANCE_POINT[0], HUMAN_AVOIDANCE_POINT[1], 0.052),
        (0.96, 0.72, 0.10),
        group,
        respondable=False,
        detectable=False,
    )
    create_text(sim, "A1_Label_HumanAvoidance", "humano detectado: AMR para y esquiva", (-1.42, 0.18, 0.10), group, height=0.13, color=(0.42, 0.04, 0.02))

    add_human_task_paths(sim, group)
    add_tool_handoff_visuals(sim, group)
    add_human_task_animation(sim, group)
    create_text(sim, "A1_Label_HumanOperators", "operarios animados: carga, cruce, entrega, calidad y FOD", (-2.20, -1.42, 0.10), group, height=0.13, color=(0.06, 0.24, 0.10))
    return operators


def create_amr_proxy(
    sim,
    alias: str,
    x: float,
    y: float,
    yaw_deg: float,
    parent: int,
    *,
    color: tuple[float, float, float],
    future: bool = False,
) -> int:
    yaw = math.radians(yaw_deg)
    robot = create_box(
        sim,
        f"{alias}_Body",
        (0.95, 0.68, 0.28),
        (x, y, 0.20),
        color if not future else (0.46, 0.50, 0.54),
        parent,
        respondable=False,
        detectable=True,
        orientation=(0.0, 0.0, yaw),
    )
    create_box(sim, f"{alias}_TopTray", (0.78, 0.50, 0.12), (x, y, 0.44), (0.16, 0.18, 0.18), parent, respondable=False, orientation=(0.0, 0.0, yaw))
    create_box(sim, f"{alias}_KitLoad", (0.54, 0.36, 0.20), (x, y, 0.63), (0.14, 0.42, 0.56), parent, respondable=False, orientation=(0.0, 0.0, yaw))
    create_cylinder(sim, f"{alias}_LiDAR", (0.16, 0.16, 0.08), (x + 0.26 * math.cos(yaw), y + 0.26 * math.sin(yaw), 0.58), (0.02, 0.06, 0.08), parent, respondable=False, detectable=False)
    create_box(sim, f"{alias}_RGBD_Camera", (0.13, 0.08, 0.08), (x + 0.48 * math.cos(yaw), y + 0.48 * math.sin(yaw), 0.50), (0.02, 0.02, 0.03), parent, respondable=False, orientation=(0.0, 0.0, yaw))
    create_box(sim, f"{alias}_RFID_Antenna", (0.04, 0.20, 0.30), (x - 0.36 * math.sin(yaw), y + 0.36 * math.cos(yaw), 0.58), (0.04, 0.20, 0.32), parent, respondable=False, orientation=(0.0, 0.0, yaw))
    create_cylinder(sim, f"{alias}_SafetyZone", (1.65, 1.65, 0.012), (x, y, 0.035), (0.90, 0.82, 0.18), parent, respondable=False, detectable=False)
    return robot


def create_animated_amr_demo(sim, group: int) -> int:
    start_x, start_y, _ = MISSION_ROUTE_POINTS[0]
    next_x, next_y, _ = MISSION_ROUTE_POINTS[1]
    yaw_deg = math.degrees(math.atan2(next_y - start_y, next_x - start_x))
    frame = create_dummy_oriented(sim, "A1_AMR_Pilot_01_RB_KAIROS_Class_Frame", (start_x, start_y, 0.0), yaw_deg, group, size=0.08)
    youbot_path = MODELS_DIR / "robots" / "mobile" / "KUKA YouBot.ttm"
    youbot_loaded = False
    if youbot_path.exists():
        try:
            youbot = int(sim.loadModel(str(youbot_path)))
            sim.setObjectAlias(youbot, "A1_AMR_Pilot_01_KUKA_YouBot_Model")
            remove_tree_scripts(sim, youbot)
            set_tree_static(sim, youbot, respondable=False, detectable=True)
            native_orientation = sim.getObjectOrientation(youbot, sim.handle_world)
            # Keep the stock YouBot attitude in world coordinates, then attach
            # it to the animated AMR frame while preserving that pose. The
            # model's native front points along the first mission segment
            # (dock -> kitting); the parent frame then rotates it with the
            # planned AMR route.
            sim.setObjectPosition(youbot, [start_x, start_y, 0.0], sim.handle_world)
            sim.setObjectOrientation(youbot, list(native_orientation), sim.handle_world)
            place_model_on_floor(sim, youbot, target_z=0.055)
            sim.setObjectParent(youbot, frame, True)
            youbot_loaded = True
        except Exception:
            youbot_loaded = False

    if not youbot_loaded:
        create_box_local(sim, "A1_AMR_Pilot_01_RB_KAIROS_Class_Body", (0.95, 0.68, 0.28), (0.0, 0.0, 0.20), (0.02, 0.45, 0.62), frame, respondable=False)
    else:
        create_box_local(sim, "A1_AMR_Pilot_01_RB_KAIROS_Class_Body", (0.98, 0.72, 0.035), (0.0, 0.0, 0.08), (0.02, 0.45, 0.62), frame, respondable=False)

    create_box_local(sim, "A1_AMR_Pilot_01_RB_KAIROS_Class_TopTray", (0.72, 0.48, 0.10), (0.0, 0.0, 0.46), (0.16, 0.18, 0.18), frame, respondable=False)
    create_box_local(sim, "A1_AMR_Pilot_01_RB_KAIROS_Class_KitLoad", (0.48, 0.32, 0.16), (0.0, 0.0, 0.59), (0.14, 0.42, 0.56), frame, respondable=False)
    create_cylinder_local(sim, "A1_AMR_Pilot_01_RB_KAIROS_Class_LiDAR", (0.13, 0.13, 0.06), (0.30, 0.0, 0.64), (0.02, 0.06, 0.08), frame, respondable=False, detectable=False)
    create_box_local(sim, "A1_AMR_Pilot_01_RB_KAIROS_Class_RGBD_Camera", (0.11, 0.07, 0.07), (0.45, 0.0, 0.54), (0.02, 0.02, 0.03), frame, respondable=False)
    create_box_local(sim, "A1_AMR_Pilot_01_RB_KAIROS_Class_RFID_Antenna", (0.035, 0.16, 0.24), (0.0, 0.34, 0.55), (0.04, 0.20, 0.32), frame, respondable=False)
    create_cylinder_local(sim, "A1_AMR_Pilot_01_RB_KAIROS_Class_SafetyZone", (1.65, 1.65, 0.012), (0.0, 0.0, 0.035), (0.90, 0.82, 0.18), frame, respondable=False, detectable=False)

    lua_points = "{\n" + ",\n".join(f"    {{{x:.3f}, {y:.3f}, '{label}'}}" for x, y, label in MISSION_ROUTE_POINTS) + "\n  }"
    script = f"""-- Animated mission preview for AMR-FOD-Kitting.
-- Start simulation: the YouBot/AMR pilot follows dock -> kitting -> RFID/QR -> HTP -> FOD -> return.
function sysCall_init()
  frame = sim.getObject('/A1_AMR_Pilot_01_RB_KAIROS_Class_Frame')
  pts = {lua_points}
  speed = 0.62
  idx = 1
  pauseUntil = 0.0
  sim.setObjectPosition(frame, {{pts[1][1], pts[1][2], 0.0}}, sim.handle_world)
end

function sysCall_actuation()
  local now = sim.getSimulationTime()
  if now < pauseUntil then
    return
  end
  local p = sim.getObjectPosition(frame, sim.handle_world)
  local nextIdx = idx + 1
  if nextIdx > #pts then nextIdx = 1 end
  local tx = pts[nextIdx][1]
  local ty = pts[nextIdx][2]
  local dx = tx - p[1]
  local dy = ty - p[2]
  local dist = math.sqrt(dx * dx + dy * dy)
  if dist < 0.045 then
    idx = nextIdx
    if string.find(pts[idx][3], 'StopHumano') then
      pauseUntil = now + 1.8
    end
    return
  end
  local dt = sim.getSimulationTimeStep()
  local step = math.min(speed * dt, dist)
  local nx = p[1] + dx / dist * step
  local ny = p[2] + dy / dist * step
  sim.setObjectPosition(frame, {{nx, ny, 0.0}}, sim.handle_world)
  sim.setObjectOrientation(frame, {{0.0, 0.0, math.atan2(dy, dx)}}, sim.handle_world)
end
"""
    script_handle = sim.createScript(sim.scripttype_simulation, script, 0, "lua")
    sim.setObjectAlias(script_handle, "A1_AMR_Pilot_01_Mission_Script")
    sim.setObjectParent(script_handle, frame, True)
    return frame


def add_amr_fleet_and_routes(sim, group: int) -> None:
    mission_xy = [(x, y) for x, y, _ in MISSION_ROUTE_POINTS]
    for idx, (start, end) in enumerate(zip(mission_xy, mission_xy[1:]), start=1):
        outbound = idx <= 9
        create_route_segment(
            sim,
            f"A1_Pilot01_Mission_Route_{idx:02d}",
            start,
            end,
            group,
            width=0.105 if outbound else 0.075,
            color=(0.02, 0.43, 0.70) if outbound else (0.88, 0.50, 0.06),
            z=0.04 if outbound else 0.055,
            dashed=True,
        )

    for order, (x, y, label) in enumerate(MISSION_ROUTE_POINTS[:-1], start=1):
        color = (0.04, 0.62, 0.34) if order <= 10 else (0.92, 0.57, 0.10)
        create_cylinder(sim, f"A1_Waypoint_{order:02d}_{label}", (0.32, 0.32, 0.035), (x, y, 0.075), color, group, respondable=False, detectable=False)
        create_text(sim, f"A1_Waypoint_Label_{order:02d}_{label}", str(order), (x + 0.18, y + 0.18, 0.12), group, height=0.11, color=(0.02, 0.10, 0.15))

    create_box(sim, "A1_Pilot01_ChargingPad", (0.94, 0.76, 0.04), (-7.10, -3.75, 0.035), (0.08, 0.25, 0.32), group, respondable=False, detectable=False)
    create_box(sim, "A1_Pilot01_ChargeContact", (0.42, 0.07, 0.04), (-7.10, -3.36, 0.080), (0.94, 0.78, 0.22), group, respondable=False, detectable=False)
    create_box(sim, "A1_Pilot01_ChargingTotem", (0.18, 0.16, 0.92), (-7.78, -3.62, 0.48), (0.05, 0.12, 0.18), group, respondable=False, detectable=False)
    create_cylinder(sim, "A1_Pilot01_ChargingLight", (0.16, 0.16, 0.08), (-7.78, -3.62, 0.98), (0.04, 0.82, 0.32), group, respondable=False, detectable=False)
    create_box(sim, "A1_Pilot01_ChargeCable", (0.58, 0.055, 0.045), (-7.44, -3.62, 0.16), (0.02, 0.04, 0.05), group, respondable=False, detectable=False, orientation=(0.0, 0.0, math.radians(4.0)))
    create_text(sim, "A1_Label_Dock", "DOCK + CARGA", (-8.18, -4.30, 0.08), group, height=0.14, color=(0.02, 0.10, 0.16))
    create_text(sim, "A1_Label_Pilot01_Scenario", "PILOTO 1 AMR: ruta planificada, no guia fisica", (-5.05, -5.18, 0.08), group, height=0.15, color=(0.03, 0.12, 0.18))
    create_text(sim, "A1_Label_Pilot01_Mission", "kit -> RFID/QR -> HTP -> FOD -> retorno", (-4.82, -5.48, 0.08), group, height=0.12, color=(0.03, 0.12, 0.18))

    create_box(sim, "A1_Mission_Board", (2.85, 0.08, 1.42), (-8.72, 1.12, 0.86), (0.06, 0.09, 0.12), group, respondable=False, detectable=False)
    create_text(sim, "A1_Mission_Board_Title", "MISION PILOTO 01", (-8.70, 0.26, 1.52), group, height=0.13, color=(0.96, 0.96, 0.86), orientation=(math.radians(90), 0.0, math.radians(-90)))
    for idx, (num, title, detail) in enumerate(PILOT_MISSION_STEPS):
        y = 0.55 + idx * 0.24
        create_box(sim, f"A1_Mission_Board_Row_{num}", (2.48, 0.025, 0.16), (-8.67, y, 1.30), (0.03, 0.36, 0.52) if idx < 3 else (0.60, 0.36, 0.08), group, respondable=False, detectable=False)
        create_text(sim, f"A1_Mission_Board_Text_{num}", f"{num}. {title}", (-8.65, y - 0.08, 1.40), group, height=0.075, color=(1.0, 1.0, 0.94), orientation=(math.radians(90), 0.0, math.radians(-90)))

    status_specs = [
        ("A1_Status_Kit_Loaded", "KIT CARGADO", (-6.85, -1.42, 0.13), (0.04, 0.62, 0.34)),
        ("A1_Status_RFID_OK", "RFID OK", (-3.70, -1.28, 0.13), (0.04, 0.62, 0.34)),
        ("A1_Status_Human_Avoidance", "STOP + ESQUIVA", (-1.58, 0.34, 0.13), (0.74, 0.22, 0.08)),
        ("A1_Status_Delivery", "ENTREGA", (5.35, -1.70, 0.13), (0.03, 0.36, 0.52)),
        ("A1_Status_FOD_Check", "FOD CHECK", (6.45, -0.45, 0.13), (0.74, 0.32, 0.08)),
    ]
    for alias, label, position, color in status_specs:
        create_box(sim, f"{alias}_Plate", (0.92, 0.28, 0.035), position, color, group, respondable=False, detectable=False)
        create_text(sim, alias, label, (position[0] - 0.38, position[1] - 0.04, position[2] + 0.04), group, height=0.085, color=(1.0, 1.0, 0.94))

    create_animated_amr_demo(sim, group)


def add_coppeliasim_models(sim, group: int) -> list[int]:
    create_text(
        sim,
        "A1_Label_CoppeliaSim_Models",
        "robot activo CoppeliaSim: KUKA YouBot (piloto AMR)",
        (0.10, 2.42, 0.08),
        group,
        height=0.15,
        color=(0.05, 0.10, 0.16),
    )
    return []


def add_safety_and_normative_markers(sim, group: int) -> None:
    create_box(sim, "A1_Safety_SlowZone_03ms", (2.4, 1.4, 0.02), (5.65, -1.05, 0.035), (0.92, 0.84, 0.18), group, respondable=False, detectable=False)
    create_text(sim, "A1_Label_SlowZone", "0.3 m/s zona con personal", (6.05, -1.72, 0.09), group, height=0.13, color=(0.44, 0.28, 0.02))
    create_box(sim, "A1_EStop_Post", (0.12, 0.12, 0.85), (0.30, -2.35, 0.425), (0.18, 0.18, 0.18), group)
    create_cylinder(sim, "A1_EStop_Button", (0.22, 0.22, 0.08), (0.30, -2.35, 0.90), (0.84, 0.04, 0.03), group, respondable=False, detectable=False)
    create_text(sim, "A1_Label_EStop", "E-STOP / ISO 3691-4", (0.95, -2.45, 0.08), group, height=0.13, color=(0.55, 0.02, 0.02))

    create_box(sim, "A1_Dynamic_Obstacle_Pallet", (0.75, 0.55, 0.42), (0.78, 0.28, 0.23), (0.66, 0.44, 0.18), group)
    create_box(sim, "A1_Dynamic_Obstacle_Pallet_Ghost", (0.75, 0.55, 0.035), (0.78, 1.02, 0.07), (0.88, 0.72, 0.38), group, respondable=False, detectable=False)
    create_route_segment(sim, "A1_Dynamic_Obstacle_Motion_Arrow", (0.78, 1.02), (0.78, 0.28), group, width=0.09, color=(0.70, 0.23, 0.10), z=0.095)
    create_cylinder(sim, "A1_Replan_Detection_Zone", (1.65, 1.65, 0.010), (0.78, 0.28, 0.080), (0.92, 0.46, 0.16), group, respondable=False, detectable=False)
    create_text(sim, "A1_Label_DynamicObstacle", "obstaculo movil detectado", (0.90, 0.88, 0.10), group, height=0.12, color=(0.44, 0.26, 0.05))
    create_text(sim, "A1_Label_Replanning", "replanificacion local", (1.20, 0.08, 0.10), group, height=0.12, color=(0.44, 0.26, 0.05))
    create_box(sim, "A1_Sim_Limits_Board", (2.55, 0.08, 0.70), (-8.80, 3.70, 0.44), (0.05, 0.08, 0.10), group, respondable=False, detectable=False)
    create_text(sim, "A1_Sim_Limits_Title", "VALIDA RUTA Y CINEMATICA", (-8.78, 3.05, 0.73), group, height=0.095, color=(0.96, 0.96, 0.86), orientation=(math.radians(90), 0.0, math.radians(-90)))
    create_text(sim, "A1_Sim_Limits_Text", "no valida carga industrial", (-8.78, 3.05, 0.53), group, height=0.075, color=(0.90, 0.92, 0.86), orientation=(math.radians(90), 0.0, math.radians(-90)))


def add_documentation_script(sim, group: int) -> None:
    documentation = """-- VIU SRM Actividad 1 - AMR-FOD-Kitting HTP A320
-- Scene purpose:
-- 1. Industrial HTP A320 / section 19.1 work area for Alestis Puerto Real case.
-- 2. Logistics/kitting area with RFID/QR gate, HMI supervision and racks.
-- 3. Single-robot pilot scenario: one AMR executes the complete logistics mission.
-- 4. The animated robot uses the KUKA YouBot model available in CoppeliaSim.
-- 5. A1_AMR_Pilot_01 represents the industrial RB-KAIROS-class AMR concept that would be purchased.
-- 6. The pilot AMR follows: dock -> kitting -> RFID/QR -> HTP -> FOD -> return.
-- 7. Human operator models are animated: kitting loads a tool, the AMR carries it, QA collects it, and a crossing operator triggers stop/avoidance.
-- 8. FOD marker, safety zones, speed restriction and emergency stop are included for screenshots.
"""
    doc = sim.createScript(sim.scripttype_passive, documentation, 0, "lua")
    sim.setObjectAlias(doc, "A1_Scene_Documentation")
    sim.setObjectParent(doc, group, True)


def add_cameras(sim, group: int) -> list[int]:
    base = safe_get(sim, "/DefaultCamera")
    if base < 0:
        return []
    specs = [
        ("A1_Camera_Overview_Submit", (9.2, -9.6, 6.2), (58.0, 0.0, 43.0)),
        ("A1_Camera_HTP_Station_19_1", (8.0, -4.0, 3.0), (62.0, 0.0, 58.0)),
        ("A1_Camera_Logistics_RFID_AMR", (-5.4, -6.3, 3.7), (61.0, 0.0, -26.0)),
        ("A1_Camera_Top_Dimensioning", (0.0, 0.0, 10.5), (0.0, 0.0, 0.0)),
    ]
    cameras: list[int] = []
    for alias, position, orientation_deg in specs:
        try:
            copied = sim.copyPasteObjects([base], 0)
            camera = int(copied[0]) if copied else -1
        except Exception:
            camera = create_dummy(sim, alias, position, group, size=0.06)
        if camera >= 0:
            sim.setObjectAlias(camera, alias)
            sim.setObjectPosition(camera, list(position))
            sim.setObjectOrientation(camera, [math.radians(v) for v in orientation_deg])
            try:
                sim.setObjectParent(camera, group, True)
            except Exception:
                pass
            cameras.append(camera)

    if base >= 0:
        sim.setObjectPosition(base, [9.2, -9.6, 6.2])
        sim.setObjectOrientation(base, [math.radians(58.0), 0.0, math.radians(43.0)])
    return cameras


def add_scene() -> tuple[object, int, list[int]]:
    sim, sim_loop, sim_deinitialize = load_coppeliasim()
    try:
        group = sim.createDummy(0.05, None)
        sim.setObjectAlias(group, "A1_AMR_FOD_Kitting_HTP_Alestis")

        add_warehouse_shell(sim, group)
        add_logistics_area(sim, group)
        add_htp_workstation(sim, group)
        operators = add_human_operators(sim, group)
        add_amr_fleet_and_routes(sim, group)
        add_safety_and_normative_markers(sim, group)
        loaded_models = add_coppeliasim_models(sim, group)
        add_documentation_script(sim, group)
        cameras = add_cameras(sim, group)

        sim.saveScene(str(OUTPUT_SCENE))
        validation = validate_scene(sim, loaded_models, operators, cameras, sim_loop)
        VALIDATION_JSON.write_text(json.dumps(validation, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(validation, indent=2, ensure_ascii=False))
        return sim, group, cameras
    finally:
        sim_deinitialize()


def route_points_inside_floor() -> dict[str, bool]:
    half_x = FLOOR_SIZE[0] / 2.0 - FLOOR_MARGIN
    half_y = FLOOR_SIZE[1] / 2.0 - FLOOR_MARGIN
    return {
        label: (-half_x <= x <= half_x and -half_y <= y <= half_y)
        for x, y, label in MISSION_ROUTE_POINTS
    }


def yaw_close(actual: float, expected: float, tolerance_deg: float = 12.0) -> bool:
    delta = math.atan2(math.sin(actual - expected), math.cos(actual - expected))
    return abs(delta) <= math.radians(tolerance_deg)


def validate_robot_orientation(sim) -> dict[str, bool]:
    checks: dict[str, bool] = {}
    expected = {
        "/A1_AMR_Pilot_01_RB_KAIROS_Class_Frame": math.atan2(
            MISSION_ROUTE_POINTS[1][1] - MISSION_ROUTE_POINTS[0][1],
            MISSION_ROUTE_POINTS[1][0] - MISSION_ROUTE_POINTS[0][0],
        ),
    }
    for path, yaw in expected.items():
        handle = safe_get(sim, path)
        if handle < 0:
            checks[path] = False
            continue
        try:
            orientation = sim.getObjectOrientation(handle)
            checks[path] = yaw_close(float(orientation[2]), yaw)
        except Exception:
            checks[path] = False
    return checks


def validate_youbot_upright(sim, path: str = "/A1_AMR_Pilot_01_KUKA_YouBot_Model") -> dict[str, object]:
    root = safe_get(sim, path)
    if root < 0:
        return {"present": False, "upright": False}
    try:
        handles = sim.getObjectsInTree(root, sim.handle_all, 0)
    except Exception:
        handles = [root]

    wheel_z: list[float] = []
    arm_z: list[float] = []
    for handle in handles:
        try:
            alias = sim.getObjectAlias(int(handle), 1).rsplit("/", 1)[-1]
            z = float(sim.getObjectPosition(int(handle), sim.handle_world)[2])
        except Exception:
            continue
        if alias.startswith("rollingJoint_"):
            wheel_z.append(z)
        elif alias in {"youBotArmJoint0", "youBotArmJoint1"}:
            arm_z.append(z)

    if len(wheel_z) < 4:
        return {"present": True, "upright": False, "reason": "wheel joints not found"}

    wheel_spread = max(wheel_z) - min(wheel_z)
    wheel_mean = sum(wheel_z) / len(wheel_z)
    arm_above = bool(arm_z) and max(arm_z) > wheel_mean + 0.07
    return {
        "present": True,
        "upright": wheel_spread < 0.03 and arm_above,
        "wheel_z_spread_m": round(wheel_spread, 4),
        "wheel_z_mean_m": round(wheel_mean, 4),
        "arm_max_z_m": round(max(arm_z), 4) if arm_z else None,
    }


def validate_youbot_forward_alignment(sim, path: str = "/A1_AMR_Pilot_01_KUKA_YouBot_Model") -> dict[str, object]:
    root = safe_get(sim, path)
    if root < 0:
        return {"present": False, "aligned": False}
    try:
        root_pos = sim.getObjectPosition(root, sim.handle_world)
        handles = sim.getObjectsInTree(root, sim.handle_all, 0)
    except Exception:
        return {"present": True, "aligned": False, "reason": "tree not readable"}

    arm_pos = None
    for handle in handles:
        try:
            if sim.getObjectAlias(int(handle), 1).rsplit("/", 1)[-1] == "youBotArmJoint0":
                arm_pos = sim.getObjectPosition(int(handle), sim.handle_world)
                break
        except Exception:
            continue
    if arm_pos is None:
        return {"present": True, "aligned": False, "reason": "front reference not found"}

    fx = float(arm_pos[0]) - float(root_pos[0])
    fy = float(arm_pos[1]) - float(root_pos[1])
    f_len = math.hypot(fx, fy)
    rx = MISSION_ROUTE_POINTS[1][0] - MISSION_ROUTE_POINTS[0][0]
    ry = MISSION_ROUTE_POINTS[1][1] - MISSION_ROUTE_POINTS[0][1]
    r_len = math.hypot(rx, ry)
    if f_len <= 1e-6 or r_len <= 1e-6:
        return {"present": True, "aligned": False, "reason": "zero vector"}
    dot = (fx * rx + fy * ry) / (f_len * r_len)
    angle_error = math.degrees(math.acos(max(-1.0, min(1.0, dot))))
    return {
        "present": True,
        "aligned": angle_error <= 20.0,
        "angle_error_deg": round(angle_error, 2),
    }


def validate_human_avoidance_clearance() -> dict[str, object]:
    hx, hy = HUMAN_AVOIDANCE_POINT

    def point_to_segment_distance(
        point: tuple[float, float],
        start: tuple[float, float],
        end: tuple[float, float],
    ) -> float:
        px, py = point
        sx, sy = start
        ex, ey = end
        dx = ex - sx
        dy = ey - sy
        denom = dx * dx + dy * dy
        if denom <= 1e-9:
            return math.hypot(px - sx, py - sy)
        t = max(0.0, min(1.0, ((px - sx) * dx + (py - sy) * dy) / denom))
        cx = sx + t * dx
        cy = sy + t * dy
        return math.hypot(px - cx, py - cy)

    segments = list(zip(MISSION_ROUTE_POINTS, MISSION_ROUTE_POINTS[1:]))
    distances = [
        point_to_segment_distance((hx, hy), (a[0], a[1]), (b[0], b[1]))
        for a, b in segments
    ]
    min_distance = min(distances) if distances else 0.0
    return {
        "human_point": [hx, hy],
        "safety_radius_m": HUMAN_SAFETY_RADIUS_M,
        "min_route_clearance_m": round(min_distance, 3),
        "route_avoids_human": min_distance >= HUMAN_SAFETY_RADIUS_M,
    }


def run_stability_preview(sim, sim_loop, handles: list[int]) -> dict[str, object]:
    watched = [h for h in handles if h is not None and int(h) >= 0]
    if not watched:
        return {"ran": False, "reason": "no handles to watch"}
    try:
        sim.startSimulation()
        for _ in range(180):
            sim_loop(None, 0)
        positions = []
        for handle in watched:
            try:
                positions.append(sim.getObjectPosition(int(handle)))
            except Exception:
                pass
        state = sim.getSimulationState()
        while state != sim.simulation_stopped:
            sim.stopSimulation()
            sim_loop(None, 0)
            state = sim.getSimulationState()
        if not positions:
            return {"ran": False, "reason": "no positions read"}
        half_x = FLOOR_SIZE[0] / 2.0 - FLOOR_MARGIN
        half_y = FLOOR_SIZE[1] / 2.0 - FLOOR_MARGIN
        min_z = min(float(p[2]) for p in positions)
        in_bounds = all(-half_x <= float(p[0]) <= half_x and -half_y <= float(p[1]) <= half_y for p in positions)
        return {
            "ran": True,
            "watched_handles": len(watched),
            "min_z_after_180_steps_m": round(min_z, 4),
            "all_above_floor": min_z >= -0.02,
            "all_within_floor_bounds": in_bounds,
        }
    except Exception as exc:
        try:
            while sim.getSimulationState() != sim.simulation_stopped:
                sim.stopSimulation()
                sim_loop(None, 0)
        except Exception:
            pass
        return {"ran": False, "reason": str(exc)}


def validate_scene(sim, loaded_models: list[int], operators: list[int], cameras: list[int], sim_loop) -> dict:
    required_paths = [
        "/A1_AMR_FOD_Kitting_HTP_Alestis",
        "/A1_Floor_Alestis_HTP_Cell",
        "/A1_A320_Section_19_1_Fuselage_Proxy",
        "/A1_A320_TailCone_Construction_Section",
        "/A1_HTP_Center_Box",
        "/A1_HTP_Internal_Rib_01",
        "/A1_RFID_Gate_Left_Post",
        "/A1_Pilot01_ChargingPad",
        "/A1_Pilot01_ChargingTotem",
        "/A1_Mission_Board",
        "/A1_Status_RFID_OK",
        "/A1_AMR_Pilot_01_KUKA_YouBot_Model",
        "/A1_AMR_Pilot_01_RB_KAIROS_Class_Body",
        "/A1_AMR_Pilot_01_RB_KAIROS_Class_Frame",
        "/A1_AMR_Pilot_01_Mission_Script",
        "/A1_Waypoint_02_Kitting",
        "/A1_FOD_Object_Red_Bit",
        "/A1_EStop_Post",
        "/A1_Dynamic_Obstacle_Pallet_Ghost",
        "/A1_Operator_Human_Crossing",
        "/A1_Human_Safety_Stop_Zone",
        "/A1_Status_Human_Avoidance",
        "/A1_Sim_Limits_Board",
        "/A1_Operator_Logistics_Walking",
        "/A1_Operator_QA_Tablet",
        "/A1_Operator_Kitting_Rack",
        "/A1_Operator_FOD_Check",
        "/A1_Operator_HMI_Supervisor",
        "/A1_Human_Task_Animation_Script",
        "/A1_Tool_Handoff_TorqueWrench_Frame",
        "/A1_Tool_Handoff_LoadZone",
        "/A1_Tool_Handoff_PickupZone",
        "/A1_Human_Path_Kitting_Handoff_1_Dash_01",
        "/A1_Human_Path_QA_Delivery_1_Dash_01",
        "/A1_Human_Path_Crossing_1_Dash_01",
        "/A1_Camera_Overview_Submit",
    ]
    checks = {path: safe_get(sim, path) >= 0 for path in required_paths}
    object_count = len(all_objects(sim))
    route_bounds = route_points_inside_floor()
    orientation_checks = validate_robot_orientation(sim)
    youbot_upright = validate_youbot_upright(sim)
    youbot_forward = validate_youbot_forward_alignment(sim)
    human_clearance = validate_human_avoidance_clearance()
    active_youbot = safe_get(sim, "/A1_AMR_Pilot_01_KUKA_YouBot_Model")
    stability = run_stability_preview(
        sim,
        sim_loop,
        [
            safe_get(sim, "/A1_AMR_Pilot_01_RB_KAIROS_Class_Frame"),
            active_youbot,
            *loaded_models,
            *operators,
        ],
    )
    result = {
        "scene": str(OUTPUT_SCENE),
        "object_count": object_count,
        "loaded_coppeliasim_models": (1 if active_youbot >= 0 else 0) + len(loaded_models),
        "human_operator_models": len(operators),
        "human_task_animation": {
            "script_present": safe_get(sim, "/A1_Human_Task_Animation_Script") >= 0,
            "tool_handoff_present": safe_get(sim, "/A1_Tool_Handoff_TorqueWrench_Frame") >= 0,
            "load_zone_present": safe_get(sim, "/A1_Tool_Handoff_LoadZone") >= 0,
            "pickup_zone_present": safe_get(sim, "/A1_Tool_Handoff_PickupZone") >= 0,
        },
        "screenshot_cameras": len(cameras),
        "checks": checks,
        "route_points_inside_floor": route_bounds,
        "robot_orientation_checks": orientation_checks,
        "youbot_upright_check": youbot_upright,
        "youbot_forward_alignment": youbot_forward,
        "human_avoidance_clearance": human_clearance,
        "stability_preview": stability,
        "passed": (
            all(checks.values())
            and all(route_bounds.values())
            and all(orientation_checks.values())
            and bool(youbot_upright.get("upright", False))
            and bool(youbot_forward.get("aligned", False))
            and bool(human_clearance.get("route_avoids_human", False))
            and bool(stability.get("all_above_floor", False))
            and bool(stability.get("all_within_floor_bounds", False))
            and object_count > 180
            and len(cameras) >= 3
            and len(operators) >= 4
        ),
        "open_hint": "Open the .ttt in CoppeliaSim, press Start to see A1_AMR_Pilot_01 follow the single-robot pilot mission, and select A1_Camera_Overview_Submit for the main screenshot.",
    }
    return result


def main() -> int:
    if not COPPELIA_DIR.exists():
        raise FileNotFoundError(COPPELIA_DIR)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    add_scene()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
