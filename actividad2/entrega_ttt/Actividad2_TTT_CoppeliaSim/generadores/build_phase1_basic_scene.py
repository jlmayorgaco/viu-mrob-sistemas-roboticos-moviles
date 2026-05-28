"""Build the Phase 1 warehouse scene for the single R1/B1 task flow."""

from __future__ import annotations

import json
import math
from pathlib import Path

from scene_common import (
    all_objects,
    create_box,
    create_cylinder,
    create_dummy,
    create_path_segment,
    load_library_model,
    load_coppeliasim,
    read_float_signal,
    read_int_signal,
    read_string_signal,
    remove_by_alias,
    safe_get,
    sim_step,
)


ROOT = Path(__file__).resolve().parents[2]
BASE_SCENE = ROOT / "actividad2" / "coppeliasim" / "Actividad2_2_Pioneer.ttt"
OUTPUT_SCENE = ROOT / "actividad2" / "coppeliasim" / "Sim_T2_Phase1_Basic.ttt"
VALIDATION_JSON = ROOT / "actividad2" / "coppeliasim" / "Sim_T2_Phase1_Basic_validation.json"
R1_CONTROLLER = ROOT / "actividad2" / "coppeliasim" / "phase1_r1_task_controller.lua"
B1_MANAGER = ROOT / "actividad2" / "coppeliasim" / "phase1_b1_walking_manager.lua"
VALIDATION_MAX_TIME_S = 240.0
VALIDATION_MAX_STEPS = 6500

B1_WAYPOINTS = [
    (-3.65, 3.05),
    (-2.50, 3.05),
    (-2.50, -3.05),
    (-0.80, -3.05),
    (1.20, -3.05),
    (3.65, -3.05),
    (2.50, -3.05),
    (2.50, 3.05),
    (0.95, 3.05),
    (-0.95, 3.05),
    (-3.65, 3.05),
]


def create_work_desk(
    sim,
    alias: str,
    position: tuple[float, float, float],
    color: tuple[float, float, float],
    parent: int,
) -> None:
    x, y, _z = position
    if load_library_model(
        sim,
        "furniture/tables/customizable table.ttm",
        alias,
        (x, y, 0.0),
        parent,
        scale=0.62,
    ) >= 0:
        return

    wood = color
    dark = (0.12, 0.11, 0.10)
    metal = (0.23, 0.25, 0.26)
    accent = (0.48, 0.58, 0.68)

    create_box(sim, alias, (0.96, 0.58, 0.08), (x, y, 0.31), wood, parent)
    for suffix, dx, dy in (
        ("Leg_FL", -0.39, -0.22),
        ("Leg_FR", 0.39, -0.22),
        ("Leg_BL", -0.39, 0.22),
        ("Leg_BR", 0.39, 0.22),
    ):
        create_box(sim, f"{alias}_{suffix}", (0.06, 0.06, 0.50), (x + dx, y + dy, 0.25), metal, parent)
    create_box(sim, f"{alias}_Drawer", (0.34, 0.08, 0.12), (x - 0.21, y - 0.31, 0.24), dark, parent)
    create_box(sim, f"{alias}_BackRail", (0.88, 0.05, 0.10), (x, y + 0.30, 0.39), metal, parent)
    create_box(sim, f"{alias}_WorkPad", (0.40, 0.26, 0.018), (x + 0.18, y, 0.36), accent, parent)


def create_operator_sofa(
    sim,
    alias: str,
    position: tuple[float, float],
    parent: int,
) -> None:
    x, y = position
    fabric = (0.18, 0.30, 0.40)
    cushion = (0.27, 0.42, 0.52)
    seam = (0.08, 0.12, 0.16)

    create_box(sim, f"{alias}_Seat", (0.42, 1.06, 0.16), (x, y, 0.16), cushion, parent)
    create_box(sim, f"{alias}_Back", (0.11, 1.12, 0.44), (x - 0.27, y, 0.36), fabric, parent)
    create_box(sim, f"{alias}_Arm_North", (0.46, 0.11, 0.28), (x - 0.02, y + 0.60, 0.24), fabric, parent)
    create_box(sim, f"{alias}_Arm_South", (0.46, 0.11, 0.28), (x - 0.02, y - 0.60, 0.24), fabric, parent)
    create_box(sim, f"{alias}_Seat_Divider", (0.36, 0.035, 0.018), (x + 0.02, y, 0.25), seam, parent, respondable=False, detectable=False)
    create_box(sim, f"{alias}_Front_Rail", (0.045, 0.94, 0.075), (x + 0.24, y, 0.23), seam, parent)


