"""Build and validate Actividad2_1_Basic_Follower.ttt.

The scene is a focused Bill-follower version of Activity 2.1:
- Pioneer P3DX follows Bill inside a named room.
- The Pioneer controller can run as P, PI, PID, LQR or NMPC.
- Bill walks a deterministic circular path with acceleration/deceleration and then stops.
- Each controller mode is simulated and exported to CSV for Python plots.
"""

from __future__ import annotations

import csv
import json
import math
import os
import statistics
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
COPPELIA_DIR = Path(r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu")
SCENE = ROOT / "actividad2" / "coppeliasim" / "Actividad2_1_Basic_Follower.ttt"
CONTROLLER = ROOT / "actividad2" / "coppeliasim" / "pioneer_pid_follower_controller.lua"
BILL_MANAGER = ROOT / "actividad2" / "coppeliasim" / "bill_walking_room_manager.lua"
CSV_LOGGER = ROOT / "actividad2" / "coppeliasim" / "follower_csv_logger.lua"
LOG_DIR = ROOT / "actividad2" / "coppeliasim" / "follower_pid_logs"
VALIDATION_JSON = ROOT / "actividad2" / "coppeliasim" / "Actividad2_1_Basic_Follower_validation.json"

BILL_SPEED_MPS = 0.22
BILL_SPEED_AMPLITUDE_MPS = 0.09
BILL_CIRCLE_RADIUS_M = 1.55
BILL_CIRCLE_LAPS = 2
BILL_CIRCLE_SAMPLES = 72
BILL_START_ANGLE_RAD = math.pi / 4.0
VALIDATION_SETTLE_MARGIN_S = 45.0
CONTROL_MODES = ("P", "PI", "PID", "LQR", "NMPC")


def generate_bill_path() -> list[dict[str, object]]:
    nodes: list[dict[str, object]] = []

    for i in range(BILL_CIRCLE_SAMPLES + 1):
        angle = BILL_START_ANGLE_RAD + 2.0 * math.pi * i / BILL_CIRCLE_SAMPLES
        nodes.append(
            {
                "xy": (BILL_CIRCLE_RADIUS_M * math.cos(angle), BILL_CIRCLE_RADIUS_M * math.sin(angle)),
                "pause": 0.0,
                "phase": "circle",
            }
        )

    return nodes


BILL_PATH = generate_bill_path()
WAYPOINTS = [node["xy"] for node in BILL_PATH]


def bill_path_length() -> float:
    return sum(
        math.hypot(WAYPOINTS[i + 1][0] - WAYPOINTS[i][0], WAYPOINTS[i + 1][1] - WAYPOINTS[i][1])
        for i in range(len(WAYPOINTS) - 1)
    )


def bill_path_duration() -> float:
    return (2.0 * math.pi * BILL_CIRCLE_RADIUS_M * BILL_CIRCLE_LAPS) / BILL_SPEED_MPS


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
    index = 0
    while True:
        handle = sim.getObjects(index, sim.handle_all)
        if handle == -1:
            break
        handles.append(handle)
        index += 1
    return handles


def set_color(sim, handle: int, color: Iterable[float]) -> None:
    rgb = list(color)
    try:
        sim.setShapeColor(handle, None, sim.colorcomponent_ambient_diffuse, rgb)
    except Exception:
        sim.setObjectColor(handle, 0, sim.colorcomponent_ambient_diffuse, rgb)


def remove_previous_follower(sim) -> None:
    prefixes = (
        "/A2F_",
        "/A2_Basic_",
        "/GoalStation",
        "/mannequin",
    )
    script_aliases = {
        "/PioneerP3DX/Script",
        "/PioneerP3DX/Pioneer_Basic_Controller",
        "/PioneerP3DX/Pioneer_Professional_Controller",
        "/PioneerP3DX/Pioneer_PID_Follower_Controller",
        "/Bill/Script",
        "/A2F_Follower_Room/A2F_Bill_Walking_Room_Manager",
        "/A2F_Follower_Room/A2F_Follower_CSV_Logger",
        "/A2F_Follower_Room/A2F_Follower_Experiment_Documentation",
    }

    candidates: list[tuple[int, str]] = []
    for handle in all_objects(sim):
        try:
            alias = sim.getObjectAlias(handle, 1)
        except Exception:
            continue
        if alias.startswith(prefixes) or alias in script_aliases:
            candidates.append((handle, alias))

    for handle, _alias in sorted(candidates, key=lambda item: item[1].count("/"), reverse=True):
        try:
            sim.removeObject(handle)
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
    yaw: float = 0.0,
    respondable: bool = True,
    detectable: bool = True,
) -> int:
    handle = sim.createPrimitiveShape(sim.primitiveshape_cuboid, list(size), 2)
    sim.setObjectAlias(handle, alias)
    sim.setObjectPosition(handle, list(position))
    sim.setObjectOrientation(handle, [0.0, 0.0, yaw])
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


def create_dummy(sim, alias: str, position: tuple[float, float, float], parent: int, size: float = 0.05) -> int:
    handle = sim.createDummy(size, None)
    sim.setObjectAlias(handle, alias)
    sim.setObjectPosition(handle, list(position))
    sim.setObjectParent(handle, parent, True)
    return handle


