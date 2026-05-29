"""Run Sim_T2_Phase1_Basic.ttt and export EKF/SLAM planning data.

Outputs:
- phase1_slam_export.csv: time-series telemetry.
- phase1_slam_summary.json: compact metrics for the report.
"""

from __future__ import annotations

import csv
import argparse
import json
import math
from pathlib import Path
from statistics import fmean

from scene_common import (
    load_coppeliasim,
    positive,
    read_float_signal,
    read_int_signal,
    read_string_signal,
    safe_get,
    sim_step,
    world_pose,
)


ROOT = Path(__file__).resolve().parents[2]
SCENE = ROOT / "actividad2" / "coppeliasim" / "Sim_T2_Phase1_Basic.ttt"
LOG_DIR = ROOT / "actividad2" / "coppeliasim" / "phase1_slam_logs"
CSV_PATH = LOG_DIR / "phase1_slam_export.csv"
SUMMARY_JSON = LOG_DIR / "phase1_slam_summary.json"

CSV_FIELDS = (
    "t",
    "control_mode",
    "slam_algorithm",
    "localization_mode",
    "slam_feature_type",
    "task_id",
    "task_state",
    "motion_mode",
    "planner_mode",
    "active_tool",
    "b1_station",
    "robot_x",
    "robot_y",
    "robot_theta",
    "est_x",
    "est_y",
    "est_theta",
    "pose_error",
    "kalman_covariance",
    "b1_x",
    "b1_y",
    "distance_to_target",
    "min_obstacle",
    "obstacle_risk",
    "battery",
    "battery_mode",
    "completed_task_count",
    "task_complete",
    "charging",
    "slam_feature_count",
    "slam_landmarks",
    "slam_updates",
    "slam_new_landmarks",
    "grid_occupied_cells",
    "grid_free_cells",
    "grid_updates",
    "grid_entropy",
    "scan_match_score",
    "cartographer_submaps",
    "loop_closures",
    "planner_wp_x",
    "planner_wp_y",
    "planner_wp_active",
    "planner_recovery_count",
    "control_v",
    "control_w",
    "control_tv",
    "slam_map",
    "grid_map",
)


def parse_triplet(text: str, default: tuple[float, float, float]) -> tuple[float, float, float]:
    try:
        parts = [float(part) for part in text.split(",")]
    except ValueError:
        return default
    if len(parts) < 3:
        return default
    return (parts[0], parts[1], parts[2])