def create_material_piece(
    sim,
    tool_alias: str,
    position: tuple[float, float, float],
    parent: int,
) -> int:
    x, y, z = position
    handle = create_dummy(sim, tool_alias, position, parent, size=0.035)

    if tool_alias == "T1":
        steel = (0.64, 0.67, 0.68)
        edge = (0.34, 0.36, 0.37)
        dark = (0.12, 0.13, 0.14)
        amber = (0.95, 0.70, 0.12)

        create_box(sim, f"{tool_alias}_Machined_Plate", (0.30, 0.15, 0.032), (x, y, z), steel, handle, respondable=False, detectable=False)
        create_box(sim, f"{tool_alias}_Left_Rib", (0.036, 0.18, 0.050), (x - 0.13, y, z + 0.020), edge, handle, respondable=False, detectable=False)
        create_box(sim, f"{tool_alias}_Right_Rib", (0.036, 0.18, 0.050), (x + 0.13, y, z + 0.020), edge, handle, respondable=False, detectable=False)
        create_cylinder(sim, f"{tool_alias}_Center_Boss", 0.088, 0.032, (x, y, z + 0.033), dark, handle, respondable=False, detectable=False)
        for i, (dx, dy) in enumerate(((-0.095, -0.046), (0.095, -0.046), (-0.095, 0.046), (0.095, 0.046)), start=1):
            create_cylinder(sim, f"{tool_alias}_Bolt_{i}", 0.030, 0.018, (x + dx, y + dy, z + 0.034), amber, handle, respondable=False, detectable=False)
    else:
        board = (0.05, 0.30, 0.18)
        copper = (0.88, 0.48, 0.16)
        plastic = (0.08, 0.10, 0.13)
        blue = (0.22, 0.68, 0.92)
        gray = (0.62, 0.64, 0.66)

        create_box(sim, f"{tool_alias}_Composite_Board", (0.28, 0.16, 0.026), (x, y, z), board, handle, respondable=False, detectable=False)
        create_box(sim, f"{tool_alias}_Copper_Rail_A", (0.20, 0.018, 0.012), (x, y - 0.043, z + 0.024), copper, handle, respondable=False, detectable=False)
        create_box(sim, f"{tool_alias}_Copper_Rail_B", (0.20, 0.018, 0.012), (x, y + 0.043, z + 0.024), copper, handle, respondable=False, detectable=False)
        create_box(sim, f"{tool_alias}_Connector", (0.055, 0.13, 0.050), (x - 0.103, y, z + 0.030), plastic, handle, respondable=False, detectable=False)
        create_cylinder(sim, f"{tool_alias}_Blue_Capacitor", 0.054, 0.060, (x + 0.088, y - 0.030, z + 0.045), blue, handle, respondable=False, detectable=False)
        create_cylinder(sim, f"{tool_alias}_Metal_Pin", 0.032, 0.050, (x + 0.082, y + 0.045, z + 0.040), gray, handle, respondable=False, detectable=False)

    return handle