def make_bill_visual_target_only(sim) -> None:
    """Keep Bill visible/detectable but remove physical impacts with Pioneer."""
    for handle in all_objects(sim):
        try:
            alias = sim.getObjectAlias(handle, 1)
            object_type = sim.getObjectType(handle)
        except Exception:
            continue
        if alias != "/Bill" and not alias.startswith("/Bill/"):
            continue
        if object_type != sim.object_shape_type:
            continue
        try:
            sim.setObjectInt32Param(handle, sim.shapeintparam_respondable, 0)
            sim.setObjectSpecialProperty(
                handle,
                sim.objectspecialproperty_renderable
                + sim.objectspecialproperty_measurable
                + sim.objectspecialproperty_detectable_all,
            )
        except Exception:
            pass


def create_path_segment(
    sim,
    alias: str,
    start: tuple[float, float],
    end: tuple[float, float],
    parent: int,
    color: tuple[float, float, float],
) -> int:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = math.hypot(dx, dy)
    yaw = math.atan2(dy, dx)
    mid = ((start[0] + end[0]) * 0.5, (start[1] + end[1]) * 0.5, 0.012)
    return create_box(
        sim,
        alias,
        (length, 0.045, 0.012),
        mid,
        color,
        parent,
        yaw=yaw,
        respondable=False,
        detectable=False,
    )


def local_pose(
    origin: tuple[float, float, float],
    yaw: float,
    offset: tuple[float, float, float],
) -> tuple[float, float, float]:
    c = math.cos(yaw)
    s = math.sin(yaw)
    return (
        origin[0] + offset[0] * c - offset[1] * s,
        origin[1] + offset[0] * s + offset[1] * c,
        origin[2] + offset[2],
    )


def create_box_local(
    sim,
    alias: str,
    size: tuple[float, float, float],
    origin: tuple[float, float, float],
    offset: tuple[float, float, float],
    color: tuple[float, float, float],
    parent: int,
    yaw: float,
    *,
    local_yaw: float = 0.0,
    respondable: bool = False,
    detectable: bool = False,
) -> int:
    return create_box(
        sim,
        alias,
        size,
        local_pose(origin, yaw, offset),
        color,
        parent,
        yaw=yaw + local_yaw,
        respondable=respondable,
        detectable=detectable,
    )


def create_industrial_table(
    sim,
    alias: str,
    origin: tuple[float, float, float],
    yaw: float,
    parent: int,
) -> None:
    steel = (0.32, 0.34, 0.35)
    dark_steel = (0.12, 0.14, 0.15)
    wood = (0.42, 0.31, 0.19)
    rubber = (0.05, 0.06, 0.07)
    safety_yellow = (0.95, 0.72, 0.16)

    create_box_local(sim, f"{alias}_Top_Textured_Work_Surface", (1.02, 0.58, 0.060), origin, (0, 0, 0.76), wood, parent, yaw)
    create_box_local(sim, f"{alias}_Black_Rubber_Mat", (0.42, 0.28, 0.018), origin, (-0.17, -0.07, 0.805), rubber, parent, yaw)
    leg_index = 1
    for x in (-0.44, 0.44):
        for y in (-0.24, 0.24):
            create_box_local(sim, f"{alias}_Square_Tube_Leg_{leg_index:02d}", (0.055, 0.055, 0.72), origin, (x, y, 0.38), steel, parent, yaw)
            leg_index += 1
    create_box_local(sim, f"{alias}_Front_Cross_Brace", (0.94, 0.040, 0.055), origin, (0, -0.29, 0.42), dark_steel, parent, yaw)
    create_box_local(sim, f"{alias}_Back_Cross_Brace", (0.94, 0.040, 0.055), origin, (0, 0.29, 0.42), dark_steel, parent, yaw)
    create_box_local(sim, f"{alias}_Tool_Tray", (0.34, 0.16, 0.035), origin, (0.27, 0.12, 0.83), steel, parent, yaw)
    for i, x in enumerate((-0.31, -0.23, 0.18, 0.30), start=1):
        create_box_local(sim, f"{alias}_Small_Tool_{i:02d}", (0.10, 0.026, 0.018), origin, (x, 0.20, 0.84), safety_yellow if i % 2 else dark_steel, parent, yaw)


def create_industrial_chair(
    sim,
    alias: str,
    origin: tuple[float, float, float],
    yaw: float,
    parent: int,
) -> None:
    seat = (0.10, 0.16, 0.20)
    frame = (0.08, 0.09, 0.10)
    create_box_local(sim, f"{alias}_Seat", (0.40, 0.38, 0.055), origin, (0, 0, 0.46), seat, parent, yaw)
    create_box_local(sim, f"{alias}_Back_Rest", (0.40, 0.055, 0.44), origin, (0, 0.20, 0.71), seat, parent, yaw)
    create_box_local(sim, f"{alias}_Lower_Back_Frame", (0.44, 0.035, 0.045), origin, (0, 0.225, 0.52), frame, parent, yaw)
    leg_index = 1
    for x in (-0.16, 0.16):
        for y in (-0.14, 0.14):
            create_box_local(sim, f"{alias}_Leg_{leg_index:02d}", (0.040, 0.040, 0.46), origin, (x, y, 0.23), frame, parent, yaw)
            leg_index += 1
    create_box_local(sim, f"{alias}_Foot_Rail_Front", (0.38, 0.030, 0.035), origin, (0, -0.18, 0.25), frame, parent, yaw)


