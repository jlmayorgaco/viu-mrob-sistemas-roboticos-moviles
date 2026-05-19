"""Build the final CoppeliaSim scene for VIU SRM Actividad 2.

The script loads the supplied anti-collision Pioneer scene, replaces the
classroom controller with a professional Lua controller, adds a small
robotized cell, HMI/battery elements and saves a new .ttt file.
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
BASE_SCENE = ROOT / "actividad2" / "coppeliasim" / "Actividad2_2_Pioneer.ttt"
OUTPUT_SCENE = ROOT / "actividad2" / "coppeliasim" / "Actividad2_Pioneer_Profesional_10_10.ttt"
CONTROLLER = ROOT / "actividad2" / "coppeliasim" / "pioneer_professional_controller.lua"
SCENARIO_MANAGER = ROOT / "actividad2" / "coppeliasim" / "scenario_event_manager.lua"
MULTI_ROBOT_MANAGER = ROOT / "actividad2" / "coppeliasim" / "multi_robot_astar_manager.lua"
VALIDATION_JSON = ROOT / "actividad2" / "coppeliasim" / "Actividad2_Pioneer_Profesional_10_10_validation.json"


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


def remove_previous_delivery(sim) -> None:
    prefixes = (
        "/VIU_",
        "/GoalStation",
        "/DockingStation",
        "/mannequin",
        "/PioneerP3DX/VIU_",
    )
    script_aliases = (
        "/PioneerP3DX/Script",
        "/PioneerP3DX/Pioneer_Professional_Controller",
        "/VIU_Actividad2_Professional_Cell/VIU_Scenario_Event_Manager",
    )

    candidates: list[tuple[int, str]] = []
    for handle in all_objects(sim):
        try:
            alias = sim.getObjectAlias(handle, 1)
        except Exception:
            continue
        if alias.startswith(prefixes) or "/VIU_" in alias or alias in script_aliases:
            candidates.append((handle, alias))

    for handle, _alias in sorted(candidates, key=lambda item: item[1].count("/"), reverse=True):
        try:
            sim.removeObject(handle)
        except Exception:
            pass


def set_color(sim, handle: int, color: Iterable[float]) -> None:
    rgb = list(color)
    try:
        sim.setShapeColor(handle, None, sim.colorcomponent_ambient_diffuse, rgb)
    except Exception:
        sim.setObjectColor(handle, 0, sim.colorcomponent_ambient_diffuse, rgb)


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
    sim.setObjectInt32Param(handle, sim.shapeintparam_static, 1)
    sim.setObjectInt32Param(handle, sim.shapeintparam_respondable, 1 if respondable else 0)

    special = sim.objectspecialproperty_renderable
    if detectable:
        special += sim.objectspecialproperty_collidable
        special += sim.objectspecialproperty_measurable
        special += sim.objectspecialproperty_detectable_all
    sim.setObjectSpecialProperty(handle, special)
    sim.setObjectParent(handle, parent, True)
    return handle


def create_cylinder(
    sim,
    alias: str,
    size: tuple[float, float, float],
    position: tuple[float, float, float],
    color: tuple[float, float, float],
    parent: int,
) -> int:
    handle = sim.createPrimitiveShape(sim.primitiveshape_cylinder, list(size), 2)
    sim.setObjectAlias(handle, alias)
    sim.setObjectPosition(handle, list(position))
    set_color(sim, handle, color)
    sim.setObjectInt32Param(handle, sim.shapeintparam_static, 1)
    sim.setObjectInt32Param(handle, sim.shapeintparam_respondable, 1)
    sim.setObjectSpecialProperty(
        handle,
        sim.objectspecialproperty_renderable
        + sim.objectspecialproperty_collidable
        + sim.objectspecialproperty_measurable
        + sim.objectspecialproperty_detectable_all,
    )
    sim.setObjectParent(handle, parent, True)
    return handle


def create_robot_marker(
    sim,
    alias: str,
    size: tuple[float, float, float],
    position: tuple[float, float, float],
    color: tuple[float, float, float],
    robot: int,
) -> int:
    handle = sim.createPrimitiveShape(sim.primitiveshape_cuboid, list(size), 2)
    sim.setObjectAlias(handle, alias)
    set_color(sim, handle, color)
    sim.setObjectInt32Param(handle, sim.shapeintparam_static, 1)
    sim.setObjectInt32Param(handle, sim.shapeintparam_respondable, 0)
    sim.setObjectSpecialProperty(handle, sim.objectspecialproperty_renderable)
    sim.setObjectParent(handle, robot, False)
    sim.setObjectPosition(handle, list(position), sim.handle_parent)
    return handle


def create_hmi_dashboard(sim, group: int) -> None:
    create_box(
        sim,
        "VIU_HMI_Panel",
        (1.18, 0.055, 0.72),
        (-1.78, 2.22, 0.90),
        (0.035, 0.045, 0.055),
        group,
        respondable=False,
        detectable=False,
    )
    create_box(
        sim,
        "VIU_HMI_TitleRail",
        (1.12, 0.062, 0.055),
        (-1.78, 2.18, 1.22),
        (0.12, 0.32, 0.46),
        group,
        respondable=False,
        detectable=False,
    )

    start_x = -2.28
    for i in range(10):
        create_box(
            sim,
            f"VIU_HMI_Battery_{i + 1}",
            (0.075, 0.065, 0.085),
            (start_x + i * 0.105, 2.16, 1.10),
            (0.06, 0.07, 0.08),
            group,
            respondable=False,
            detectable=False,
        )

    state_names = ["ROUTE", "AVOIDING", "RECOVERY", "HOLD", "ARRIVED"]
    for i, name in enumerate(state_names):
        create_box(
            sim,
            f"VIU_HMI_State_{name}",
            (0.12, 0.065, 0.08),
            (-2.22 + i * 0.22, 2.16, 0.95),
            (0.06, 0.07, 0.08),
            group,
            respondable=False,
            detectable=False,
        )

    zone_names = ["DEFAULT", "APPROACH_LANE", "NARROW_PASSAGE", "TARGET_ZONE", "DOCKING"]
    for i, name in enumerate(zone_names):
        create_box(
            sim,
            f"VIU_HMI_Zone_{name}",
            (0.12, 0.065, 0.08),
            (-2.22 + i * 0.22, 2.16, 0.79),
            (0.06, 0.07, 0.08),
            group,
            respondable=False,
            detectable=False,
        )

    create_box(sim, "VIU_HMI_SensorFault", (0.16, 0.065, 0.09), (-2.13, 2.16, 0.63), (0.06, 0.07, 0.08), group, respondable=False, detectable=False)
    create_box(sim, "VIU_HMI_BatteryLow", (0.16, 0.065, 0.09), (-1.78, 2.16, 0.63), (0.06, 0.07, 0.08), group, respondable=False, detectable=False)
    create_box(sim, "VIU_HMI_Charging", (0.16, 0.065, 0.09), (-1.43, 2.16, 0.63), (0.06, 0.07, 0.08), group, respondable=False, detectable=False)


def create_virtual_sensor(
    sim,
    alias: str,
    position: tuple[float, float, float],
    robot: int,
    *,
    range_m: float = 1.35,
    orientation_source: str | None = None,
    yaw: float = 0.0,
    cone: bool = False,
) -> int:
    sensor_type = sim.proximitysensor_cone if cone else sim.proximitysensor_ray
    int_params = [6, 6, 3, 3, 3, 2, 0, 0] if cone else [3, 3, 2, 2, 1, 1, 0, 0]
    float_params = [
        0.035,
        range_m,
        0.035,
        0.035,
        0.28,
        0.28,
        0.0,
        0.02,
        0.06,
        math.radians(18 if cone else 0),
        0.0,
        0.0,
        0.012,
        0.0,
        0.0,
    ]
    handle = sim.createProximitySensor(sensor_type, 16, 0, int_params, float_params)
    sim.setObjectAlias(handle, alias)
    sim.setObjectParent(handle, robot, False)
    sim.setObjectPosition(handle, list(position), sim.handle_parent)
    if orientation_source:
        source = safe_get(sim, orientation_source)
        if source >= 0:
            sim.setObjectOrientation(handle, sim.getObjectOrientation(source, robot), sim.handle_parent)
        else:
            sim.setObjectOrientation(handle, [0.0, math.radians(90.0), yaw], sim.handle_parent)
    else:
        sim.setObjectOrientation(handle, [0.0, math.radians(90.0), yaw], sim.handle_parent)
    return handle


def add_robot_sensor_suite(sim) -> list[int]:
    robot = safe_get(sim, "/PioneerP3DX")
    if robot < 0:
        return []

    create_robot_marker(sim, "VIU_SensorMast", (0.12, 0.08, 0.10), (0.04, 0.0, 0.205), (0.03, 0.18, 0.26), robot)
    create_robot_marker(sim, "VIU_SafetyControllerBox", (0.18, 0.13, 0.055), (-0.05, 0.0, 0.182), (0.08, 0.08, 0.09), robot)

    sensors = [
        create_virtual_sensor(sim, "VIU_Virtual_Lidar_Front", (0.24, 0.0, 0.19), robot, range_m=1.25, yaw=0.0, cone=True),
        create_virtual_sensor(
            sim,
            "VIU_Virtual_Lidar_FrontLeft",
            (0.20, 0.08, 0.18),
            robot,
            range_m=1.25,
            orientation_source="/PioneerP3DX/ultrasonicSensor[2]",
        ),
        create_virtual_sensor(
            sim,
            "VIU_Virtual_Lidar_FrontRight",
            (0.20, -0.08, 0.18),
            robot,
            range_m=1.25,
            orientation_source="/PioneerP3DX/ultrasonicSensor[5]",
        ),
        create_virtual_sensor(
            sim,
            "VIU_Virtual_Safety_Left",
            (0.03, 0.17, 0.17),
            robot,
            range_m=1.05,
            orientation_source="/PioneerP3DX/ultrasonicSensor[0]",
        ),
        create_virtual_sensor(
            sim,
            "VIU_Virtual_Safety_Right",
            (0.03, -0.17, 0.17),
            robot,
            range_m=1.05,
            orientation_source="/PioneerP3DX/ultrasonicSensor[7]",
        ),
        create_virtual_sensor(sim, "VIU_Virtual_LongRange_Center", (0.22, 0.0, 0.24), robot, range_m=1.75, yaw=0.0),
    ]
    return sensors


def create_dummy(sim, alias: str, position: tuple[float, float, float], parent: int, size: float = 0.07) -> int:
    handle = sim.createDummy(size, None)
    sim.setObjectAlias(handle, alias)
    sim.setObjectPosition(handle, list(position))
    sim.setObjectParent(handle, parent, True)
    return handle


def fleet_cell_to_world(cell: tuple[int, int], z: float = 0.08) -> tuple[float, float, float]:
    origin_x = -2.18
    origin_y = -2.20
    step = 0.38
    return (origin_x + (cell[0] - 1) * step, origin_y + (cell[1] - 1) * step, z)


def create_line_segment(
    sim,
    alias: str,
    start: tuple[float, float],
    end: tuple[float, float],
    width: float,
    z: float,
    color: tuple[float, float, float],
    parent: int,
) -> int:
    sx, sy = start
    ex, ey = end
    dx = ex - sx
    dy = ey - sy
    length = math.hypot(dx, dy)
    angle = math.atan2(dy, dx)
    return create_box(
        sim,
        alias,
        (length, width, 0.010),
        ((sx + ex) / 2.0, (sy + ey) / 2.0, z),
        color,
        parent,
        respondable=False,
        detectable=False,
        orientation=(0.0, 0.0, angle),
    )


def add_visual_polish(sim, group: int) -> int:
    visual_group = sim.createDummy(0.025, None)
    sim.setObjectAlias(visual_group, "VIU_Visual_Polish_Industrial_Textures")
    sim.setObjectParent(visual_group, group, True)

    # Industrial floor base plus raised micro-strips. This gives texture without
    # depending on external bitmap files that could be missing on submission.
    create_box(
        sim,
        "VIU_IndustrialFloor_Base",
        (5.55, 5.45, 0.010),
        (0.0, -0.10, -0.006),
        (0.63, 0.66, 0.68),
        visual_group,
        respondable=False,
        detectable=False,
    )

    for i, x in enumerate([round(-2.40 + 0.48 * k, 2) for k in range(11)], start=1):
        create_box(
            sim,
            f"VIU_FloorTile_X_{i:02d}",
            (0.012, 5.18, 0.006),
            (x, -0.10, 0.004),
            (0.48, 0.50, 0.52),
            visual_group,
            respondable=False,
            detectable=False,
        )
    for i, y in enumerate([round(-2.48 + 0.48 * k, 2) for k in range(11)], start=1):
        create_box(
            sim,
            f"VIU_FloorTile_Y_{i:02d}",
            (5.18, 0.012, 0.006),
            (0.0, y, 0.005),
            (0.48, 0.50, 0.52),
            visual_group,
            respondable=False,
            detectable=False,
        )

    accent_tiles = [
        ("VIU_FloorAccent_Docking", (-1.55, -1.96), (0.92, 0.72), (0.55, 0.65, 0.67)),
        ("VIU_FloorAccent_Target", (1.45, 1.20), (1.02, 1.02), (0.69, 0.66, 0.50)),
        ("VIU_FloorAccent_Workzone", (1.22, -0.58), (0.92, 0.78), (0.67, 0.55, 0.55)),
        ("VIU_FloorAccent_Fleet", (-0.47, -0.49), (3.96, 3.96), (0.58, 0.62, 0.64)),
    ]
    for alias, pos, size, color in accent_tiles:
        create_box(
            sim,
            alias,
            (size[0], size[1], 0.008),
            (pos[0], pos[1], 0.010),
            color,
            visual_group,
            respondable=False,
            detectable=False,
        )

    border_specs = [
        ("North", (-2.42, 2.34), (2.42, 2.34)),
        ("South", (-2.42, -2.52), (2.42, -2.52)),
        ("West", (-2.42, -2.52), (-2.42, 2.34)),
        ("East", (2.42, -2.52), (2.42, 2.34)),
    ]
    for name, start, end in border_specs:
        create_line_segment(sim, f"VIU_SafetyBorder_{name}", start, end, 0.045, 0.022, (0.96, 0.74, 0.08), visual_group)

    for i, x in enumerate([-2.10, -1.70, -1.30, -0.90, -0.50, -0.10, 0.30, 0.70, 1.10, 1.50, 1.90], start=1):
        color = (0.98, 0.76, 0.05) if i % 2 else (0.10, 0.10, 0.10)
        create_box(
            sim,
            f"VIU_HazardStripe_North_{i:02d}",
            (0.24, 0.045, 0.012),
            (x, 2.34, 0.034),
            color,
            visual_group,
            respondable=False,
            detectable=False,
            orientation=(0.0, 0.0, math.radians(18)),
        )
        create_box(
            sim,
            f"VIU_HazardStripe_South_{i:02d}",
            (0.24, 0.045, 0.012),
            (x, -2.52, 0.034),
            color,
            visual_group,
            respondable=False,
            detectable=False,
            orientation=(0.0, 0.0, math.radians(-18)),
        )

    for i, x in enumerate([-1.42, -0.95, -0.48, -0.01, 0.46, 0.93, 1.40], start=1):
        create_box(
            sim,
            f"VIU_LaneDash_Approach_{i:02d}",
            (0.28, 0.028, 0.012),
            (x, -1.55, 0.030),
            (0.94, 0.94, 0.88),
            visual_group,
            respondable=False,
            detectable=False,
        )

    for i, (x, y) in enumerate([(-1.88, -2.28), (-1.22, -2.28), (-1.88, -1.64), (-1.22, -1.64)], start=1):
        create_box(
            sim,
            f"VIU_ChargeBay_Corner_{i}",
            (0.18, 0.050, 0.014),
            (x, y, 0.036),
            (0.98, 0.82, 0.12),
            visual_group,
            respondable=False,
            detectable=False,
        )

    return visual_group


def add_fleet_grid_texture(sim, parent: int) -> None:
    origin_x = -2.18
    origin_y = -2.20
    step = 0.38
    min_x = origin_x - step / 2.0
    max_x = origin_x + 9 * step + step / 2.0
    min_y = origin_y - step / 2.0
    max_y = origin_y + 9 * step + step / 2.0
    center_x = (min_x + max_x) / 2.0
    center_y = (min_y + max_y) / 2.0
    length_x = max_x - min_x
    length_y = max_y - min_y

    for i in range(11):
        x = min_x + i * step
        create_box(
            sim,
            f"VIU_AStar_GridLine_X_{i:02d}",
            (0.010, length_y, 0.008),
            (x, center_y, 0.023),
            (0.34, 0.38, 0.41),
            parent,
            respondable=False,
            detectable=False,
        )
        y = min_y + i * step
        create_box(
            sim,
            f"VIU_AStar_GridLine_Y_{i:02d}",
            (length_x, 0.010, 0.008),
            (center_x, y, 0.024),
            (0.34, 0.38, 0.41),
            parent,
            respondable=False,
            detectable=False,
        )


def add_fleet_route_markers(sim, parent: int) -> None:
    path_specs = {
        "R1": {
            "color": (0.08, 0.32, 0.78),
            "cells": [(2, 2), (2, 5), (4, 5), (4, 9), (8, 9), (10, 10)],
        },
        "R2": {
            "color": (0.74, 0.22, 0.16),
            "cells": [(3, 10), (5, 10), (5, 7), (9, 7), (10, 2)],
        },
        "R3": {
            "color": (0.10, 0.56, 0.28),
            "cells": [(6, 2), (9, 2), (9, 6), (9, 10)],
        },
    }

    for robot_id, spec in path_specs.items():
        cells = spec["cells"]
        color = spec["color"]
        for i in range(len(cells) - 1):
            a = fleet_cell_to_world(cells[i], 0.0)
            b = fleet_cell_to_world(cells[i + 1], 0.0)
            create_line_segment(
                sim,
                f"VIU_Fleet_{robot_id}_Route_{i + 1:02d}",
                (a[0], a[1]),
                (b[0], b[1]),
                0.038,
                0.058 + 0.003 * i,
                color,
                parent,
            )


def add_multi_robot_fleet(sim, group: int) -> None:
    chargers = {
        "R1": (2, 2),
        "R2": (2, 10),
        "R3": (6, 2),
    }
    starts = {
        "R1": (2, 2),
        "R2": (3, 10),
        "R3": (6, 2),
    }
    goals = {
        "R1": (10, 10),
        "R2": (10, 2),
        "R3": (9, 10),
    }
    colors = {
        "R1": (0.10, 0.42, 0.82),
        "R2": (0.74, 0.24, 0.18),
        "R3": (0.12, 0.62, 0.34),
    }

    create_box(
        sim,
        "VIU_AStar_Grid_Backplate",
        (4.70, 4.70, 0.008),
        (0.0, -0.10, 0.004),
        (0.92, 0.94, 0.96),
        group,
        respondable=False,
        detectable=False,
    )
    add_fleet_grid_texture(sim, group)

    blocked_cells = [(6, 5), (6, 6), (7, 5), (7, 6), (8, 6), (5, 8), (6, 8)]
    for i, cell in enumerate(blocked_cells, start=1):
        create_box(
            sim,
            f"VIU_AStar_Blocked_{i}",
            (0.30, 0.30, 0.018),
            fleet_cell_to_world(cell, 0.018),
            (0.16, 0.17, 0.18),
            group,
            respondable=False,
            detectable=False,
        )

    for robot_id, cell in chargers.items():
        create_box(
            sim,
            f"VIU_Fleet_Charge_{robot_id}",
            (0.34, 0.34, 0.030),
            fleet_cell_to_world(cell, 0.040),
            (0.08, 0.44, 0.72),
            group,
            respondable=False,
            detectable=False,
        )
        create_box(
            sim,
            f"VIU_Fleet_ChargeContact_{robot_id}",
            (0.22, 0.055, 0.045),
            fleet_cell_to_world(cell, 0.075),
            (0.92, 0.78, 0.18),
            group,
            respondable=False,
            detectable=False,
        )

    for robot_id, cell in goals.items():
        create_box(
            sim,
            f"VIU_Fleet_Goal_{robot_id}",
            (0.34, 0.34, 0.022),
            fleet_cell_to_world(cell, 0.026),
            (0.86, 0.68, 0.16),
            group,
            respondable=False,
            detectable=False,
        )

    for robot_id, cell in starts.items():
        robot = create_box(
            sim,
            f"VIU_Fleet_Robot_{robot_id[-1]}",
            (0.24, 0.24, 0.15),
            fleet_cell_to_world(cell, 0.150),
            colors[robot_id],
            group,
            respondable=False,
            detectable=False,
        )
        create_robot_marker(
            sim,
            f"VIU_Fleet_Status_{robot_id}",
            (0.14, 0.14, 0.035),
            (0.0, 0.0, 0.105),
            (0.03, 0.70, 0.20),
            robot,
        )
    add_fleet_route_markers(sim, group)


def add_robotized_cell(sim) -> int:
    group = sim.createDummy(0.04, None)
    sim.setObjectAlias(group, "VIU_Actividad2_Professional_Cell")

    add_visual_polish(sim, group)

    create_box(sim, "VIU_SafetyFence_North", (5.3, 0.05, 0.55), (0.0, 2.55, 0.275), (0.05, 0.14, 0.22), group)
    create_box(sim, "VIU_SafetyFence_South", (5.3, 0.05, 0.55), (0.0, -2.75, 0.275), (0.05, 0.14, 0.22), group)
    create_box(sim, "VIU_SafetyFence_West", (0.05, 5.05, 0.55), (-2.65, -0.05, 0.275), (0.05, 0.14, 0.22), group)
    create_box(sim, "VIU_SafetyFence_East", (0.05, 5.05, 0.55), (2.65, -0.05, 0.275), (0.05, 0.14, 0.22), group)

    create_box(sim, "VIU_DockingStation", (0.65, 0.55, 0.05), (-1.55, -1.96, 0.025), (0.11, 0.34, 0.28), group, respondable=False, detectable=False)
    create_box(sim, "VIU_ChargingPad", (0.54, 0.42, 0.025), (-1.55, -1.96, 0.065), (0.08, 0.44, 0.72), group, respondable=False, detectable=False)
    create_box(sim, "VIU_ChargingPedestal", (0.12, 0.10, 0.34), (-1.95, -1.96, 0.20), (0.04, 0.12, 0.16), group, respondable=False, detectable=False)
    create_box(sim, "VIU_ChargingContact_A", (0.045, 0.19, 0.035), (-1.50, -2.03, 0.095), (0.88, 0.80, 0.18), group, respondable=False, detectable=False)
    create_box(sim, "VIU_ChargingContact_B", (0.045, 0.19, 0.035), (-1.60, -1.89, 0.095), (0.88, 0.80, 0.18), group, respondable=False, detectable=False)
    create_box(sim, "VIU_Conveyor_Infeed", (1.10, 0.34, 0.24), (0.78, 1.62, 0.12), (0.12, 0.12, 0.13), group)
    create_box(sim, "VIU_Conveyor_Outfeed", (0.95, 0.32, 0.24), (1.35, 0.42, 0.12), (0.13, 0.13, 0.14), group)
    create_box(sim, "VIU_Pallet_A", (0.36, 0.30, 0.28), (-0.20, -0.74, 0.14), (0.62, 0.42, 0.16), group)
    create_box(sim, "VIU_Pallet_B", (0.34, 0.36, 0.24), (0.78, 0.12, 0.12), (0.58, 0.35, 0.13), group)
    create_cylinder(sim, "VIU_RobotArm_WorkZone", (0.42, 0.42, 0.08), (1.22, -0.58, 0.04), (0.58, 0.08, 0.08), group)

    create_box(sim, "VIU_EventPallet_Moving", (0.32, 0.26, 0.30), (-0.35, -0.34, 0.15), (0.70, 0.48, 0.12), group)
    create_box(sim, "VIU_EventGate_Left", (0.10, 0.42, 0.46), (0.52, -0.28, 0.23), (0.08, 0.24, 0.48), group)
    create_box(sim, "VIU_EventGate_Right", (0.10, 0.42, 0.46), (0.98, -0.28, 0.23), (0.08, 0.24, 0.48), group)

    create_box(sim, "VIU_EventScenarioPanel", (0.72, 0.05, 0.42), (-2.15, 2.20, 0.46), (0.06, 0.08, 0.10), group, respondable=False, detectable=False)
    create_cylinder(sim, "VIU_Traffic_Red", (0.10, 0.10, 0.045), (-2.15, 2.16, 0.61), (0.18, 0.03, 0.03), group)
    create_cylinder(sim, "VIU_Traffic_Yellow", (0.10, 0.10, 0.045), (-2.15, 2.16, 0.49), (0.18, 0.15, 0.03), group)
    create_cylinder(sim, "VIU_Traffic_Green", (0.10, 0.10, 0.045), (-2.15, 2.16, 0.37), (0.02, 0.72, 0.18), group)
    create_hmi_dashboard(sim, group)
    add_multi_robot_fleet(sim, group)

    create_box(sim, "VIU_SafeApproachLane", (3.95, 0.18, 0.012), (0.10, -1.55, 0.006), (0.05, 0.42, 0.35), group, respondable=False, detectable=False)
    create_box(sim, "VIU_TargetStopZone", (0.82, 0.82, 0.014), (1.45, 1.20, 0.007), (0.88, 0.72, 0.16), group, respondable=False, detectable=False)
    create_box(sim, "VIU_DynamicScenarioZone", (1.45, 0.18, 0.010), (0.38, -0.98, 0.010), (0.92, 0.52, 0.09), group, respondable=False, detectable=False)
    create_box(sim, "VIU_NarrowPassageZone", (0.92, 0.16, 0.010), (0.75, -0.46, 0.012), (0.42, 0.46, 0.70), group, respondable=False, detectable=False)

    create_dummy(sim, "DockingStation", (-1.55, -1.96, 0.18), group)
    create_dummy(sim, "GoalStation", (1.45, 1.20, 0.18), group)
    create_dummy(sim, "mannequin", (1.45, 1.20, 0.28), group, size=0.08)
    create_dummy(sim, "VIU_Waypoint_1", (-0.70, -1.55, 0.12), group, size=0.05)
    create_dummy(sim, "VIU_Waypoint_2", (0.55, -1.55, 0.12), group, size=0.05)
    create_dummy(sim, "VIU_Waypoint_3", (1.85, -1.10, 0.12), group, size=0.05)
    create_dummy(sim, "VIU_Waypoint_4", (2.05, 0.95, 0.12), group, size=0.05)

    return group


def attach_controller(sim, group: int) -> int:
    robot = safe_get(sim, "/PioneerP3DX")
    if robot < 0:
        raise RuntimeError("PioneerP3DX was not found in the base scene")

    script_text = CONTROLLER.read_text(encoding="utf-8")
    script_handle = sim.createScript(sim.scripttype_simulation, script_text, 0, "lua")
    sim.setObjectAlias(script_handle, "Pioneer_Professional_Controller")
    sim.setObjectParent(script_handle, robot, False)

    documentation = """-- VIU SRM Actividad 2 - Documentation embedded in scene
