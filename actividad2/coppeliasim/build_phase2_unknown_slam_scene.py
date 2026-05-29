"""Build the Phase 2 scene by adding unknown-map SLAM markers to Phase 1."""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

from scene_common import (
    read_float_signal,
    read_int_signal,
    read_string_signal,
    remove_by_alias,
    sim_step,
)


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.append(str(SCRIPT_DIR))

import build_phase1_basic_scene as phase1


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_SCENE = ROOT / "actividad2" / "coppeliasim" / "Sim_T2_Phase2_SLAM_Unknown.ttt"
VALIDATION_JSON = ROOT / "actividad2" / "coppeliasim" / "Sim_T2_Phase2_SLAM_Unknown_validation.json"
PHASE2_MANAGER = ROOT / "actividad2" / "coppeliasim" / "phase2_dynamic_unknown_manager.lua"
MAPPING_PROGRESS_MIN_PCT = 50.0


P2_PREFIXES = (
    "/P2_",
    "/Phase2_",
    "/Sim_T2_Phase2_",
)


def remove_previous_phase2(sim) -> None:
    """Clear both overlays before rebuilding the Phase 2 scene."""

    phase1.remove_previous_phase1(sim)
    remove_by_alias(sim, P2_PREFIXES, contains=("/Phase2_",))


def create_phase2_root(sim) -> int:
    root = sim.createDummy(0.05, None)
    sim.setObjectAlias(root, "Sim_T2_Phase2_SLAM_Unknown_Overlay")
    return root


def add_unknown_zone(sim, alias: str, xy: tuple[float, float], size: tuple[float, float], root: int) -> None:
    x, y = xy
    sx, sy = size
    phase1.create_box(
        sim,
        f"{alias}_Base",
        (sx, sy, 0.010),
        (x, y, 0.020),
        (0.23, 0.27, 0.30),
        root,
        respondable=False,
        detectable=False,
    )
    phase1.create_box(
        sim,
        f"{alias}_Border_N",
        (sx, 0.025, 0.020),
        (x, y + sy * 0.5, 0.040),
        (0.88, 0.50, 0.14),
        root,
        respondable=False,
        detectable=False,
    )
    phase1.create_box(
        sim,
        f"{alias}_Border_S",
        (sx, 0.025, 0.020),
        (x, y - sy * 0.5, 0.040),
        (0.88, 0.50, 0.14),
        root,
        respondable=False,
        detectable=False,
    )
    phase1.create_box(
        sim,
        f"{alias}_Border_E",
        (0.025, sy, 0.020),
        (x + sx * 0.5, y, 0.040),
        (0.88, 0.50, 0.14),
        root,
        respondable=False,
        detectable=False,
    )
    phase1.create_box(
        sim,
        f"{alias}_Border_W",
        (0.025, sy, 0.020),
        (x - sx * 0.5, y, 0.040),
        (0.88, 0.50, 0.14),
        root,
        respondable=False,
        detectable=False,
    )


def add_costmap_cells(sim, root: int) -> None:
    cells = [
        (-2.40, -1.55, 0.62),
        (-2.40, -0.78, 0.44),
        (-2.40, 0.00, 0.30),
        (-2.40, 0.78, 0.44),
        (-2.40, 1.55, 0.62),
        (-1.35, -1.55, 0.34),
        (-1.35, -0.78, 0.20),
        (-1.35, 0.00, 0.12),
        (-1.35, 0.78, 0.20),
        (-1.35, 1.55, 0.34),
        (-0.30, -1.55, 0.22),
        (-0.30, -0.78, 0.14),
        (-0.30, 0.00, 0.10),
        (-0.30, 0.78, 0.14),
        (-0.30, 1.55, 0.22),
        (0.75, -1.55, 0.30),
        (0.75, -0.78, 0.18),
        (0.75, 0.00, 0.12),
        (0.75, 0.78, 0.18),
        (0.75, 1.55, 0.30),
        (1.80, -1.55, 0.54),
        (1.80, -0.78, 0.36),
        (1.80, 0.00, 0.26),
        (1.80, 0.78, 0.36),
        (1.80, 1.55, 0.54),
    ]

    for index, (x, y, risk) in enumerate(cells, start=1):
        if risk >= 0.50:
            color = (0.82, 0.24, 0.16)
        elif risk >= 0.30:
            color = (0.88, 0.58, 0.14)
        else:
            color = (0.20, 0.58, 0.42)
        phase1.create_box(
            sim,
            f"P2_Costmap_Cell_{index:02d}",
            (0.46, 0.34, 0.009),
            (x, y, 0.035),
            color,
            root,
            respondable=False,
            detectable=False,
        )