def create_storage_shelf(
    sim,
    alias: str,
    origin: tuple[float, float, float],
    yaw: float,
    parent: int,
) -> None:
    post = (0.10, 0.12, 0.14)
    shelf = (0.32, 0.36, 0.38)
    bin_blue = (0.06, 0.22, 0.38)
    bin_orange = (0.88, 0.40, 0.12)
    tool_dark = (0.06, 0.07, 0.08)
    width = 0.92
    depth = 0.34
    height = 1.04

    post_index = 1
    for x in (-width / 2, width / 2):
        for y in (-depth / 2, depth / 2):
            create_box_local(sim, f"{alias}_Post_{post_index:02d}", (0.040, 0.040, height), origin, (x, y, height / 2), post, parent, yaw)
            post_index += 1
    for level, z in enumerate((0.18, 0.43, 0.68, 0.93), start=1):
        create_box_local(sim, f"{alias}_Shelf_Level_{level:02d}", (width + 0.08, depth + 0.04, 0.045), origin, (0, 0, z), shelf, parent, yaw)
    for i, (x, z, color) in enumerate(((-0.26, 0.55, bin_blue), (0.02, 0.55, bin_orange), (0.27, 0.55, bin_blue), (-0.18, 0.80, bin_orange), (0.22, 0.80, tool_dark)), start=1):
        create_box_local(sim, f"{alias}_Storage_Bin_{i:02d}", (0.22, 0.22, 0.16), origin, (x, 0.01, z), color, parent, yaw)
    create_box_local(sim, f"{alias}_Long_Tool_Tube", (0.68, 0.050, 0.045), origin, (0.02, -0.02, 1.03), tool_dark, parent, yaw)


def create_pallet_stack(
    sim,
    alias: str,
    origin: tuple[float, float, float],
    yaw: float,
    parent: int,
) -> None:
    plank = (0.45, 0.31, 0.17)
    crate = (0.25, 0.29, 0.24)
    for i, y in enumerate((-0.22, 0.0, 0.22), start=1):
        create_box_local(sim, f"{alias}_Pallet_Plank_{i:02d}", (0.82, 0.055, 0.055), origin, (0, y, 0.055), plank, parent, yaw)
    for i, x in enumerate((-0.28, 0.0, 0.28), start=1):
        create_box_local(sim, f"{alias}_Pallet_Skid_{i:02d}", (0.08, 0.54, 0.055), origin, (x, 0, 0.115), plank, parent, yaw)
    create_box_local(sim, f"{alias}_Parts_Crate_Left", (0.32, 0.28, 0.24), origin, (-0.20, -0.06, 0.275), crate, parent, yaw)
    create_box_local(sim, f"{alias}_Parts_Crate_Right", (0.30, 0.26, 0.20), origin, (0.18, 0.08, 0.255), (0.20, 0.24, 0.28), parent, yaw)


def create_hazard_stripes(
    sim,
    alias: str,
    origin: tuple[float, float, float],
    yaw: float,
    parent: int,
    *,
    count: int = 10,
    spacing: float = 0.17,
) -> None:
    for i in range(count):
        color = (0.94, 0.72, 0.10) if i % 2 == 0 else (0.04, 0.04, 0.04)
        create_box_local(
            sim,
            f"{alias}_Stripe_{i + 1:02d}",
            (0.11, 0.035, 0.010),
            origin,
            ((i - (count - 1) / 2.0) * spacing, 0, 0.014),
            color,
            parent,
            yaw,
            local_yaw=math.radians(28),
        )


def create_wall_industrial_details(sim, parent: int) -> None:
    conduit = (0.08, 0.10, 0.12)
    panel = (0.18, 0.22, 0.25)
    warning = (0.95, 0.72, 0.12)
    create_box(sim, "A2F_North_Wall_Cable_Tray", (3.80, 0.035, 0.045), (-0.10, 2.555, 0.49), conduit, parent, respondable=False, detectable=False)
    create_box(sim, "A2F_South_Wall_Air_Line", (3.20, 0.035, 0.040), (0.20, -2.555, 0.45), conduit, parent, respondable=False, detectable=False)
    create_box(sim, "A2F_East_Wall_Control_Cabinet", (0.050, 0.48, 0.60), (2.555, 1.16, 0.40), panel, parent, respondable=False, detectable=False)
    create_box(sim, "A2F_East_Wall_Control_Cabinet_Door", (0.055, 0.38, 0.45), (2.525, 1.16, 0.40), (0.12, 0.14, 0.16), parent, respondable=False, detectable=False)
    create_box(sim, "A2F_East_Wall_EStop_Button", (0.060, 0.07, 0.07), (2.49, 1.02, 0.46), (0.78, 0.05, 0.04), parent, respondable=False, detectable=False)
    create_box(sim, "A2F_East_Wall_Status_Light", (0.060, 0.06, 0.06), (2.49, 1.30, 0.52), (0.05, 0.72, 0.26), parent, respondable=False, detectable=False)
    create_box(sim, "A2F_North_Wall_Caution_Plate", (0.50, 0.040, 0.22), (-1.72, 2.548, 0.34), warning, parent, respondable=False, detectable=False)