def sample_row(sim, robot: int, b1: int) -> dict[str, float | int | str]:
    rx, ry, rtheta = world_pose(sim, robot)
    bx, by, _ = world_pose(sim, b1)
    est = parse_triplet(read_string_signal(sim, "phase1EstimatedPose", "nan,nan,nan"), (math.nan, math.nan, math.nan))
    waypoint = parse_triplet(read_string_signal(sim, "phase1PlannerWaypoint", "nan,nan,0"), (math.nan, math.nan, 0.0))
    slam_algorithm = read_string_signal(sim, "phase1SlamAlgorithmActive", "KALMAN_LANDMARK")
    slam_map = read_string_signal(sim, "phase1SlamMap", "")
    grid_map = read_string_signal(sim, "phase1GridMap", "")
    cartographer_mode = slam_algorithm == "CARTOGRAPHER_SUBMAP"

    return {
        "t": round(float(sim.getSimulationTime()), 4),
        "control_mode": read_string_signal(sim, "phase1ControlModeActive", "PID"),
        "slam_algorithm": slam_algorithm,
        "localization_mode": read_string_signal(sim, "phase1LocalizationMode", "UNKNOWN"),
        "slam_feature_type": read_string_signal(sim, "phase1SlamFeatureType", "landmarks"),
        "task_id": read_string_signal(sim, "phase1TaskId", "UNKNOWN"),
        "task_state": read_string_signal(sim, "phase1TaskState", "UNKNOWN"),
        "motion_mode": read_string_signal(sim, "phase1MotionMode", "UNKNOWN"),
        "planner_mode": read_string_signal(sim, "phase1PlannerMode", "UNKNOWN"),
        "active_tool": read_string_signal(sim, "phase1ActiveTool", "NONE"),
        "b1_station": read_string_signal(sim, "phase1B1Station", "UNKNOWN"),
        "robot_x": round(rx, 5),
        "robot_y": round(ry, 5),
        "robot_theta": round(rtheta, 5),
        "est_x": round(est[0], 5),
        "est_y": round(est[1], 5),
        "est_theta": round(est[2], 5),
        "pose_error": round(read_float_signal(sim, "phase1PoseError", 0.0), 5),
        "kalman_covariance": round(read_float_signal(sim, "phase1KalmanCovariance", 0.0), 5),
        "b1_x": round(bx, 5),
        "b1_y": round(by, 5),
        "distance_to_target": round(read_float_signal(sim, "phase1DistanceToTarget", -1.0), 5),
        "min_obstacle": round(read_float_signal(sim, "phase1MinObstacleDistance", -1.0), 5),
        "obstacle_risk": round(read_float_signal(sim, "phase1ObstacleRisk", 0.0), 5),
        "battery": round(read_float_signal(sim, "phase1BatteryLevel", -1.0), 5),
        "battery_mode": read_string_signal(sim, "phase1BatteryMode", "UNKNOWN"),
        "completed_task_count": read_int_signal(sim, "phase1CompletedTaskCount", 0),
        "task_complete": read_int_signal(sim, "phase1TaskComplete", 0),
        "charging": read_int_signal(sim, "phase1Charging", 0),
        "slam_feature_count": read_int_signal(sim, "phase1SlamFeatureCount", 0),
        "slam_landmarks": read_int_signal(sim, "phase1SlamLandmarkCount", 0),
        "slam_updates": read_int_signal(sim, "phase1SlamUpdates", 0),
        "slam_new_landmarks": read_int_signal(sim, "phase1SlamNewLandmarks", 0),
        "grid_occupied_cells": read_int_signal(sim, "phase1GridOccupiedCells", 0),
        "grid_free_cells": read_int_signal(sim, "phase1GridFreeCells", 0),
        "grid_updates": read_int_signal(sim, "phase1GridUpdates", 0),
        "grid_entropy": round(read_float_signal(sim, "phase1GridEntropy", 0.0), 5),
        "scan_match_score": round(read_float_signal(sim, "phase1ScanMatchScore", 0.0), 5),
        "cartographer_submaps": read_int_signal(sim, "phase1CartographerSubmaps", 0) if cartographer_mode else 0,
        "loop_closures": read_int_signal(sim, "phase1LoopClosures", 0) if cartographer_mode else 0,
        "planner_wp_x": round(waypoint[0], 5),
        "planner_wp_y": round(waypoint[1], 5),
        "planner_wp_active": int(round(waypoint[2])),
        "planner_recovery_count": read_int_signal(sim, "phase1PlannerRecoveryCount", 0),
        "control_v": round(read_float_signal(sim, "phase1ControlV", 0.0), 5),
        "control_w": round(read_float_signal(sim, "phase1ControlW", 0.0), 5),
        "control_tv": round(read_float_signal(sim, "phase1ControlTV", 0.0), 5),
        "slam_map": slam_map,
        "grid_map": grid_map,
    }