def add_frontier_targets(sim, root: int) -> None:
    frontiers = [
        ("P2_Frontier_01_NE_Rack", (3.70, 3.70, 0.10), (0.88, 0.54, 0.12)),
        ("P2_Frontier_02_Center_Corridor", (0.10, 0.45, 0.10), (0.18, 0.66, 0.92)),
        ("P2_Frontier_03_West_Table", (-4.00, 1.10, 0.10), (0.16, 0.62, 0.42)),
        ("P2_Frontier_04_SE_Return", (3.70, -1.20, 0.10), (0.82, 0.32, 0.42)),
        ("P2_Frontier_05_Charging_Corridor", (-0.70, -3.60, 0.10), (0.68, 0.52, 0.90)),
        ("P2_Frontier_06_North_Unknown", (-1.20, 4.20, 0.10), (0.92, 0.72, 0.20)),
    ]

    for alias, position, color in frontiers:
        phase1.create_dummy(sim, alias, position, root, size=0.075)
        phase1.create_box(
            sim,
            f"{alias}_Marker",
            (0.22, 0.22, 0.020),
            (position[0], position[1], 0.035),
            color,
            root,
            respondable=False,
            detectable=False,
            yaw=math.radians(45.0),
        )


def add_unknown_obstacles(sim, root: int) -> None:
    # Unknown obstacles sit near the nominal route and leave recoverable gaps.
    phase1.create_box(
        sim,
        "P2_Unknown_Crate_A",
        (0.30, 0.46, 0.34),
        (-3.95, -0.70, 0.17),
        (0.54, 0.25, 0.16),
        root,
        yaw=math.radians(9.0),
    )
    phase1.create_box(
        sim,
        "P2_Unknown_Crate_B",
        (0.38, 0.28, 0.32),
        (4.10, 1.55, 0.16),
        (0.44, 0.32, 0.18),
        root,
        yaw=math.radians(-12.0),
    )
    phase1.create_cylinder(
        sim,
        "P2_Unknown_Drum_C",
        0.30,
        0.52,
        (-0.20, 4.20, 0.26),
        (0.20, 0.22, 0.24),
        root,
    )
    phase1.create_box(
        sim,
        "P2_Narrow_Gate_Left",
        (0.12, 0.46, 0.42),
        (0.35, -1.70, 0.21),
        (0.16, 0.20, 0.25),
        root,
        respondable=False,
        detectable=False,
    )
    phase1.create_box(
        sim,
        "P2_Narrow_Gate_Right",
        (0.12, 0.46, 0.42),
        (1.45, -1.70, 0.21),
        (0.16, 0.20, 0.25),
        root,
        respondable=False,
        detectable=False,
    )


def add_landmark_beacons(sim, root: int) -> None:
    landmarks = [
        ("P2_Landmark_AprilTag_NW", (-4.75, 4.45, 0.55), (0.08, 0.10, 0.12)),
        ("P2_Landmark_AprilTag_NE", (4.75, 4.45, 0.55), (0.08, 0.10, 0.12)),
        ("P2_Landmark_AprilTag_SE", (4.75, -4.65, 0.55), (0.08, 0.10, 0.12)),
        ("P2_Landmark_AprilTag_SW", (-4.75, -4.65, 0.55), (0.08, 0.10, 0.12)),
    ]

    for alias, position, color in landmarks:
        phase1.create_dummy(sim, alias, position, root, size=0.060)
        phase1.create_box(
            sim,
            f"{alias}_Panel",
            (0.18, 0.030, 0.18),
            (position[0], position[1], position[2]),
            color,
            root,
            respondable=False,
            detectable=True,
        )


def add_phase2_panels(sim, root: int) -> None:
    phase1.create_box(
        sim,
        "P2_Unknown_Map_Status_Panel",
        (1.36, 0.055, 0.55),
        (1.40, 4.72, 0.62),
        (0.05, 0.07, 0.09),
        root,
        respondable=False,
        detectable=False,
    )
    rows = [
        ("P2_Status_Row_1_UnknownMap", -0.20, (0.88, 0.50, 0.14)),
        ("P2_Status_Row_2_Frontiers", -0.05, (0.18, 0.66, 0.92)),
        ("P2_Status_Row_3_StaticObstacles", 0.10, (0.82, 0.24, 0.16)),
        ("P2_Status_Row_4_Replan", 0.25, (0.20, 0.58, 0.42)),
    ]
    for alias, dz, color in rows:
        phase1.create_box(
            sim,
            alias,
            (1.06, 0.060, 0.095),
            (1.40, 4.68, 0.49 + dz),
            color,
            root,
            respondable=False,
            detectable=False,
        )