def build_room(sim) -> int:
    room = sim.createDummy(0.045, None)
    sim.setObjectAlias(room, "A2F_Follower_Room")

    create_box(
        sim,
        "A2F_Room_Floor_Base",
        (5.20, 5.20, 0.010),
        (0.0, 0.0, -0.007),
        (0.55, 0.57, 0.58),
        room,
        respondable=False,
        detectable=False,
    )

    tile_size = 0.65
    for ix in range(8):
        for iy in range(8):
            x = -2.275 + ix * tile_size
            y = -2.275 + iy * tile_size
            shade = 0.67 if (ix + iy) % 2 == 0 else 0.61
            create_box(
                sim,
                f"A2F_Floor_Tile_{ix + 1:02d}_{iy + 1:02d}",
                (tile_size - 0.012, tile_size - 0.012, 0.006),
                (x, y, 0.0),
                (shade, shade + 0.012, shade + 0.018),
                room,
                respondable=False,
                detectable=False,
            )

    wall_color = (0.12, 0.16, 0.20)
    create_box(sim, "A2F_Room_Wall_North", (5.20, 0.06, 0.55), (0.0, 2.60, 0.275), wall_color, room, respondable=False)
    create_box(sim, "A2F_Room_Wall_South", (5.20, 0.06, 0.55), (0.0, -2.60, 0.275), wall_color, room, respondable=False)
    create_box(sim, "A2F_Room_Wall_East", (0.06, 5.20, 0.55), (2.60, 0.0, 0.275), wall_color, room, respondable=False)
    create_box(sim, "A2F_Room_Wall_West", (0.06, 5.20, 0.55), (-2.60, 0.0, 0.275), wall_color, room, respondable=False)

    create_industrial_table(sim, "A2F_Industrial_Work_Table_NorthEast", (2.02, 2.04, 0.0), math.radians(-7), room)
    create_industrial_table(sim, "A2F_Industrial_Inspection_Table_NorthWest", (-2.02, 2.04, 0.0), math.radians(8), room)
    create_industrial_chair(sim, "A2F_Industrial_Operator_Chair", (1.42, 2.06, 0.0), math.radians(94), room)
    create_storage_shelf(sim, "A2F_Tool_Shelf_East_Wall", (2.32, -0.32, 0.0), math.radians(90), room)
    create_storage_shelf(sim, "A2F_Parts_Shelf_South_Wall", (1.72, -2.28, 0.0), 0.0, room)
    create_pallet_stack(sim, "A2F_Industrial_Pallet_Stack_SouthWest", (-2.10, -2.12, 0.0), math.radians(-8), room)
    create_wall_industrial_details(sim, room)
    create_hazard_stripes(sim, "A2F_Hazard_Texture_North_Service_Aisle", (-0.70, 2.34, 0.0), 0.0, room, count=12)
    create_hazard_stripes(sim, "A2F_Hazard_Texture_South_Service_Aisle", (0.78, -2.34, 0.0), 0.0, room, count=10)
    create_hazard_stripes(sim, "A2F_Hazard_Texture_East_Shelf_Clearance", (2.34, -1.18, 0.0), math.radians(90), room, count=8)

    for index, x in enumerate((-1.95, -0.65, 0.65, 1.95), start=1):
        create_box(sim, f"A2F_Floor_Expansion_Joint_X_{index:02d}", (0.018, 5.08, 0.007), (x, 0.0, 0.011), (0.34, 0.35, 0.36), room, respondable=False, detectable=False)
    for index, y in enumerate((-1.95, -0.65, 0.65, 1.95), start=1):
        create_box(sim, f"A2F_Floor_Expansion_Joint_Y_{index:02d}", (5.08, 0.018, 0.007), (0.0, y, 0.012), (0.34, 0.35, 0.36), room, respondable=False, detectable=False)

    circle_path_color = (0.08, 0.40, 0.76)
    for index in range(len(WAYPOINTS) - 1):
        create_path_segment(sim, f"A2F_Bill_Walking_Path_Segment_{index + 1:02d}", WAYPOINTS[index], WAYPOINTS[index + 1], room, circle_path_color)

    for index, waypoint in enumerate(WAYPOINTS, start=1):
        should_show_marker = index == 1
        alias = "A2F_Bill_Start_Finish_Waypoint" if index == 1 else f"A2F_Bill_Waypoint_{index:02d}"
        if should_show_marker:
            create_box(
                sim,
                alias,
                (0.22, 0.22, 0.020),
                (waypoint[0], waypoint[1], 0.025),
                (0.04, 0.62, 0.28),
                room,
                respondable=False,
                detectable=False,
            )
        create_dummy(sim, f"A2F_Bill_Waypoint_Handle_{index:02d}", (waypoint[0], waypoint[1], 0.13), room, size=0.035)

    create_box(
        sim,
        "A2F_Pioneer_Target_Follow_Distance_Ring",
        (0.82, 0.82, 0.010),
        (WAYPOINTS[-1][0], WAYPOINTS[-1][1], 0.017),
        (0.86, 0.68, 0.18),
        room,
        respondable=False,
        detectable=False,
    )
    create_box(
        sim,
        "A2F_Control_Mode_Panel_All_Modes",
        (1.62, 0.05, 0.42),
        (-1.64, 2.54, 0.50),
        (0.06, 0.08, 0.11),
        room,
        respondable=False,
        detectable=False,
    )
    create_box(sim, "A2F_Control_Mode_Light_P", (0.16, 0.055, 0.12), (-2.28, 2.50, 0.55), (0.88, 0.22, 0.14), room, respondable=False, detectable=False)
    create_box(sim, "A2F_Control_Mode_Light_PI", (0.16, 0.055, 0.12), (-1.96, 2.50, 0.55), (0.92, 0.68, 0.18), room, respondable=False, detectable=False)
    create_box(sim, "A2F_Control_Mode_Light_PID", (0.16, 0.055, 0.12), (-1.64, 2.50, 0.55), (0.12, 0.58, 0.28), room, respondable=False, detectable=False)
    create_box(sim, "A2F_Control_Mode_Light_LQR", (0.16, 0.055, 0.12), (-1.32, 2.50, 0.55), (0.18, 0.42, 0.84), room, respondable=False, detectable=False)
    create_box(sim, "A2F_Control_Mode_Light_NMPC", (0.16, 0.055, 0.12), (-1.00, 2.50, 0.55), (0.00, 0.58, 0.62), room, respondable=False, detectable=False)
    create_box(
        sim,
        "A2F_CSV_Data_Logging_Station",
        (0.62, 0.34, 0.28),
        (2.16, -2.18, 0.14),
        (0.08, 0.10, 0.13),
        room,
        respondable=False,
    )
    create_dummy(sim, "A2F_CSV_Output_Reference_Point", (2.16, -2.18, 0.36), room, size=0.045)

    return room