-- 1. Integrates Pioneer P3DX in a robotized cell.
-- 2. Follows route waypoints toward Bill/mannequin/GoalStation with
--    potential-field attraction.
-- 3. Avoids obstacles via 16 ultrasonic sensors plus 6 virtual safety sensors.
-- 4. Adds scenario events: moving pallet, safety hold, dynamic target,
--    narrow passage, sensor degradation and low battery.
-- 5. Adds speed zones, battery policy, charging station and visual HMI.
-- 6. Adds a cooperative 3-AMR fleet with A* time reservations and recharge.
-- 7. Publishes missionReady, pioneerArrived, pioneerState,
--    pioneerDistanceToTarget, pioneerMinObstacleDistance, pioneerObstacleRisk,
--    pioneerScenario, battery, speed-zone, route and fleet signals.
-- 8. Includes delivery scene, report and presentation in actividad2/.
"""
    doc = sim.createScript(sim.scripttype_passive, documentation, 0, "lua")
    sim.setObjectAlias(doc, "VIU_Activity2_Delivery_Documentation")
    sim.setObjectParent(doc, group, True)

    scenario_text = SCENARIO_MANAGER.read_text(encoding="utf-8")
    scenario = sim.createScript(sim.scripttype_simulation, scenario_text, 0, "lua")
    sim.setObjectAlias(scenario, "VIU_Scenario_Event_Manager")
    sim.setObjectParent(scenario, group, False)

    fleet_text = MULTI_ROBOT_MANAGER.read_text(encoding="utf-8")
    fleet = sim.createScript(sim.scripttype_simulation, fleet_text, 0, "lua")
    sim.setObjectAlias(fleet, "VIU_MultiRobot_AStar_Manager")
    sim.setObjectParent(fleet, group, False)
    return script_handle


def set_initial_layout(sim) -> None:
    pioneer = safe_get(sim, "/PioneerP3DX")
    bill = safe_get(sim, "/Bill")
    if pioneer >= 0:
        sim.setObjectPosition(pioneer, [-1.55, -1.92, 0.1388])
        sim.setObjectOrientation(pioneer, [0.0, 0.0, math.radians(18.0)])
    if bill >= 0:
        sim.setObjectPosition(bill, [1.45, 1.20, 0.0])
        sim.setObjectOrientation(bill, [0.0, 0.0, math.radians(-145.0)])
    plant = safe_get(sim, "/indoorPlant")
    if plant >= 0:
        sim.setObjectPosition(plant, [-0.32, -0.58, 0.165])

    camera = safe_get(sim, "/DefaultCamera")
    if camera >= 0:
        sim.setObjectPosition(camera, [3.15, -4.35, 3.15])
        sim.setObjectOrientation(camera, [math.radians(58), 0.0, math.radians(38)])


def sim_step(sim, sim_loop) -> None:
    if sim.getSimulationState() == sim.simulation_stopped:
        return
    current = sim.getSimulationTime()
    for _ in range(80):
        sim_loop(None, 0)
        if current != sim.getSimulationTime() or sim.getSimulationState() == sim.simulation_stopped:
            break


def validate_scene(sim, sim_loop) -> dict:
    robot = safe_get(sim, "/PioneerP3DX")
    target = safe_get(sim, "/mannequin")
    if robot < 0 or target < 0:
        raise RuntimeError("Cannot validate without /PioneerP3DX and /mannequin")

    rel = sim.getObjectPosition(target, robot)
    initial_distance = math.hypot(rel[0], rel[1])

    sim.setInt32Signal("missionReady", 1)
    sim.setInt32Signal("pioneerUseWaypoints", 1)
    sim.setInt32Signal("pioneerScenarioEnabled", 1)
    sim.startSimulation()
    states_seen: set[str] = set()
    scenarios_seen: set[str] = set()
    speed_zones_seen: set[str] = set()
    battery_modes_seen: set[str] = set()
    sensor_fault_seen = False
    charging_seen = False
    fleet_complete_seen = False
    for _ in range(2200):
        sim_step(sim, sim_loop)
        if sim.getSimulationTime() > 90:
            break
        state = sim.getStringSignal("pioneerState")
        scenario = sim.getStringSignal("pioneerScenario")
        speed_zone = sim.getStringSignal("pioneerSpeedZone")
        battery_mode = sim.getStringSignal("pioneerBatteryMode")
        sensor_fault = sim.getInt32Signal("pioneerSensorFaultActive")
        charging = sim.getInt32Signal("pioneerCharging")
        fleet_all_complete = sim.getInt32Signal("fleetAllComplete")
        if state:
            states_seen.add(str(state))
        if scenario:
            scenarios_seen.add(str(scenario))
        if speed_zone:
            speed_zones_seen.add(str(speed_zone))
        if battery_mode:
            battery_modes_seen.add(str(battery_mode))
        if sensor_fault is not None and int(sensor_fault) > 0:
            sensor_fault_seen = True
        if charging is not None and int(charging) > 0:
            charging_seen = True
        if fleet_all_complete is not None and int(fleet_all_complete) == 1:
            fleet_complete_seen = True
        if (
            state == "ARRIVED"
            and sim.getSimulationTime() > 42
            and "S8_FINAL_APPROACH" in scenarios_seen
            and fleet_complete_seen
        ):
            break
    final_rel = sim.getObjectPosition(target, robot)
    final_distance = math.hypot(final_rel[0], final_rel[1])
    min_obstacle = sim.getFloatSignal("pioneerMinObstacleDistance")
    obstacle_risk = sim.getFloatSignal("pioneerObstacleRisk")
    sensor_count = sim.getInt32Signal("pioneerSensorCount")
    battery_level = sim.getFloatSignal("pioneerBatteryLevel")
    battery_mode = sim.getStringSignal("pioneerBatteryMode")
    speed_zone = sim.getStringSignal("pioneerSpeedZone")
    speed_limit = sim.getFloatSignal("pioneerSpeedLimitFactor")
    sensor_fault_count = sim.getInt32Signal("pioneerSensorFaultCount")
    fleet_total = sim.getInt32Signal("fleetRobotsTotal")
    fleet_plans_ready = sim.getInt32Signal("fleetAStarPlansReady")
    fleet_plan_count = sim.getInt32Signal("fleetAStarPlanCount")
    fleet_conflicts = sim.getInt32Signal("fleetReservationConflictsAvoided")
    fleet_charging_events = sim.getInt32Signal("fleetChargingEvents")
    fleet_mission_complete = sim.getInt32Signal("fleetMissionComplete")
    fleet_recharged_count = sim.getInt32Signal("fleetRechargedCount")
    fleet_all_complete = sim.getInt32Signal("fleetAllComplete")
    fleet_min_battery = sim.getFloatSignal("fleetMinBattery")
    fleet_state_summary = sim.getStringSignal("fleetStateSummary")
    route_index = sim.getInt32Signal("pioneerRouteIndex")
    state = sim.getStringSignal("pioneerState")
    scenario = sim.getStringSignal("pioneerScenario")
    sim.stopSimulation()
    while sim.getSimulationState() != sim.simulation_stopped:
        sim_loop(None, 0)

    virtual_sensor_names = [
        "/PioneerP3DX/VIU_Virtual_Lidar_Front",
        "/PioneerP3DX/VIU_Virtual_Lidar_FrontLeft",
        "/PioneerP3DX/VIU_Virtual_Lidar_FrontRight",
        "/PioneerP3DX/VIU_Virtual_Safety_Left",
        "/PioneerP3DX/VIU_Virtual_Safety_Right",
        "/PioneerP3DX/VIU_Virtual_LongRange_Center",
    ]
    virtual_sensor_count = sum(1 for name in virtual_sensor_names if safe_get(sim, name) >= 0)

    result = {
        "scene": str(OUTPUT_SCENE),
        "initial_distance_m": round(initial_distance, 3),
        "final_distance_m": round(final_distance, 3),
        "last_state": state,
        "last_scenario": scenario,
        "states_seen": sorted(states_seen),
        "scenarios_seen": sorted(scenarios_seen),
        "speed_zones_seen": sorted(speed_zones_seen),
        "battery_modes_seen": sorted(battery_modes_seen),
        "route_index": int(route_index) if route_index is not None else None,
        "sensor_count": int(sensor_count) if sensor_count is not None else None,
        "virtual_sensor_count": virtual_sensor_count,
        "battery_level": round(float(battery_level), 2) if battery_level is not None else None,
        "battery_mode": battery_mode,
        "speed_zone": speed_zone,
        "speed_limit_factor": round(float(speed_limit), 3) if speed_limit is not None else None,
        "sensor_fault_count": int(sensor_fault_count) if sensor_fault_count is not None else None,
        "fleet": {
            "robots_total": int(fleet_total) if fleet_total is not None else None,
            "astar_plans_ready": int(fleet_plans_ready) if fleet_plans_ready is not None else None,
            "astar_plan_count": int(fleet_plan_count) if fleet_plan_count is not None else None,
            "reservation_conflicts_avoided": int(fleet_conflicts) if fleet_conflicts is not None else None,
            "charging_events": int(fleet_charging_events) if fleet_charging_events is not None else None,
            "mission_complete": int(fleet_mission_complete) if fleet_mission_complete is not None else None,
            "recharged_count": int(fleet_recharged_count) if fleet_recharged_count is not None else None,
            "all_complete": int(fleet_all_complete) if fleet_all_complete is not None else None,
            "min_battery": round(float(fleet_min_battery), 2) if fleet_min_battery is not None else None,
            "state_summary": fleet_state_summary,
        },
        "min_obstacle_distance_m": round(float(min_obstacle), 3) if min_obstacle is not None else None,
        "obstacle_risk": round(float(obstacle_risk), 3) if obstacle_risk is not None else None,
        "checks": {
            "pioneer_present": robot >= 0,
            "mannequin_present": target >= 0,
            "controller_attached": safe_get(sim, "/PioneerP3DX/Pioneer_Professional_Controller") >= 0,
            "scenario_manager_attached": safe_get(sim, "/VIU_Actividad2_Professional_Cell/VIU_Scenario_Event_Manager") >= 0,
            "professional_cell_present": safe_get(sim, "/VIU_Actividad2_Professional_Cell") >= 0,
            "event_objects_present": safe_get(sim, "/VIU_EventPallet_Moving") >= 0
            and safe_get(sim, "/VIU_EventGate_Left") >= 0
            and safe_get(sim, "/VIU_EventGate_Right") >= 0,
            "hmi_present": safe_get(sim, "/VIU_HMI_Panel") >= 0
            and safe_get(sim, "/VIU_HMI_Battery_1") >= 0
            and safe_get(sim, "/VIU_HMI_State_ARRIVED") >= 0,
            "charging_station_present": safe_get(sim, "/VIU_ChargingPad") >= 0
            and safe_get(sim, "/VIU_ChargingPedestal") >= 0,
            "multi_robot_fleet_present": safe_get(sim, "/VIU_Fleet_Robot_1") >= 0
            and safe_get(sim, "/VIU_Fleet_Robot_2") >= 0
            and safe_get(sim, "/VIU_Fleet_Robot_3") >= 0,
            "fleet_chargers_present": safe_get(sim, "/VIU_Fleet_Charge_R1") >= 0
            and safe_get(sim, "/VIU_Fleet_Charge_R2") >= 0
            and safe_get(sim, "/VIU_Fleet_Charge_R3") >= 0,
            "fleet_astar_manager_attached": safe_get(sim, "/VIU_Actividad2_Professional_Cell/VIU_MultiRobot_AStar_Manager") >= 0,
            "visual_floor_texture_present": safe_get(sim, "/VIU_IndustrialFloor_Base") >= 0
            and safe_get(sim, "/VIU_FloorTile_X_01") >= 0
            and safe_get(sim, "/VIU_FloorTile_Y_01") >= 0,
            "visual_signage_present": safe_get(sim, "/VIU_SafetyBorder_North") >= 0
            and safe_get(sim, "/VIU_HazardStripe_North_01") >= 0
            and safe_get(sim, "/VIU_LaneDash_Approach_01") >= 0,
            "fleet_visual_grid_present": safe_get(sim, "/VIU_AStar_GridLine_X_00") >= 0
            and safe_get(sim, "/VIU_Fleet_R1_Route_01") >= 0
            and safe_get(sim, "/VIU_Fleet_R2_Route_01") >= 0
            and safe_get(sim, "/VIU_Fleet_R3_Route_01") >= 0,
            "virtual_sensors_present": virtual_sensor_count >= 6,
            "sensor_suite_active": sensor_count is not None and int(sensor_count) >= 22,
            "battery_telemetry_active": battery_level is not None and 0 <= float(battery_level) <= 100,
            "battery_policy_seen": "LOW" in battery_modes_seen,
            "charging_seen": charging_seen,
            "speed_zones_seen": len(speed_zones_seen) >= 3,
            "sensor_fault_event_seen": sensor_fault_seen,
            "fleet_astar_active": fleet_total is not None
            and int(fleet_total) == 3
            and fleet_plans_ready is not None
            and int(fleet_plans_ready) == 1
            and fleet_plan_count is not None
            and int(fleet_plan_count) >= 3,
            "fleet_cooperation_active": fleet_conflicts is not None and int(fleet_conflicts) >= 1,
            "fleet_battery_cycle_complete": fleet_charging_events is not None
            and int(fleet_charging_events) >= 3
            and fleet_recharged_count is not None
            and int(fleet_recharged_count) == 3,
            "fleet_all_complete": fleet_all_complete is not None and int(fleet_all_complete) == 1,
            "scenario_events_seen": len(scenarios_seen) >= 8,
            "distance_reduced": final_distance < initial_distance,
            "close_to_target": final_distance <= 0.95,
            "arrived_or_tracking": state in ("ARRIVED", "TRACKING", "ROUTE", "AVOIDING", "RECOVERY"),
        },
    }
    result["passed"] = all(result["checks"].values())
    return result


def main() -> int:
    if not BASE_SCENE.exists():
        raise FileNotFoundError(BASE_SCENE)
    if not CONTROLLER.exists():
        raise FileNotFoundError(CONTROLLER)
    if not SCENARIO_MANAGER.exists():
        raise FileNotFoundError(SCENARIO_MANAGER)
    if not MULTI_ROBOT_MANAGER.exists():
        raise FileNotFoundError(MULTI_ROBOT_MANAGER)

    sim, sim_loop, sim_deinitialize = load_coppeliasim()
    try:
        if sim.loadScene(str(BASE_SCENE)) < 0:
            raise RuntimeError(f"Could not load {BASE_SCENE}")
        for _ in range(3):
            sim_loop(None, 0)

        remove_previous_delivery(sim)
        set_initial_layout(sim)
        group = add_robotized_cell(sim)
        add_robot_sensor_suite(sim)
        attach_controller(sim, group)

        sim.saveScene(str(OUTPUT_SCENE))
        validation = validate_scene(sim, sim_loop)
        VALIDATION_JSON.write_text(json.dumps(validation, indent=2), encoding="utf-8")

        if not validation["passed"]:
            print(json.dumps(validation, indent=2))
            return 2
        print(json.dumps(validation, indent=2))
        return 0
    finally:
        sim_deinitialize()


if __name__ == "__main__":
    raise SystemExit(main())