def add_phase2_unknown_layer(sim) -> int:
    root = create_phase2_root(sim)

    add_unknown_zone(sim, "P2_Unknown_Zone_North", (-0.80, 2.80), (3.20, 1.80), root)
    add_unknown_zone(sim, "P2_Unknown_Zone_Center", (0.10, -0.20), (3.60, 2.10), root)
    add_costmap_cells(sim, root)
    add_frontier_targets(sim, root)
    add_unknown_obstacles(sim, root)
    add_landmark_beacons(sim, root)
    add_phase2_panels(sim, root)

    return root


def attach_phase2_manager(sim, root: int) -> None:
    text = PHASE2_MANAGER.read_text(encoding="utf-8")
    manager = sim.createScript(sim.scripttype_simulation, text, 0, "lua")
    sim.setObjectAlias(manager, "Phase2_Unknown_Map_Manager")
    sim.setObjectParent(manager, root, False)

    documentation = """-- VIU SRM Actividad 2 - Fase 2
-- Parte de Fase 1 y anade zonas desconocidas, frontiers y obstaculos.
-- R1 mantiene la mision T1/T2 mientras el mapa se completa en ejecucion.
"""
    doc = sim.createScript(sim.scripttype_passive, documentation, 0, "lua")
    sim.setObjectAlias(doc, "Phase2_Documentation")
    sim.setObjectParent(doc, root, False)