def create_tool_shelf(
    sim,
    shelf_alias: str,
    tool_alias: str,
    position: tuple[float, float],
    shelf_color: tuple[float, float, float],
    tool_color: tuple[float, float, float],
    parent: int,
    *,
    approach_offset_y: float,
    storage_offset_y: float = -0.04,
    visual_position: tuple[float, float] | None = None,
    rack_yaw: float | None = None,
) -> None:
    x, y = position
    visual_x, visual_y = visual_position if visual_position is not None else position

    create_dummy(sim, shelf_alias, (x, y + approach_offset_y, 0.22), parent, size=0.055)
    create_dummy(sim, f"{shelf_alias}_Storage", (x, y + storage_offset_y, 0.28), parent, size=0.045)
    if rack_yaw is None:
        rack_yaw = math.pi if approach_offset_y < 0 else 0.0
    imported = load_library_model(
        sim,
        "furniture/shelves-cupboards-racks/rack.ttm",
        f"P1_ToolRack_{tool_alias}",
        (visual_x, visual_y, 0.0),
        parent,
        yaw=rack_yaw,
        scale=0.62,
    )
    if imported < 0:
        frame = (0.16, 0.18, 0.20)
        shelf = shelf_color
        create_box(sim, f"P1_ToolShelf_{tool_alias}_Back", (0.82, 0.06, 0.70), (visual_x, visual_y + 0.18, 0.39), frame, parent)
        for suffix, dx in (("Left", -0.42), ("Right", 0.42)):
            create_box(sim, f"P1_ToolShelf_{tool_alias}_{suffix}_Post", (0.05, 0.10, 0.78), (visual_x + dx, visual_y, 0.39), frame, parent)
        for level, z in enumerate((0.18, 0.36, 0.54), start=1):
            create_box(sim, f"P1_ToolShelf_{tool_alias}_Level_{level}", (0.88, 0.34, 0.045), (visual_x, visual_y, z), shelf, parent)
        create_box(sim, f"P1_ToolShelf_{tool_alias}_Bin_A", (0.20, 0.18, 0.10), (visual_x - 0.24, visual_y - 0.03, 0.425), (0.33, 0.36, 0.38), parent)
        create_box(sim, f"P1_ToolShelf_{tool_alias}_Bin_B", (0.20, 0.18, 0.10), (visual_x + 0.24, visual_y - 0.03, 0.425), (0.33, 0.36, 0.38), parent)
    create_box(
        sim,
        f"P1_ToolShelf_{tool_alias}_Label",
        (0.50, 0.035, 0.09),
        (visual_x, visual_y + (0.20 if approach_offset_y > 0 else -0.20), 0.66),
        tool_color,
        parent,
        respondable=False,
        detectable=False,
    )
    create_material_piece(sim, tool_alias, (x, y + storage_offset_y, 0.280), parent)


def remove_previous_phase1(sim) -> None:
    prefixes = (
        "/P1_",
        "/Phase1_",
        "/Rack_T1",
        "/Rack_T2",
        "/T1",
        "/T2",
        "/C1",
        "/Landmark_",
        "/Sim_T2_Phase1_",
        "/GoalStation",
        "/mannequin",
    )
    script_aliases = {
        "/PioneerP3DX/Script",
        "/PioneerP3DX/Pioneer_Basic_Controller",
        "/PioneerP3DX/Pioneer_Professional_Controller",
        "/PioneerP3DX/Phase1_R1_Task_Controller",
        "/Bill/Script",
        "/B1/Script",
        "/Sim_T2_Phase1_Basic_Cell/Phase1_B1_Walking_Manager",
        "/Sim_T2_Phase1_Basic_Cell/Phase1_Documentation",
    }

    remove_by_alias(sim, prefixes, script_aliases, contains=("/Phase1_",))


def make_b1_visual_target_only(sim) -> None:
    for handle in all_objects(sim):
        try:
            alias = sim.getObjectAlias(handle, 1)
            object_type = sim.getObjectType(handle)
        except Exception:
            continue
        if alias != "/B1" and not alias.startswith("/B1/"):
            continue
        if object_type != sim.object_shape_type:
            continue
        try:
            sim.setObjectInt32Param(handle, sim.shapeintparam_respondable, 0)
            sim.setObjectSpecialProperty(
                handle,
                sim.objectspecialproperty_renderable + sim.objectspecialproperty_measurable,
            )
        except Exception:
            pass