def set_initial_layout(sim) -> None:
    pioneer = safe_get(sim, "/PioneerP3DX")
    bill = safe_get(sim, "/Bill")
    plant = safe_get(sim, "/indoorPlant")
    camera = safe_get(sim, "/DefaultCamera")

    if pioneer >= 0:
        sim.setObjectAlias(pioneer, "PioneerP3DX")
        sim.setObjectPosition(pioneer, [1.82, 0.40, 0.1388])
        sim.setObjectOrientation(pioneer, [0.0, 0.0, BILL_START_ANGLE_RAD + math.pi / 2.0])
    if bill >= 0:
        sim.setObjectAlias(bill, "Bill")
        sim.setObjectPosition(bill, [WAYPOINTS[0][0], WAYPOINTS[0][1], 0.0])
        sim.setObjectOrientation(bill, [0.0, 0.0, BILL_START_ANGLE_RAD + math.pi / 2.0])
        make_bill_visual_target_only(sim)
    if plant >= 0:
        try:
            sim.removeObject(plant)
        except Exception:
            sim.setObjectPosition(plant, [-3.2, -3.2, -0.5])
    if camera >= 0:
        sim.setObjectPosition(camera, [4.35, -5.10, 4.20])
        sim.setObjectOrientation(camera, [math.radians(60), 0.0, math.radians(42)])


def attach_scripts(sim, room: int) -> None:
    robot = safe_get(sim, "/PioneerP3DX")
    if robot < 0:
        raise RuntimeError("PioneerP3DX was not found in the scene")
    if safe_get(sim, "/Bill") < 0:
        raise RuntimeError("Bill was not found in the scene")

    controller_text = CONTROLLER.read_text(encoding="utf-8")
    controller = sim.createScript(sim.scripttype_simulation, controller_text, 0, "lua")
    sim.setObjectAlias(controller, "Pioneer_PID_Follower_Controller")
    sim.setObjectParent(controller, robot, False)

    bill_text = BILL_MANAGER.read_text(encoding="utf-8")
    bill_script = sim.createScript(sim.scripttype_simulation, bill_text, 0, "lua")
    sim.setObjectAlias(bill_script, "A2F_Bill_Walking_Room_Manager")
    sim.setObjectParent(bill_script, room, False)

    logger_text = CSV_LOGGER.read_text(encoding="utf-8").replace("__A2F_LOG_DIR__", LOG_DIR.as_posix())
    logger = sim.createScript(sim.scripttype_simulation, logger_text, 0, "lua")
    sim.setObjectAlias(logger, "A2F_Follower_CSV_Logger")
    sim.setObjectParent(logger, room, False)

    documentation = """-- VIU SRM Actividad 2.1 - Basic Bill follower experiment
-- Objects are intentionally named with the A2F_ prefix for review.
-- Bill walks two circular laps with a 2x faster smooth acceleration/deceleration profile and then stops.
-- The workspace uses industrial tables, one operator chair, shelves, safety strips, wall panels and floor texture details.
-- PioneerP3DX/Pioneer_PID_Follower_Controller follows Bill.
-- Set string signal followerControlMode to P, PI, PID, LQR or NMPC before starting.
-- CSV data are exported to actividad2/coppeliasim/follower_pid_logs.
-- P: proportional distance follower, steady moving offset is expected.
-- PI: integral term reduces steady-state distance offset.
-- PID: derivative term damps speed-change and stop oscillations.
-- LQR: offline Riccati gain on linearized tracking error with wheel command, delta-u and power telemetry.
-- NMPC: nonlinear model predictive controller with direct shooting, constraints and delta-u cost.
"""
    doc = sim.createScript(sim.scripttype_passive, documentation, 0, "lua")
    sim.setObjectAlias(doc, "A2F_Follower_Experiment_Documentation")
    sim.setObjectParent(doc, room, True)


def sim_step(sim, sim_loop) -> None:
    if sim.getSimulationState() == sim.simulation_stopped:
        return
    current = sim.getSimulationTime()
    for _ in range(80):
        sim_loop(None, 0)
        if current != sim.getSimulationTime() or sim.getSimulationState() == sim.simulation_stopped:
            break


