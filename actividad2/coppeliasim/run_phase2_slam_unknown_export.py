"""Run Sim_T2_Phase2_SLAM_Unknown.ttt and export unknown-map SLAM data.

R1 starts with only the static landmarks in memory. During the mission it adds
obstacles from sensor detections while the dynamic pallet and temporary blocker
force avoidance and replanning. This exporter records the plotting signals.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from statistics import fmean

import run_phase1_slam_export as phase1_export
from scene_common import positive, world_pose


ROOT = Path(__file__).resolve().parents[2]
SCENE = ROOT / "actividad2" / "coppeliasim" / "Sim_T2_Phase2_SLAM_Unknown.ttt"
LOG_DIR = ROOT / "actividad2" / "coppeliasim" / "phase2_slam_logs"
CSV_PATH = LOG_DIR / "phase2_slam_unknown_export.csv"
SUMMARY_JSON = LOG_DIR / "phase2_slam_unknown_summary.json"

PHASE2_FIELDS = (
    "phase2_state",
    "phase2_scenario",
    "phase2_compliance",
    "phase2_moved_objects",
    "phase2_motion_model",
    "mapping_evidence_pct",
    "map_revealed_pct",
    "dynamic_obstacle_signal_x",
    "dynamic_obstacle_signal_y",
    "dynamic_obstacle_active",
    "temporary_blocker_active",
    "obstacle_crossings",
    "replan_triggers",
    "frontier_count",
    "unknown_cells",
    "mapped_landmark_count",
    "mapping_update_count",
    "mapped_occupied_cells",
    "grid_mapping_update_count",
    "dynamic_pallet_x",
    "dynamic_pallet_y",
    "dynamic_pallet_theta",
    "temporary_blocker_x",
    "temporary_blocker_y",
    "temporary_blocker_theta",
)

CSV_FIELDS = phase1_export.CSV_FIELDS + PHASE2_FIELDS


def sample_row(sim, robot: int, b1: int, pallet: int, blocker: int) -> dict[str, float | int | str]:
    row = phase1_export.sample_row(sim, robot, b1)
    px, py, ptheta = world_pose(sim, pallet)
    bx, by, btheta = world_pose(sim, blocker)

    row.update(
        {
            "phase2_state": phase1_export.read_string_signal(sim, "phase2State", "UNKNOWN"),
            "phase2_scenario": phase1_export.read_string_signal(sim, "phase2Scenario", "UNKNOWN"),
            "phase2_compliance": phase1_export.read_string_signal(sim, "phase2Compliance", ""),
            "phase2_moved_objects": phase1_export.read_string_signal(sim, "phase2MovedObjects", ""),
            "phase2_motion_model": phase1_export.read_string_signal(sim, "phase2MotionModel", ""),
            "mapping_evidence_pct": round(
                phase1_export.read_float_signal(sim, "phase2MappingEvidencePct", 0.0), 5
            ),
            "map_revealed_pct": round(phase1_export.read_float_signal(sim, "phase2MapRevealedPct", 0.0), 5),
            "dynamic_obstacle_signal_x": round(phase1_export.read_float_signal(sim, "phase2DynamicObstacleX", math.nan), 5),
            "dynamic_obstacle_signal_y": round(phase1_export.read_float_signal(sim, "phase2DynamicObstacleY", math.nan), 5),
            "dynamic_obstacle_active": phase1_export.read_int_signal(sim, "phase2DynamicObstacleActive", 0),
            "temporary_blocker_active": phase1_export.read_int_signal(sim, "phase2TemporaryBlockerActive", 0),
            "obstacle_crossings": phase1_export.read_int_signal(sim, "phase2ObstacleCrossings", 0),
            "replan_triggers": phase1_export.read_int_signal(sim, "phase2ReplanTriggers", 0),
            "frontier_count": phase1_export.read_int_signal(sim, "phase2FrontierCount", 0),
            "unknown_cells": phase1_export.read_int_signal(sim, "phase2UnknownCells", 0),
            "mapped_landmark_count": phase1_export.read_int_signal(sim, "phase2MappedLandmarkCount", 0),
            "mapping_update_count": phase1_export.read_int_signal(sim, "phase2MappingUpdateCount", 0),
            "mapped_occupied_cells": phase1_export.read_int_signal(sim, "phase2MappedOccupiedCells", 0),
            "grid_mapping_update_count": phase1_export.read_int_signal(sim, "phase2GridMappingUpdateCount", 0),
            "dynamic_pallet_x": round(px, 5),
            "dynamic_pallet_y": round(py, 5),
            "dynamic_pallet_theta": round(ptheta, 5),
            "temporary_blocker_x": round(bx, 5),
            "temporary_blocker_y": round(by, 5),
            "temporary_blocker_theta": round(btheta, 5),
        }
    )
    return row


def write_csv(rows: list[dict[str, float | int | str]], csv_path: Path = CSV_PATH) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def threshold_time(rows: list[dict[str, float | int | str]], key: str, threshold: float) -> float | None:
    for row in rows:
        if float(row[key]) >= threshold:
            return round(float(row["t"]), 3)
    return None


def summarize(
    rows: list[dict[str, float | int | str]],
    csv_path: Path = CSV_PATH,
    summary_json: Path = SUMMARY_JSON,
    requested_algorithm: str = "KALMAN_LANDMARK",
) -> dict[str, object]:
    path_length = 0.0
    dynamic_travel = 0.0
    blocker_active_s = 0.0
    avoiding_s = 0.0
    slam_waypoint_s = 0.0
    prev = rows[0]

    for row in rows[1:]:
        dt = max(0.0, float(row["t"]) - float(prev["t"]))
        dx = float(row["robot_x"]) - float(prev["robot_x"])
        dy = float(row["robot_y"]) - float(prev["robot_y"])
        pdx = float(row["dynamic_pallet_x"]) - float(prev["dynamic_pallet_x"])
        pdy = float(row["dynamic_pallet_y"]) - float(prev["dynamic_pallet_y"])
        if math.isfinite(dx) and math.isfinite(dy):
            path_length += math.hypot(dx, dy)
        if math.isfinite(pdx) and math.isfinite(pdy):
            dynamic_travel += math.hypot(pdx, pdy)
        if int(prev["temporary_blocker_active"]) == 1:
            blocker_active_s += dt
        if str(prev["motion_mode"]) == "AVOIDING":
            avoiding_s += dt
        if str(prev["planner_mode"]) == "SLAM_WAYPOINT":
            slam_waypoint_s += dt
        prev = row

    final = rows[-1]
    pose_errors = [float(row["pose_error"]) for row in rows if math.isfinite(float(row["pose_error"]))]
    risks = [float(row["obstacle_risk"]) for row in rows if math.isfinite(float(row["obstacle_risk"]))]
    min_obstacles = positive(float(row["min_obstacle"]) for row in rows)

    result = {
        "scene": str(SCENE),
        "csv": str(csv_path),
        "unknown_map_prior_known": False,
        "requested_slam_algorithm": requested_algorithm,
        "slam_algorithm": str(final["slam_algorithm"]),
        "localization_mode": str(final["localization_mode"]),
        "phase2_scenario": str(final["phase2_scenario"]),
        "phase2_moved_objects": str(final["phase2_moved_objects"]),
        "phase2_motion_model": str(final["phase2_motion_model"]),
        "completed": int(final["task_complete"]) == 1 and int(final["completed_task_count"]) >= 4,
        "duration_s": round(float(final["t"]), 3),
        "samples": len(rows),
        "path_length_m": round(path_length, 3),
        "dynamic_pallet_travel_m": round(dynamic_travel, 3),
        "temporary_blocker_active_s": round(blocker_active_s, 3),
        "avoiding_s": round(avoiding_s, 3),
        "slam_waypoint_s": round(slam_waypoint_s, 3),
        "mapping_evidence_final_pct": round(float(final["mapping_evidence_pct"]), 3),
        "mapping_evidence_25pct_time_s": threshold_time(rows, "mapping_evidence_pct", 25.0),
        "mapping_evidence_50pct_time_s": threshold_time(rows, "mapping_evidence_pct", 50.0),
        "mapping_evidence_75pct_time_s": threshold_time(rows, "mapping_evidence_pct", 75.0),
        "map_revealed_final_pct": round(float(final["map_revealed_pct"]), 3),
        "map_reveal_25pct_time_s": threshold_time(rows, "map_revealed_pct", 25.0),
        "map_reveal_50pct_time_s": threshold_time(rows, "map_revealed_pct", 50.0),
        "map_reveal_75pct_time_s": threshold_time(rows, "map_revealed_pct", 75.0),
        "slam_landmarks_final": int(final["slam_landmarks"]),
        "slam_landmarks_max": max(int(row["slam_landmarks"]) for row in rows),
        "slam_updates": int(final["slam_updates"]),
        "grid_occupied_cells_final": int(final["grid_occupied_cells"]),
        "grid_updates": int(final["grid_updates"]),
        "frontier_count": int(final["frontier_count"]),
        "unknown_cells_declared": int(final["unknown_cells"]),
        "dynamic_obstacle_crossings": int(final["obstacle_crossings"]),
        "replan_triggers": int(final["replan_triggers"]),
        "planner_recovery_count": int(final.get("planner_recovery_count", 0)),
        "min_obstacle_m": round(min(min_obstacles), 3) if min_obstacles else None,
        "max_obstacle_risk": round(max(risks), 3) if risks else None,
        "mean_pose_error_m": round(fmean(pose_errors), 4) if pose_errors else None,
        "max_pose_error_m": round(max(pose_errors), 4) if pose_errors else None,
        "battery_start_pct": round(float(rows[0]["battery"]), 3),
        "battery_final_pct": round(float(final["battery"]), 3),
        "completed_task_count": int(final["completed_task_count"]),
        "final_task_state": str(final["task_state"]),
        "final_motion_mode": str(final["motion_mode"]),
        "planner_modes_seen": sorted({str(row["planner_mode"]) for row in rows}),
        "motion_modes_seen": sorted({str(row["motion_mode"]) for row in rows}),
        "task_states_seen": sorted({str(row["task_state"]) for row in rows}),
        "final_slam_map": str(final["slam_map"]),
        "final_grid_map": str(final["grid_map"]),
    }
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    summary_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def run(
    slam_algorithm: str = "KALMAN_LANDMARK",
    csv_path: Path = CSV_PATH,
    summary_json: Path = SUMMARY_JSON,
) -> dict[str, object]:
    if not SCENE.exists():
        raise FileNotFoundError(SCENE)

    sim, sim_loop, sim_deinitialize = phase1_export.load_coppeliasim()
    try:
        if sim.loadScene(str(SCENE)) < 0:
            raise RuntimeError(f"Could not load {SCENE}")
        for _ in range(3):
            sim_loop(None, 0)

        robot = phase1_export.safe_get(sim, "/PioneerP3DX")
        b1 = phase1_export.safe_get(sim, "/B1")
        pallet = phase1_export.safe_get(sim, "/P2_Dynamic_Pallet")
        blocker = phase1_export.safe_get(sim, "/P2_Temporary_Blocker")
        if robot < 0 or b1 < 0:
            raise RuntimeError("Scene is missing /PioneerP3DX or /B1")
        if pallet < 0 or blocker < 0:
            raise RuntimeError("Scene is missing /P2_Dynamic_Pallet or /P2_Temporary_Blocker")

        sim.setStringSignal("phase1ControlMode", "PID")
        sim.setStringSignal("phase1SlamAlgorithm", slam_algorithm)
        sim.startSimulation()

        rows: list[dict[str, float | int | str]] = []
        last_sample = -1000.0
        for _ in range(4600):
            phase1_export.sim_step(sim, sim_loop)
            t = float(sim.getSimulationTime())
            if t - last_sample >= 0.10:
                rows.append(sample_row(sim, robot, b1, pallet, blocker))
                last_sample = t
            completed = phase1_export.read_int_signal(sim, "phase1TaskComplete", 0) == 1
            charging = (
                phase1_export.read_int_signal(sim, "phase1Charging", 0) == 1
                or phase1_export.read_string_signal(sim, "phase1TaskState") == "CHARGING"
            )
            if completed and charging and t > 20:
                break
            if t > 170:
                break

        if not rows or float(rows[-1]["t"]) < float(sim.getSimulationTime()):
            rows.append(sample_row(sim, robot, b1, pallet, blocker))

        sim.stopSimulation()
        while sim.getSimulationState() != sim.simulation_stopped:
            sim_loop(None, 0)
    finally:
        sim_deinitialize()

    write_csv(rows, csv_path)
    return summarize(rows, csv_path, summary_json, slam_algorithm)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 2 unknown-map SLAM export.")
    parser.add_argument(
        "--slam-algorithm",
        choices=("KALMAN_LANDMARK", "GMAPPING_GRID", "HECTOR_GRID_MATCHING", "CARTOGRAPHER_SUBMAP"),
        default="KALMAN_LANDMARK",
        help="SLAM/map estimator mode requested through the CoppeliaSim signal.",
    )
    parser.add_argument(
        "--tag",
        default="",
        help="Optional output tag. Example: gmapping writes phase2_slam_unknown_gmapping.csv/json.",
    )
    args = parser.parse_args()

    if args.tag:
        csv_path = LOG_DIR / f"phase2_slam_unknown_{args.tag}.csv"
        summary_json = LOG_DIR / f"phase2_slam_unknown_{args.tag}_summary.json"
    else:
        csv_path = CSV_PATH
        summary_json = SUMMARY_JSON

    result = run(args.slam_algorithm, csv_path, summary_json)
    print(json.dumps(result, indent=2))
    return 0 if result["completed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