def add_phase1_warehouse(sim) -> int:
    group = sim.createDummy(0.045, None)
    sim.setObjectAlias(group, "Sim_T2_Phase1_Basic_Cell")

    create_box(
        sim,
        "P1_Warehouse_Floor",
        (10.60, 10.20, 0.010),
        (0.0, -0.05, -0.008),
        (0.64, 0.67, 0.68),
        group,
        respondable=False,
        detectable=False,
    )

    tile = 0.53
    for ix in range(20):
        for iy in range(19):
            shade = 0.70 if (ix + iy) % 2 == 0 else 0.60
            create_box(
                sim,
                f"P1_Floor_Tile_{ix + 1:02d}_{iy + 1:02d}",
                (tile - 0.012, tile - 0.012, 0.004),
                (-5.035 + ix * tile, -4.82 + iy * tile, 0.0),
                (shade, shade + 0.012, shade + 0.016),
                group,
                respondable=False,
                detectable=False,
            )

    wall = (0.05, 0.12, 0.18)
    create_box(sim, "P1_Warehouse_Wall_North", (10.60, 0.06, 0.52), (0.0, 5.02, 0.26), wall, group, respondable=False)
    create_box(sim, "P1_Warehouse_Wall_South", (10.60, 0.06, 0.52), (0.0, -5.12, 0.26), wall, group, respondable=False)
    create_box(sim, "P1_Warehouse_Wall_West", (0.06, 10.15, 0.52), (-5.32, -0.05, 0.26), wall, group, respondable=False)
    create_box(sim, "P1_Warehouse_Wall_East", (0.06, 10.15, 0.52), (5.32, -0.05, 0.26), wall, group, respondable=False)

    # Obstacles sit near the nominal route and leave a narrow recoverable gap.
    create_box(sim, "P1_Obstacle_Pallet_A", (0.42, 0.52, 0.30), (-1.20, -1.55, 0.15), (0.58, 0.34, 0.14), group)
    create_box(sim, "P1_Obstacle_Pillar_B", (0.32, 0.32, 0.62), (-0.18, -0.20, 0.31), (0.16, 0.18, 0.20), group)
    create_box(sim, "P1_Obstacle_Crate_C", (0.50, 0.42, 0.34), (1.15, 1.35, 0.17), (0.54, 0.40, 0.18), group)

    create_work_desk(sim, "P1_WorkTable_1", (-3.65, 3.75, 0.0), (0.34, 0.24, 0.18), group)
    create_dummy(sim, "WS1_Tool_Drop", (-3.65, 3.05, 0.36), group, size=0.055)
    create_dummy(sim, "WS1_Work_Surface", (-3.65, 3.75, 0.42), group, size=0.045)
    create_work_desk(sim, "P1_WorkTable_2", (3.65, -3.75, 0.0), (0.24, 0.32, 0.20), group)
    create_dummy(sim, "WS2_Tool_Drop", (3.65, -3.05, 0.36), group, size=0.055)
    create_dummy(sim, "WS2_Work_Surface", (3.65, -3.75, 0.42), group, size=0.045)

    create_operator_sofa(sim, "P1_Operator_Sofa", (-4.60, 0.10), group)

    create_tool_shelf(
        sim,
        "Rack_T1",
        "T1",
        (-3.20, -4.02),
        (0.28, 0.33, 0.36),
        (0.95, 0.70, 0.12),
        group,
        approach_offset_y=0.52,
        storage_offset_y=-0.18,
        visual_position=(-3.20, -4.58),
        rack_yaw=math.radians(90),
    )
    create_dummy(sim, "Landmark_Rack_T1", (-3.20, -4.02, 0.62), group, size=0.045)

    create_tool_shelf(
        sim,
        "Rack_T2",
        "T2",
        (3.20, 4.02),
        (0.30, 0.34, 0.38),
        (0.22, 0.68, 0.92),
        group,
        approach_offset_y=-0.52,
        storage_offset_y=0.12,
        visual_position=(3.20, 4.58),
        rack_yaw=math.radians(90),
    )
    create_dummy(sim, "Landmark_Rack_T2", (3.20, 4.02, 0.62), group, size=0.045)

    create_box(
        sim,
        "P1_C1_ChargePad",
        (0.74, 0.74, 0.018),
        (-0.10, -4.32, 0.010),
        (0.08, 0.32, 0.62),
        group,
        respondable=False,
        detectable=False,
    )
    create_dummy(sim, "C1", (-0.10, -4.32, 0.16), group, size=0.075)
    create_dummy(sim, "Landmark_C1", (-0.10, -4.32, 0.50), group, size=0.045)

    create_box(
        sim,
        "P1_TaskQueue_Panel",
        (1.10, 0.06, 0.48),
        (-4.30, 4.80, 0.64),
        (0.04, 0.06, 0.08),
        group,
        respondable=False,
        detectable=False,
    )
    create_box(sim, "P1_TaskQueue_task1_T1_to_B1_WS1", (0.82, 0.07, 0.10), (-4.30, 4.76, 0.76), (0.94, 0.66, 0.16), group, respondable=False, detectable=False)
    create_box(sim, "P1_TaskQueue_task2_return_T1", (0.82, 0.07, 0.10), (-4.30, 4.76, 0.60), (0.92, 0.46, 0.12), group, respondable=False, detectable=False)
    create_box(sim, "P1_TaskQueue_task3_T2_to_B1_WS2", (0.82, 0.07, 0.10), (-4.30, 4.76, 0.44), (0.18, 0.52, 0.88), group, respondable=False, detectable=False)
    create_box(sim, "P1_Kalman_EKF_Status", (0.82, 0.07, 0.10), (-4.30, 4.76, 0.28), (0.12, 0.52, 0.86), group, respondable=False, detectable=False)

    for index, start in enumerate(B1_WAYPOINTS):
        end = B1_WAYPOINTS[(index + 1) % len(B1_WAYPOINTS)]
        create_path_segment(
            sim,
            f"P1_B1_Path_Segment_{index + 1:02d}",
            start,
            end,
            group,
            (0.10, 0.44, 0.78),
            z=0.014,
            width=0.040,
        )
        create_box(
            sim,
            f"P1_B1_Waypoint_{index + 1:02d}",
            (0.16, 0.16, 0.016),
            (start[0], start[1], 0.025),
            (0.12, 0.54, 0.82),
            group,
            respondable=False,
            detectable=False,
        )

    create_dummy(sim, "Landmark_Warehouse_NE", (4.70, 4.55, 0.28), group, size=0.045)
    create_dummy(sim, "Landmark_Warehouse_SW", (-4.70, -4.60, 0.28), group, size=0.045)
    return group