def clear_runtime_signals(sim) -> None:
    for name in (
        "followerMode",
        "followerState",
        "followerDistance",
        "followerDistanceError",
        "followerHeadingError",
        "followerIntegralError",
        "followerDerivativeError",
        "followerControlV",
        "followerControlW",
        "followerReady",
        "followerWheelLeftLinear",
        "followerWheelRightLinear",
        "followerWheelLeftOmega",
        "followerWheelRightOmega",
        "followerWheelLeftU",
        "followerWheelRightU",
        "followerWheelLeftDeltaU",
        "followerWheelRightDeltaU",
        "followerWheelLeftPower",
        "followerWheelRightPower",
        "followerYawPower",
        "followerPowerTotal",
        "followerEnergyJ",
        "billStopped",
        "billPathState",
        "billSpeed",
        "billLapProgress",
        "followerCsvPath",
    ):
        try:
            sim.clearStringSignal(name)
        except Exception:
            pass
        try:
            sim.clearFloatSignal(name)
        except Exception:
            pass
        try:
            sim.clearInt32Signal(name)
        except Exception:
            pass


def read_float_signal(sim, name: str, fallback: float = 0.0) -> float:
    value = sim.getFloatSignal(name)
    return float(value) if value is not None else fallback


def read_string_signal(sim, name: str, fallback: str = "") -> str:
    value = sim.getStringSignal(name)
    return str(value) if value else fallback