def write_csv(rows: list[dict[str, float | int | str]], csv_path: Path = CSV_PATH) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def summarize(
    rows: list[dict[str, float | int | str]],
    csv_path: Path = CSV_PATH,
    summary_json: Path = SUMMARY_JSON,
    requested_algorithm: str = "KALMAN_LANDMARK",
) -> dict[str, object]:
    path_length = 0.0
    active_motion_s = 0.0
    avoiding_s = 0.0
    slam_waypoint_s = 0.0
    wait_b1_s = 0.0
    prev = rows[0]

    for row in rows[1:]:
        dt = float(row["t"]) - float(prev["t"])
        dx = float(row["robot_x"]) - float(prev["robot_x"])
        dy = float(row["robot_y"]) - float(prev["robot_y"])
        if math.isfinite(dx) and math.isfinite(dy):
            path_length += math.hypot(dx, dy)
        if str(prev["motion_mode"]) in {"ROUTE", "AVOIDING", "SLAM_PATH"}:
            active_motion_s += dt
        if str(prev["motion_mode"]) == "AVOIDING":
            avoiding_s += dt
        if str(prev["planner_mode"]) == "SLAM_WAYPOINT":
            slam_waypoint_s += dt
        if str(prev["motion_mode"]) == "WAIT_B1":
            wait_b1_s += dt
        prev = row

    final = rows[-1]
    pose_errors = [float(row["pose_error"]) for row in rows if math.isfinite(float(row["pose_error"]))]
    risks = [float(row["obstacle_risk"]) for row in rows if math.isfinite(float(row["obstacle_risk"]))]
    min_obstacles = positive(float(row["min_obstacle"]) for row in rows)
    planner_modes = sorted({str(row["planner_mode"]) for row in rows})
    motion_modes = sorted({str(row["motion_mode"]) for row in rows})
    task_states = sorted({str(row["task_state"]) for row in rows})

    result = {
        "scene": str(SCENE),
        "csv": str(csv_path),
        "requested_slam_algorithm": requested_algorithm,
        "slam_algorithm": str(final["slam_algorithm"]),
        "localization_mode": str(final["localization_mode"]),
        "completed": int(final["task_complete"]) == 1 and int(final["completed_task_count"]) >= 4,
        "duration_s": round(float(final["t"]), 3),
        "samples": len(rows),
        "path_length_m": round(path_length, 3),
        "active_motion_s": round(active_motion_s, 3),
        "avoiding_s": round(avoiding_s, 3),
        "slam_waypoint_s": round(slam_waypoint_s, 3),
        "wait_b1_s": round(wait_b1_s, 3),
        "battery_start_pct": round(float(rows[0]["battery"]), 3),
        "battery_final_pct": round(float(final["battery"]), 3),
        "battery_used_pct": round(float(rows[0]["battery"]) - float(final["battery"]), 3),
        "min_obstacle_m": round(min(min_obstacles), 3) if min_obstacles else None,
        "max_obstacle_risk": round(max(risks), 3) if risks else None,
        "mean_pose_error_m": round(fmean(pose_errors), 4) if pose_errors else None,
        "max_pose_error_m": round(max(pose_errors), 4) if pose_errors else None,
        "slam_landmarks_final": int(final["slam_landmarks"]),
        "slam_landmarks_max": max(int(row["slam_landmarks"]) for row in rows),
        "slam_updates": int(final["slam_updates"]),
        "grid_occupied_cells_final": int(final["grid_occupied_cells"]),
        "grid_free_cells_final": int(final["grid_free_cells"]),
        "grid_updates": int(final["grid_updates"]),
        "grid_entropy_final": round(float(final["grid_entropy"]), 5),
        "scan_match_score_final": round(float(final["scan_match_score"]), 5),
        "cartographer_submaps_final": int(final["cartographer_submaps"]),
        "loop_closures_final": int(final["loop_closures"]),
        "planner_recovery_count": int(final["planner_recovery_count"]),
        "planner_modes_seen": planner_modes,
        "motion_modes_seen": motion_modes,
        "task_states_seen": task_states,
        "final_task_state": str(final["task_state"]),
        "final_motion_mode": str(final["motion_mode"]),
        "final_slam_map": str(final["slam_map"]),
        "final_grid_map": str(final["grid_map"]),
    }
    summary_json.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def run(
    slam_algorithm: str = "KALMAN_LANDMARK",
    csv_path: Path = CSV_PATH,
    summary_json: Path = SUMMARY_JSON,
) -> dict[str, object]:
    if not SCENE.exists():
        raise FileNotFoundError(SCENE)

    sim, sim_loop, sim_deinitialize = load_coppeliasim()
    try:
        if sim.loadScene(str(SCENE)) < 0:
            raise RuntimeError(f"Could not load {SCENE}")
        for _ in range(3):
            sim_loop(None, 0)

        robot = safe_get(sim, "/PioneerP3DX")
        b1 = safe_get(sim, "/B1")
        if robot < 0 or b1 < 0:
            raise RuntimeError("Scene is missing /PioneerP3DX or /B1")

        sim.setStringSignal("phase1ControlMode", "PID")
        sim.setStringSignal("phase1SlamAlgorithm", slam_algorithm)
        sim.startSimulation()

        rows: list[dict[str, float | int | str]] = []
        last_sample = -1000.0
        for _ in range(4500):
            sim_step(sim, sim_loop)
            t = float(sim.getSimulationTime())
            if t - last_sample >= 0.10:
                rows.append(sample_row(sim, robot, b1))
                last_sample = t
            completed = read_int_signal(sim, "phase1TaskComplete", 0) == 1
            charging = read_int_signal(sim, "phase1Charging", 0) == 1 or read_string_signal(sim, "phase1TaskState") == "CHARGING"
            if completed and charging and t > 20:
                break
            if t > 170:
                break

        if not rows or float(rows[-1]["t"]) < float(sim.getSimulationTime()):
            rows.append(sample_row(sim, robot, b1))

        sim.stopSimulation()
        while sim.getSimulationState() != sim.simulation_stopped:
            sim_loop(None, 0)
    finally:
        sim_deinitialize()

    write_csv(rows, csv_path)
    return summarize(rows, csv_path, summary_json, slam_algorithm)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 1 Basic SLAM export.")
    parser.add_argument(
        "--slam-algorithm",
        choices=("KALMAN_LANDMARK", "GMAPPING_GRID", "HECTOR_GRID_MATCHING", "CARTOGRAPHER_SUBMAP"),
        default="KALMAN_LANDMARK",
        help="SLAM/map estimator mode requested through the CoppeliaSim signal.",
    )
    parser.add_argument(
        "--tag",
        default="",
        help="Optional output tag. Example: gmapping writes phase1_slam_gmapping.csv/json.",
    )
    args = parser.parse_args()

    if args.tag:
        csv_path = LOG_DIR / f"phase1_slam_{args.tag}.csv"
        summary_json = LOG_DIR / f"phase1_slam_{args.tag}_summary.json"
    else:
        csv_path = CSV_PATH
        summary_json = SUMMARY_JSON

    result = run(args.slam_algorithm, csv_path, summary_json)
    print(json.dumps(result, indent=2))
    return 0 if result["completed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