def set_initial_layout(sim) -> None:
    pioneer = safe_get(sim, "/PioneerP3DX")
    bill = safe_get(sim, "/Bill")
    camera = safe_get(sim, "/DefaultCamera")
    plant = safe_get(sim, "/indoorPlant")

    if pioneer >= 0:
        sim.setObjectAlias(pioneer, "PioneerP3DX")
        sim.setObjectPosition(pioneer, [-0.10, -4.32, 0.1388])
        sim.setObjectOrientation(pioneer, [0.0, 0.0, math.radians(92.0)])
    if bill >= 0:
        sim.setObjectAlias(bill, "B1")
        sim.setObjectPosition(bill, [B1_WAYPOINTS[0][0], B1_WAYPOINTS[0][1], 0.0])
        sim.setObjectOrientation(bill, [0.0, 0.0, math.radians(90.0)])
        make_b1_visual_target_only(sim)
    if plant >= 0:
        sim.setObjectPosition(plant, [4.35, 0.92, 0.165])
    if camera >= 0:
        sim.setObjectPosition(camera, [6.45, -7.20, 5.20])
        sim.setObjectOrientation(camera, [math.radians(62.0), 0.0, math.radians(41.0)])


def attach_scripts(sim, group: int) -> None:
    robot = safe_get(sim, "/PioneerP3DX")
    b1 = safe_get(sim, "/B1")
    if robot < 0:
        raise RuntimeError("PioneerP3DX was not found in the base scene")
    if b1 < 0:
        raise RuntimeError("B1/Bill was not found in the base scene")

    controller_text = R1_CONTROLLER.read_text(encoding="utf-8")
    controller = sim.createScript(sim.scripttype_simulation, controller_text, 0, "lua")
    sim.setObjectAlias(controller, "Phase1_R1_Task_Controller")
    sim.setObjectParent(controller, robot, False)

    b1_text = B1_MANAGER.read_text(encoding="utf-8")
    b1_script = sim.createScript(sim.scripttype_simulation, b1_text, 0, "lua")
    sim.setObjectAlias(b1_script, "Phase1_B1_Walking_Manager")
    sim.setObjectParent(b1_script, group, False)

    documentation = """-- VIU SRM Actividad 2 - Fase 1
-- Ciclo R1/B1: entrega T1, retorno T1, entrega T2, retorno T2.
-- La escena registra navegacion, SLAM, bateria y estados de tarea.
"""
    doc = sim.createScript(sim.scripttype_passive, documentation, 0, "lua")
    sim.setObjectAlias(doc, "Phase1_Documentation")
    sim.setObjectParent(doc, group, True)