def simulate_mode(sim, sim_loop, mode: str, duration: float | None = None) -> dict:
    if duration is None:
        duration = bill_path_duration() + VALIDATION_SETTLE_MARGIN_S

    clear_runtime_signals(sim)
    set_initial_layout(sim)
    sim.setStringSignal("followerControlMode", mode)

    robot = safe_get(sim, "/PioneerP3DX")
    bill = safe_get(sim, "/Bill")
    if robot < 0 or bill < 0:
        raise RuntimeError("Cannot validate without /PioneerP3DX and /Bill")

    csv_path = LOG_DIR / f"follower_{mode}.csv"
    rows: list[dict[str, object]] = []

    sim.startSimulation()
    for _ in range(int(duration / 0.01) + 1000):
        sim_step(sim, sim_loop)
        t = float(sim.getSimulationTime())
        bp = sim.getObjectPosition(bill, -1)
        rp = sim.getObjectPosition(robot, -1)
        row = {
            "t": round(t, 3),
            "mode": mode,
            "bill_x": bp[0],
            "bill_y": bp[1],
            "pioneer_x": rp[0],
            "pioneer_y": rp[1],
            "distance": read_float_signal(sim, "followerDistance", -1.0),
            "error": read_float_signal(sim, "followerDistanceError", 0.0),
            "heading_error": read_float_signal(sim, "followerHeadingError", 0.0),
            "control_v": read_float_signal(sim, "followerControlV", 0.0),
            "control_w": read_float_signal(sim, "followerControlW", 0.0),
            "integral": read_float_signal(sim, "followerIntegralError", 0.0),
            "derivative": read_float_signal(sim, "followerDerivativeError", 0.0),
            "wheel_left_linear": read_float_signal(sim, "followerWheelLeftLinear", 0.0),
            "wheel_right_linear": read_float_signal(sim, "followerWheelRightLinear", 0.0),
            "wheel_left_omega": read_float_signal(sim, "followerWheelLeftOmega", 0.0),
            "wheel_right_omega": read_float_signal(sim, "followerWheelRightOmega", 0.0),
            "u_left": read_float_signal(sim, "followerWheelLeftU", 0.0),
            "u_right": read_float_signal(sim, "followerWheelRightU", 0.0),
            "du_left": read_float_signal(sim, "followerWheelLeftDeltaU", 0.0),
            "du_right": read_float_signal(sim, "followerWheelRightDeltaU", 0.0),
            "wheel_left_power": read_float_signal(sim, "followerWheelLeftPower", 0.0),
            "wheel_right_power": read_float_signal(sim, "followerWheelRightPower", 0.0),
            "yaw_power": read_float_signal(sim, "followerYawPower", 0.0),
            "total_power": read_float_signal(sim, "followerPowerTotal", 0.0),
            "energy_j": read_float_signal(sim, "followerEnergyJ", 0.0),
            "follower_state": read_string_signal(sim, "followerState", "UNKNOWN"),
            "bill_state": read_string_signal(sim, "billPathState", "UNKNOWN"),
            "bill_speed": read_float_signal(sim, "billSpeed", 0.0),
        }
        rows.append(row)
        if t >= duration:
            break

    final_state = read_string_signal(sim, "followerState", "UNKNOWN")
    bill_state = read_string_signal(sim, "billPathState", "UNKNOWN")
    runtime_csv = read_string_signal(sim, "followerCsvPath", "")

    sim.stopSimulation()
    while sim.getSimulationState() != sim.simulation_stopped:
        sim_loop(None, 0)

    fieldnames = [
        "t",
        "mode",
        "bill_x",
        "bill_y",
        "pioneer_x",
        "pioneer_y",
        "distance",
        "error",
        "heading_error",
        "control_v",
        "control_w",
        "integral",
        "derivative",
        "wheel_left_linear",
        "wheel_right_linear",
        "wheel_left_omega",
        "wheel_right_omega",
        "u_left",
        "u_right",
        "du_left",
        "du_right",
        "wheel_left_power",
        "wheel_right_power",
        "yaw_power",
        "total_power",
        "energy_j",
        "follower_state",
        "bill_state",
        "bill_speed",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    moving_rows = [r for r in rows if float(r["t"]) > 4.0 and r["bill_state"] == "WALKING"]
    stopped_rows = [r for r in rows if r["bill_state"] == "STOPPED" and float(r["t"]) > duration - 10.0]
    error_rows = [r for r in rows if float(r["distance"]) > 0.0]
    moving_abs = [abs(float(r["error"])) for r in moving_rows]
    stopped_abs = [abs(float(r["error"])) for r in stopped_rows]
    all_abs = [abs(float(r["error"])) for r in error_rows]
    heading_abs = [abs(float(r["heading_error"])) for r in stopped_rows]
    bill_speed_values = [float(r["bill_speed"]) for r in moving_rows if float(r["bill_speed"]) > 0.0]
    power_values = [float(r["total_power"]) for r in rows if float(r["t"]) > 1.0]
    omega_values = [
        max(abs(float(r["wheel_left_omega"])), abs(float(r["wheel_right_omega"])))
        for r in rows
        if float(r["t"]) > 1.0
    ]
    control_values = [float(r["control_v"]) for r in rows if float(r["t"]) > 1.0]
    control_tv = sum(abs(b - a) for a, b in zip(control_values, control_values[1:]))
    wheel_u_values = [
        (float(r["u_left"]), float(r["u_right"]))
        for r in rows
        if float(r["t"]) > 1.0
    ]
    wheel_du_values = [
        (float(r["du_left"]), float(r["du_right"]))
        for r in rows
        if float(r["t"]) > 1.0
    ]
    wheel_u_total_variation = sum(
        abs(next_left - left) + abs(next_right - right)
        for (left, right), (next_left, next_right) in zip(wheel_u_values, wheel_u_values[1:])
    )
    wheel_du_abs = [abs(left) + abs(right) for left, right in wheel_du_values]
    wheel_du_rms = math.sqrt(
        statistics.fmean(left * left + right * right for left, right in wheel_du_values)
    ) if wheel_du_values else None
    stopped_v = [float(r["control_v"]) for r in rows if r["bill_state"] == "STOPPED"]
    stopped_delta_v = [b - a for a, b in zip(stopped_v, stopped_v[1:])]
    stop_velocity_flip_count = sum(1 for a, b in zip(stopped_delta_v, stopped_delta_v[1:]) if a * b < 0)

    stop_times = [float(r["t"]) for r in rows if r["bill_state"] == "STOPPED"]
    stop_time = min(stop_times) if stop_times else None
    final_row = rows[-1]

    return {
        "mode": mode,
        "csv": str(csv_path),
        "runtime_coppeliasim_csv": runtime_csv,
        "samples": len(rows),
        "final_state": final_state,
        "bill_state": bill_state,
        "bill_stop_time_s": round(stop_time, 3) if stop_time is not None else None,
        "mean_abs_error_moving_m": round(statistics.fmean(moving_abs), 4) if moving_abs else None,
        "mean_abs_error_after_stop_m": round(statistics.fmean(stopped_abs), 4) if stopped_abs else None,
        "max_abs_error_m": round(max(all_abs), 4) if all_abs else None,
        "final_distance_m": round(float(final_row["distance"]), 4),
        "final_abs_error_m": round(abs(float(final_row["error"])), 4),
        "final_heading_abs_rad": round(abs(float(final_row["heading_error"])), 4),
        "mean_heading_abs_after_stop_rad": round(statistics.fmean(heading_abs), 4) if heading_abs else None,
        "bill_speed_min_mps": round(min(bill_speed_values), 4) if bill_speed_values else None,
        "bill_speed_max_mps": round(max(bill_speed_values), 4) if bill_speed_values else None,
        "bill_speed_range_mps": round(max(bill_speed_values) - min(bill_speed_values), 4) if bill_speed_values else None,
        "mean_power_w": round(statistics.fmean(power_values), 4) if power_values else None,
        "peak_power_w": round(max(power_values), 4) if power_values else None,
        "energy_j": round(float(final_row["energy_j"]), 4),
        "energy_wh": round(float(final_row["energy_j"]) / 3600.0, 5),
        "peak_wheel_omega_rad_s": round(max(omega_values), 4) if omega_values else None,
        "control_v_total_variation": round(control_tv, 4),
        "wheel_u_total_variation": round(wheel_u_total_variation, 4),
        "wheel_delta_u_mean_abs": round(statistics.fmean(wheel_du_abs), 5) if wheel_du_abs else None,
        "wheel_delta_u_rms": round(wheel_du_rms, 5) if wheel_du_rms is not None else None,
        "stop_velocity_flip_count": stop_velocity_flip_count,
        "settled_seen": any(r["follower_state"] == "SETTLED" for r in rows),
    }


def build_and_save(sim, sim_loop) -> None:
    if sim.loadScene(str(SCENE)) < 0:
        raise RuntimeError(f"Could not load {SCENE}")
    for _ in range(3):
        sim_loop(None, 0)

    remove_previous_follower(sim)
    set_initial_layout(sim)
    room = build_room(sim)
    attach_scripts(sim, room)
    sim.saveScene(str(SCENE))


def validate_scene(sim, sim_loop) -> dict:
    results = [simulate_mode(sim, sim_loop, mode) for mode in CONTROL_MODES]
    by_mode = {r["mode"]: r for r in results}

    checks = {
        "scene_exists": SCENE.exists() and SCENE.stat().st_size > 1_000_000,
        "pioneer_present": safe_get(sim, "/PioneerP3DX") >= 0,
        "bill_present": safe_get(sim, "/Bill") >= 0,
        "room_present": safe_get(sim, "/A2F_Follower_Room") >= 0,
        "pioneer_pid_script_attached": safe_get(sim, "/PioneerP3DX/Pioneer_PID_Follower_Controller") >= 0,
        "bill_walk_script_attached": safe_get(sim, "/A2F_Follower_Room/A2F_Bill_Walking_Room_Manager") >= 0,
        "csv_logger_attached": safe_get(sim, "/A2F_Follower_Room/A2F_Follower_CSV_Logger") >= 0,
        "path_named_and_visible": all(safe_get(sim, f"/A2F_Follower_Room/A2F_Bill_Walking_Path_Segment_{i:02d}") >= 0 for i in range(1, len(WAYPOINTS))),
        "csvs_written": all(Path(r["csv"]).exists() and Path(r["csv"]).stat().st_size > 200 for r in results),
        "all_modes_sampled": all(r["samples"] >= 500 for r in results),
        "bill_stops_in_each_mode": all(r["bill_state"] == "STOPPED" for r in results),
        "bill_accel_decel_profile_recorded": all(
            r["bill_speed_range_mps"] is not None and r["bill_speed_range_mps"] >= BILL_SPEED_AMPLITUDE_MPS * 1.6
            for r in results
        ),
        "pid_settles": by_mode["PID"]["settled_seen"] and by_mode["PID"]["final_abs_error_m"] <= 0.09,
        "pi_mode_recorded_for_comparison": by_mode["PI"]["samples"] >= 500
        and by_mode["PI"]["mean_abs_error_moving_m"] is not None,
        "p_has_measurable_moving_offset": by_mode["P"]["mean_abs_error_moving_m"] is not None
        and by_mode["P"]["mean_abs_error_moving_m"] >= 0.08,
        "pid_moving_error_is_controlled": by_mode["PID"]["mean_abs_error_moving_m"] is not None
        and by_mode["PID"]["mean_abs_error_moving_m"] <= 0.55,
        "pid_final_error_is_tight": by_mode["PID"]["final_abs_error_m"] <= 0.08,
        "lqr_mode_recorded": by_mode["LQR"]["samples"] >= 500
        and by_mode["LQR"]["mean_abs_error_moving_m"] is not None,
        "nmpc_mode_recorded": by_mode["NMPC"]["samples"] >= 500
        and by_mode["NMPC"]["mean_abs_error_moving_m"] is not None,
        "wheel_power_logged": all(r["mean_power_w"] is not None and r["energy_j"] > 0 for r in results),
        "wheel_command_du_logged": all(r["wheel_delta_u_rms"] is not None for r in results),
        "lqr_delta_u_smoother_than_pid": by_mode["LQR"]["wheel_delta_u_rms"] is not None
        and by_mode["PID"]["wheel_delta_u_rms"] is not None
        and by_mode["LQR"]["wheel_delta_u_rms"] < by_mode["PID"]["wheel_delta_u_rms"],
        "nmpc_delta_u_smoother_than_pid": by_mode["NMPC"]["wheel_delta_u_rms"] is not None
        and by_mode["PID"]["wheel_delta_u_rms"] is not None
        and by_mode["NMPC"]["wheel_delta_u_rms"] < by_mode["PID"]["wheel_delta_u_rms"],
        "nmpc_final_error_reasonable": by_mode["NMPC"]["final_abs_error_m"] <= 0.13
        and by_mode["NMPC"]["mean_abs_error_after_stop_m"] is not None
        and by_mode["NMPC"]["mean_abs_error_after_stop_m"] <= 0.11,
        "lqr_final_error_is_tight": by_mode["LQR"]["final_abs_error_m"] <= 0.10
        and by_mode["LQR"]["mean_abs_error_after_stop_m"] is not None
        and by_mode["LQR"]["mean_abs_error_after_stop_m"] <= 0.08,
    }

    result = {
        "scene": str(SCENE),
        "log_dir": str(LOG_DIR),
        "modes": results,
        "checks": checks,
    }
    result["passed"] = all(checks.values())
    return result


def main() -> int:
    for path in (SCENE, CONTROLLER, BILL_MANAGER, CSV_LOGGER):
        if not path.exists():
            raise FileNotFoundError(path)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    for old in LOG_DIR.glob("*.csv"):
        old.unlink()

    sim, sim_loop, sim_deinitialize = load_coppeliasim()
    try:
        build_and_save(sim, sim_loop)
        validation = validate_scene(sim, sim_loop)
        VALIDATION_JSON.write_text(json.dumps(validation, indent=2), encoding="utf-8")
        print(json.dumps(validation, indent=2))
        return 0 if validation["passed"] else 2
    finally:
        sim_deinitialize()


if __name__ == "__main__":
    raise SystemExit(main())