def validate_phase2_scene(sim, sim_loop) -> dict:
    robot = phase1.safe_get(sim, "/PioneerP3DX")
    b1 = phase1.safe_get(sim, "/B1")
    tool1 = phase1.safe_get(sim, "/T1")
    tool2 = phase1.safe_get(sim, "/T2")
    c1 = phase1.safe_get(sim, "/C1")
    if min(robot, b1, tool1, tool2, c1) < 0:
        raise RuntimeError("Cannot validate without /PioneerP3DX, /B1, /T1, /T2 and /C1")

    sim.startSimulation()

    task_states_seen: set[str] = set()
    motion_modes_seen: set[str] = set()
    planner_modes_seen: set[str] = set()
    phase2_states_seen: set[str] = set()
    max_mapping_evidence = 0.0
    max_risk = 0.0
    max_pose_error = 0.0
    max_slam_landmarks = 0
    max_replan_triggers = 0
    max_crossings = 0
    dynamic_obstacle_active_seen = False
    blocker_active_seen = False
    task_complete_seen = False
    charging_seen = False
    min_obstacle_seen = math.inf

    for _ in range(4700):
        sim_step(sim, sim_loop)
        t = sim.getSimulationTime()
        if t > 170:
            break

        task_state = read_string_signal(sim, "phase1TaskState", "UNKNOWN")
        motion_mode = read_string_signal(sim, "phase1MotionMode", "UNKNOWN")
        planner_mode = read_string_signal(sim, "phase1PlannerMode", "UNKNOWN")
        phase2_state = read_string_signal(sim, "phase2State", "UNKNOWN")
        risk = read_float_signal(sim, "phase1ObstacleRisk", 0.0)
        min_obstacle = read_float_signal(sim, "phase1MinObstacleDistance", -1.0)
        pose_error = read_float_signal(sim, "phase1PoseError", 0.0)
        slam_landmarks = read_int_signal(sim, "phase1SlamLandmarkCount", 0)
        mapping_evidence = read_float_signal(
            sim,
            "phase2MappingEvidencePct",
            read_float_signal(sim, "phase2MapRevealedPct", 0.0),
        )
        replan_triggers = read_int_signal(sim, "phase2ReplanTriggers", 0)
        crossings = read_int_signal(sim, "phase2ObstacleCrossings", 0)

        task_states_seen.add(task_state)
        motion_modes_seen.add(motion_mode)
        planner_modes_seen.add(planner_mode)
        phase2_states_seen.add(phase2_state)
        max_mapping_evidence = max(max_mapping_evidence, mapping_evidence)
        max_risk = max(max_risk, risk)
        max_pose_error = max(max_pose_error, pose_error)
        max_slam_landmarks = max(max_slam_landmarks, slam_landmarks)
        max_replan_triggers = max(max_replan_triggers, replan_triggers)
        max_crossings = max(max_crossings, crossings)
        dynamic_obstacle_active_seen = dynamic_obstacle_active_seen or read_int_signal(sim, "phase2DynamicObstacleActive", 0) == 1
        blocker_active_seen = blocker_active_seen or read_int_signal(sim, "phase2TemporaryBlockerActive", 0) == 1

        if min_obstacle > 0:
            min_obstacle_seen = min(min_obstacle_seen, min_obstacle)
        if read_int_signal(sim, "phase1TaskComplete", 0) == 1:
            task_complete_seen = True
        if read_int_signal(sim, "phase1Charging", 0) == 1 or task_state == "CHARGING":
            charging_seen = True
        if task_complete_seen and charging_seen and max_mapping_evidence > MAPPING_PROGRESS_MIN_PCT and t > 45:
            break

    final_task_state = read_string_signal(sim, "phase1TaskState", "UNKNOWN")
    final_motion_mode = read_string_signal(sim, "phase1MotionMode", "UNKNOWN")
    final_planner_mode = read_string_signal(sim, "phase1PlannerMode", "UNKNOWN")
    final_battery = read_float_signal(sim, "phase1BatteryLevel", -1.0)
    final_pose_error = read_float_signal(sim, "phase1PoseError", -1.0)
    b1_moved = read_float_signal(sim, "phase1B1MovedDistance", 0.0)
    phase1_compliance = read_string_signal(sim, "phase1Compliance", "")
    phase2_compliance = read_string_signal(sim, "phase2Compliance", "")
    completed_task_count = read_int_signal(sim, "phase1CompletedTaskCount", 0)
    sensor_count = read_int_signal(sim, "phase1SensorCount", 0)
    sensor_ray_count = read_int_signal(sim, "phase1SensorRayCount", 0)
    sensor_rays_visible = read_int_signal(sim, "phase1SensorRaysVisible", 0)
    kalman_active = read_int_signal(sim, "phase1KalmanActive", 0)
    slam_landmark_count = read_int_signal(sim, "phase1SlamLandmarkCount", 0)
    slam_updates = read_int_signal(sim, "phase1SlamUpdates", 0)
    frontier_count = read_int_signal(sim, "phase2FrontierCount", 0)
    unknown_cells = read_int_signal(sim, "phase2UnknownCells", 0)

    sim.stopSimulation()
    while sim.getSimulationState() != sim.simulation_stopped:
        sim_loop(None, 0)

    if min_obstacle_seen == math.inf:
        min_obstacle_seen = -1.0

    checks = {
        "scene_exists": OUTPUT_SCENE.exists() and OUTPUT_SCENE.stat().st_size > 1_000_000,
        "phase1_base_present": phase1.safe_get(sim, "/Sim_T2_Phase1_Basic_Cell") >= 0,
        "phase1_operator_sofa_present": phase1.safe_get(sim, "/P1_Operator_Sofa") >= 0
        or (
            phase1.safe_get(sim, "/P1_Operator_Sofa_Seat") >= 0
            and phase1.safe_get(sim, "/P1_Operator_Sofa_Back") >= 0
        ),
        "phase2_overlay_present": phase1.safe_get(sim, "/Sim_T2_Phase2_SLAM_Unknown_Overlay") >= 0,
        "unknown_zones_present": phase1.safe_get(sim, "/P2_Unknown_Zone_North_Base") >= 0
        and phase1.safe_get(sim, "/P2_Unknown_Zone_Center_Base") >= 0,
        "frontier_targets_present": all(
            phase1.safe_get(sim, f"/P2_Frontier_{index:02d}_{suffix}") >= 0
            for index, suffix in (
                (1, "NE_Rack"),
                (2, "Center_Corridor"),
                (3, "West_Table"),
                (4, "SE_Return"),
                (5, "Charging_Corridor"),
                (6, "North_Unknown"),
            )
        ),
        "costmap_grid_present": phase1.safe_get(sim, "/P2_Costmap_Cell_01") >= 0
        and phase1.safe_get(sim, "/P2_Costmap_Cell_25") >= 0,
        "unknown_obstacles_present": phase1.safe_get(sim, "/P2_Unknown_Crate_A") >= 0
        and phase1.safe_get(sim, "/P2_Unknown_Crate_B") >= 0
        and phase1.safe_get(sim, "/P2_Unknown_Drum_C") >= 0,
        "no_dynamic_pallet": phase1.safe_get(sim, "/P2_Dynamic_Pallet") < 0,
        "no_temporary_blocker": phase1.safe_get(sim, "/P2_Temporary_Blocker") < 0,
        "phase2_manager_attached": phase1.safe_get(
            sim, "/Sim_T2_Phase2_SLAM_Unknown_Overlay/Phase2_Unknown_Map_Manager"
        )
        >= 0,
        "r1_controller_attached": phase1.safe_get(sim, "/PioneerP3DX/Phase1_R1_Task_Controller") >= 0,
        "b1_walk_script_attached": phase1.safe_get(
            sim, "/Sim_T2_Phase1_Basic_Cell/Phase1_B1_Walking_Manager"
        )
        >= 0,
        "unknown_map_signal_present": "unknown_map" in phase2_compliance and unknown_cells >= 20,
        "frontier_signal_present": "frontier_targets" in phase2_compliance and frontier_count >= 6,
        "static_unknown_obstacle_signal_present": "static_unknown_obstacles" in phase2_compliance,
        "dynamic_obstacle_disabled": not dynamic_obstacle_active_seen and max_crossings == 0,
        "temporary_blocker_disabled": not blocker_active_seen,
        "mapping_evidence_progress_seen": max_mapping_evidence >= MAPPING_PROGRESS_MIN_PCT,
        "map_reveal_progress_seen": max_mapping_evidence >= MAPPING_PROGRESS_MIN_PCT,
        "replan_trigger_seen": max_replan_triggers >= 1 or "SLAM_WAYPOINT" in planner_modes_seen,
        "obstacle_avoidance_active": "AVOIDING" in motion_modes_seen or max_risk > 0.05,
        "slam_path_planning_active": "SLAM_WAYPOINT" in planner_modes_seen,
        "ekf_slam_obstacle_map_active": max_slam_landmarks >= 3 and slam_updates >= 5,
        "kalman_active": kalman_active == 1,
        "kalman_error_bounded": 0 <= final_pose_error <= 0.32 and max_pose_error <= 0.48,
        "sensor_suite_active": sensor_count >= 16,
        "sensor_rays_visualized": sensor_rays_visible == 1 and sensor_ray_count >= sensor_count,
        "phase1_mission_progress_seen": completed_task_count >= 3
        and {"DELIVER_T1_WS1", "RETURN_T1_RACK", "DELIVER_T2_WS2"}.issubset(task_states_seen),
        "phase1_compliance_inherited": "ekf_slam_obstacle_map" in phase1_compliance
        and "slam_path_planning" in phase1_compliance
        and "battery_charge" in phase1_compliance,
    }

    result = {
        "scene": str(OUTPUT_SCENE),
        "final_task_state": final_task_state,
        "final_motion_mode": final_motion_mode,
        "final_planner_mode": final_planner_mode,
        "task_states_seen": sorted(task_states_seen),
        "motion_modes_seen": sorted(motion_modes_seen),
        "planner_modes_seen": sorted(planner_modes_seen),
        "phase2_states_seen": sorted(phase2_states_seen),
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
        "max_mapping_evidence_pct": round(max_mapping_evidence, 1),
        "max_map_revealed_pct": round(max_mapping_evidence, 1),
        "max_replan_triggers": max_replan_triggers,
        "dynamic_obstacle_crossings": max_crossings,
        "frontier_count": frontier_count,
        "unknown_cells": unknown_cells,
        "task_complete_seen": task_complete_seen,
        "charging_seen": charging_seen,
        "checks": checks,
    }
    result["passed"] = all(checks.values())
    return result


def main() -> int:
    for path in (phase1.BASE_SCENE, phase1.R1_CONTROLLER, phase1.B1_MANAGER, PHASE2_MANAGER):
        if not path.exists():
            raise FileNotFoundError(path)

    sim, sim_loop, sim_deinitialize = phase1.load_coppeliasim()
    try:
        if sim.loadScene(str(phase1.BASE_SCENE)) < 0:
            raise RuntimeError(f"Could not load {phase1.BASE_SCENE}")
        for _ in range(3):
            sim_loop(None, 0)

        remove_previous_phase2(sim)
        phase1_group = phase1.add_phase1_warehouse(sim)
        phase1.set_initial_layout(sim)
        phase1.attach_scripts(sim, phase1_group)
        phase2_root = add_phase2_unknown_layer(sim)
        attach_phase2_manager(sim, phase2_root)

        sim.saveScene(str(OUTPUT_SCENE))
        validation = validate_phase2_scene(sim, sim_loop)
        VALIDATION_JSON.write_text(json.dumps(validation, indent=2), encoding="utf-8")
        print(json.dumps(validation, indent=2))
        return 0 if validation["passed"] else 2
    finally:
        sim_deinitialize()


if __name__ == "__main__":
    raise SystemExit(main())