def validate_scene(sim, sim_loop) -> dict:
    robot = safe_get(sim, "/PioneerP3DX")
    b1 = safe_get(sim, "/B1")
    tool1 = safe_get(sim, "/T1")
    tool2 = safe_get(sim, "/T2")
    c1 = safe_get(sim, "/C1")
    if min(robot, b1, tool1, tool2, c1) < 0:
        raise RuntimeError("Cannot validate without /PioneerP3DX, /B1, /T1, /T2 and /C1")

    sim.startSimulation()

    task_states_seen: set[str] = set()
    motion_modes_seen: set[str] = set()
    battery_modes_seen: set[str] = set()
    b1_stations_seen: set[str] = set()
    b1_actions_seen: set[str] = set()
    planner_modes_seen: set[str] = set()
    min_obstacle_seen = math.inf
    max_risk = 0.0
    max_pose_error = 0.0
    max_slam_landmarks = 0
    task_complete_seen = False
    charging_seen = False

    for _ in range(VALIDATION_MAX_STEPS):
        sim_step(sim, sim_loop)
        t = sim.getSimulationTime()
        if t > VALIDATION_MAX_TIME_S:
            break

        task_state = read_string_signal(sim, "phase1TaskState", "UNKNOWN")
        motion_mode = read_string_signal(sim, "phase1MotionMode", "UNKNOWN")
        battery_mode = read_string_signal(sim, "phase1BatteryMode", "UNKNOWN")
        b1_station = read_string_signal(sim, "phase1B1Station", "UNKNOWN")
        b1_action = read_string_signal(sim, "phase1B1Action", "UNKNOWN")
        planner_mode = read_string_signal(sim, "phase1PlannerMode", "UNKNOWN")
        risk = read_float_signal(sim, "phase1ObstacleRisk", 0.0)
        min_obstacle = read_float_signal(sim, "phase1MinObstacleDistance", -1.0)
        pose_error = read_float_signal(sim, "phase1PoseError", 0.0)
        slam_landmarks = read_int_signal(sim, "phase1SlamLandmarkCount", 0)

        task_states_seen.add(task_state)
        motion_modes_seen.add(motion_mode)
        battery_modes_seen.add(battery_mode)
        b1_stations_seen.add(b1_station)
        b1_actions_seen.add(b1_action)
        planner_modes_seen.add(planner_mode)
        max_risk = max(max_risk, risk)
        max_pose_error = max(max_pose_error, pose_error)
        max_slam_landmarks = max(max_slam_landmarks, slam_landmarks)
        if min_obstacle > 0:
            min_obstacle_seen = min(min_obstacle_seen, min_obstacle)
        if read_int_signal(sim, "phase1TaskComplete", 0) == 1:
            task_complete_seen = True
        if read_int_signal(sim, "phase1Charging", 0) == 1 or task_state == "CHARGING":
            charging_seen = True
        if task_complete_seen and charging_seen and t > 22:
            break

    final_task_state = read_string_signal(sim, "phase1TaskState", "UNKNOWN")
    final_motion_mode = read_string_signal(sim, "phase1MotionMode", "UNKNOWN")
    final_battery = read_float_signal(sim, "phase1BatteryLevel", -1.0)
    final_pose_error = read_float_signal(sim, "phase1PoseError", -1.0)
    b1_moved = read_float_signal(sim, "phase1B1MovedDistance", 0.0)
    compliance = read_string_signal(sim, "phase1Compliance", "")
    battery_task_accepted = read_int_signal(sim, "phase1BatteryTaskAccepted", 0)
    tool1_delivered = read_int_signal(sim, "phase1Tool1Delivered", 0)
    tool1_returned = read_int_signal(sim, "phase1Tool1Returned", 0)
    tool2_delivered = read_int_signal(sim, "phase1Tool2Delivered", 0)
    tool2_returned = read_int_signal(sim, "phase1Tool2Returned", 0)
    completed_task_count = read_int_signal(sim, "phase1CompletedTaskCount", 0)
    kalman_active = read_int_signal(sim, "phase1KalmanActive", 0)
    sensor_count = read_int_signal(sim, "phase1SensorCount", 0)
    sensor_ray_count = read_int_signal(sim, "phase1SensorRayCount", 0)
    sensor_rays_visible = read_int_signal(sim, "phase1SensorRaysVisible", 0)
    slam_landmark_count = read_int_signal(sim, "phase1SlamLandmarkCount", 0)
    slam_updates = read_int_signal(sim, "phase1SlamUpdates", 0)

    sim.stopSimulation()
    while sim.getSimulationState() != sim.simulation_stopped:
        sim_loop(None, 0)

    if min_obstacle_seen == math.inf:
        min_obstacle_seen = -1.0

    checks = {
        "scene_exists": OUTPUT_SCENE.exists() and OUTPUT_SCENE.stat().st_size > 1_000_000,
        "r1_pioneer_present": robot >= 0,
        "b1_person_present": b1 >= 0,
        "t1_tool_present": tool1 >= 0,
        "t2_tool_present": tool2 >= 0,
        "material_piece_visuals_present": safe_get(sim, "/T1/T1_Machined_Plate") >= 0
        and safe_get(sim, "/T1/T1_Center_Boss") >= 0
        and safe_get(sim, "/T2/T2_Composite_Board") >= 0
        and safe_get(sim, "/T2/T2_Blue_Capacitor") >= 0,
        "c1_charger_present": c1 >= 0,
        "warehouse_present": safe_get(sim, "/Sim_T2_Phase1_Basic_Cell") >= 0,
        "two_worktables_present": safe_get(sim, "/P1_WorkTable_1") >= 0
        and safe_get(sim, "/P1_WorkTable_2") >= 0,
        "operator_sofa_present": safe_get(sim, "/P1_Operator_Sofa") >= 0
        or (
            safe_get(sim, "/P1_Operator_Sofa_Seat") >= 0
            and safe_get(sim, "/P1_Operator_Sofa_Back") >= 0
        ),
        "two_tool_stations_present": safe_get(sim, "/Rack_T1") >= 0
        and safe_get(sim, "/Rack_T2") >= 0,
        "obstacles_present": safe_get(sim, "/P1_Obstacle_Pallet_A") >= 0
        and safe_get(sim, "/P1_Obstacle_Pillar_B") >= 0,
        "task_queue_present": safe_get(sim, "/P1_TaskQueue_task1_T1_to_B1_WS1") >= 0
        and safe_get(sim, "/P1_TaskQueue_task2_return_T1") >= 0
        and safe_get(sim, "/P1_TaskQueue_task3_T2_to_B1_WS2") >= 0,
        "r1_controller_attached": safe_get(sim, "/PioneerP3DX/Phase1_R1_Task_Controller") >= 0,
        "b1_walk_script_attached": safe_get(sim, "/Sim_T2_Phase1_Basic_Cell/Phase1_B1_Walking_Manager") >= 0,
        "task_accepted_by_battery": battery_task_accepted == 1,
        "t1_delivery_seen": tool1_delivered == 1 and "DELIVER_T1_WS1" in task_states_seen,
        "t1_return_seen": tool1_returned == 1 and "RETURN_T1_RACK" in task_states_seen,
        "t2_delivery_seen": tool2_delivered == 1 and "DELIVER_T2_WS2" in task_states_seen,
        "t2_return_seen": tool2_returned == 1 and "RETURN_T2_RACK" in task_states_seen,
        "full_task_sequence_complete": task_complete_seen and completed_task_count >= 4,
        "return_to_charge_seen": "TO_CHARGE" in task_states_seen or charging_seen,
        "charging_seen": charging_seen,
        "b1_moved_between_tables": b1_moved >= 2.40 and "WS1" in b1_stations_seen and "WS2" in b1_stations_seen,
        "b1_visual_work_actions_seen": "WORKING_T1_ON_WS1_TABLE" in b1_actions_seen
        and "WORKING_T2_ON_WS2_TABLE" in b1_actions_seen,
        "b1_visual_handoff_actions_seen": any(action.startswith("TAKING_T1") for action in b1_actions_seen)
        and any(action.startswith("READY_TO_TAKE_T2") or action.startswith("TAKING_T2") for action in b1_actions_seen),
        "obstacle_avoidance_active": "AVOIDING" in motion_modes_seen or max_risk > 0.05,
        "kalman_active": kalman_active == 1,
        "ekf_slam_obstacle_map_active": max_slam_landmarks >= 3 and slam_updates >= 5,
        "slam_path_planning_active": "SLAM_WAYPOINT" in planner_modes_seen,
        "kalman_error_bounded": 0 <= final_pose_error <= 0.28 and max_pose_error <= 0.42,
        "sensor_suite_active": sensor_count >= 16,
        "sensor_rays_visualized": sensor_rays_visible == 1 and sensor_ray_count >= sensor_count,
        "compliance_signal_present": "two_worktables" in compliance
        and "ekf_slam_obstacle_map" in compliance
        and "slam_path_planning" in compliance
        and "battery_charge" in compliance,
    }

    result = {
        "scene": str(OUTPUT_SCENE),
        "final_task_state": final_task_state,
        "final_motion_mode": final_motion_mode,
        "task_states_seen": sorted(task_states_seen),
        "motion_modes_seen": sorted(motion_modes_seen),
        "battery_modes_seen": sorted(battery_modes_seen),
        "b1_stations_seen": sorted(b1_stations_seen),
        "b1_actions_seen": sorted(b1_actions_seen),
        "planner_modes_seen": sorted(planner_modes_seen),
        "battery_level": round(final_battery, 2),
        "b1_moved_distance_m": round(b1_moved, 3),
        "completed_task_count": completed_task_count,
        "slam_landmark_count": slam_landmark_count,
        "slam_updates": slam_updates,
        "max_slam_landmarks": max_slam_landmarks,
        "min_obstacle_seen_m": round(min_obstacle_seen, 3),
        "max_obstacle_risk": round(max_risk, 3),
        "final_pose_error_m": round(final_pose_error, 3),
        "max_pose_error_m": round(max_pose_error, 3),
        "sensor_count": sensor_count,
        "sensor_ray_count": sensor_ray_count,
        "checks": checks,
    }
    result["passed"] = all(checks.values())
    return result


def main() -> int:
    for path in (BASE_SCENE, R1_CONTROLLER, B1_MANAGER):
        if not path.exists():
            raise FileNotFoundError(path)

    sim, sim_loop, sim_deinitialize = load_coppeliasim()
    try:
        if sim.loadScene(str(BASE_SCENE)) < 0:
            raise RuntimeError(f"Could not load {BASE_SCENE}")
        for _ in range(3):
            sim_loop(None, 0)

        remove_previous_phase1(sim)
        group = add_phase1_warehouse(sim)
        set_initial_layout(sim)
        attach_scripts(sim, group)

        sim.saveScene(str(OUTPUT_SCENE))
        validation = validate_scene(sim, sim_loop)
        VALIDATION_JSON.write_text(json.dumps(validation, indent=2), encoding="utf-8")
        print(json.dumps(validation, indent=2))
        return 0 if validation["passed"] else 2
    finally:
        sim_deinitialize()


if __name__ == "__main__":
    raise SystemExit(main())
