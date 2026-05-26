"""Run Phase 1 Basic scene with each controller mode and export CSV/JSON.

The Lua controller reads ``phase1ControlMode`` before the simulation starts.
This script runs the same task sequence for P, PI, PID, LQR and NMPC, then
summarizes mission time, battery use, obstacle risk, localization error and
control smoothness.
"""

from __future__ import annotations

import csv
import json
import math
import os
import sys
from pathlib import Path
from statistics import fmean
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
COPPELIA_DIR = Path(r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu")
SCENE = ROOT / "actividad2" / "coppeliasim" / "Sim_T2_Phase1_Basic.ttt"
LOG_DIR = ROOT / "actividad2" / "coppeliasim" / "phase1_controller_logs"
SUMMARY_JSON = LOG_DIR / "phase1_controller_summary.json"
MODES = ("P", "PI", "PID", "LQR", "NMPC")

CSV_FIELDS = (
    "t",
    "mode",
    "task_id",
    "task_state",
    "motion_mode",
    "active_tool",
    "b1_station",
    "robot_x",
    "robot_y",
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
    "pose_error",
    "kalman_covariance",
    "control_v",
    "control_w",
    "control_tv",
)


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


def read_string_signal(sim, name: str, default: str = "") -> str:
    value = sim.getStringSignal(name)
    if value is None:
        return default
    return str(value)


def read_float_signal(sim, name: str, default: float = 0.0) -> float:
    value = sim.getFloatSignal(name)
    if value is None:
        return default
    return float(value)


def read_int_signal(sim, name: str, default: int = 0) -> int:
    value = sim.getInt32Signal(name)
    if value is None:
        return default
    return int(value)


def sim_step(sim, sim_loop) -> None:
    if sim.getSimulationState() == sim.simulation_stopped:
        return
    current = sim.getSimulationTime()
    for _ in range(80):
        sim_loop(None, 0)
        if current != sim.getSimulationTime() or sim.getSimulationState() == sim.simulation_stopped:
            break


def world_xy(sim, handle: int) -> tuple[float, float]:
    if handle < 0:
        return (math.nan, math.nan)
    try:
        p = sim.getObjectPosition(handle, -1)
    except Exception:
        return (math.nan, math.nan)
    return (float(p[0]), float(p[1]))


def sample_row(sim, mode: str, robot: int, b1: int) -> dict[str, float | int | str]:
    rx, ry = world_xy(sim, robot)
    bx, by = world_xy(sim, b1)
    return {
        "t": round(float(sim.getSimulationTime()), 4),
        "mode": mode,
        "task_id": read_string_signal(sim, "phase1TaskId", "UNKNOWN"),
        "task_state": read_string_signal(sim, "phase1TaskState", "UNKNOWN"),
        "motion_mode": read_string_signal(sim, "phase1MotionMode", "UNKNOWN"),
        "active_tool": read_string_signal(sim, "phase1ActiveTool", "NONE"),
        "b1_station": read_string_signal(sim, "phase1B1Station", "UNKNOWN"),
        "robot_x": round(rx, 5),
        "robot_y": round(ry, 5),
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
        "pose_error": round(read_float_signal(sim, "phase1PoseError", 0.0), 5),
        "kalman_covariance": round(read_float_signal(sim, "phase1KalmanCovariance", 0.0), 5),
        "control_v": round(read_float_signal(sim, "phase1ControlV", 0.0), 5),
        "control_w": round(read_float_signal(sim, "phase1ControlW", 0.0), 5),
        "control_tv": round(read_float_signal(sim, "phase1ControlTV", 0.0), 5),
    }


def write_csv(mode: str, rows: list[dict[str, float | int | str]]) -> Path:
    path = LOG_DIR / f"phase1_{mode}.csv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def positive(values: Iterable[float]) -> list[float]:
    return [v for v in values if v > 0]


def summarize_rows(mode: str, csv_path: Path, rows: list[dict[str, float | int | str]]) -> dict[str, object]:
    if not rows:
        return {"mode": mode, "csv": str(csv_path), "completed": False}

    path_length = 0.0
    active_motion = 0.0
    wait_time = 0.0
    manipulation_time = 0.0
    avoiding_time = 0.0
    prev = rows[0]
    for row in rows[1:]:
        dt = float(row["t"]) - float(prev["t"])
        dx = float(row["robot_x"]) - float(prev["robot_x"])
        dy = float(row["robot_y"]) - float(prev["robot_y"])
        if math.isfinite(dx) and math.isfinite(dy):
            path_length += math.hypot(dx, dy)
        prev_motion = str(prev["motion_mode"])
        if prev_motion in {"ROUTE", "AVOIDING"}:
            active_motion += dt
        if prev_motion == "WAIT_B1":
            wait_time += dt
        if prev_motion == "MANIPULATING":
            manipulation_time += dt
        if prev_motion == "AVOIDING":
            avoiding_time += dt
        prev = row

    min_obstacles = positive(float(row["min_obstacle"]) for row in rows)
    pose_errors = [float(row["pose_error"]) for row in rows]
    risk_values = [float(row["obstacle_risk"]) for row in rows]
    final = rows[-1]
    completed = int(final["task_complete"]) == 1 and int(final["completed_task_count"]) >= 3
    duration = float(final["t"])
    battery_start = float(rows[0]["battery"])
    battery_final = float(final["battery"])
    battery_used = battery_start - battery_final

    return {
        "mode": mode,
        "csv": str(csv_path),
        "completed": completed,
        "duration_s": round(duration, 3),
        "active_motion_s": round(active_motion, 3),
        "wait_b1_s": round(wait_time, 3),
        "manipulation_s": round(manipulation_time, 3),
        "avoiding_s": round(avoiding_time, 3),
        "path_length_m": round(path_length, 3),
        "battery_used_pct": round(battery_used, 3),
        "battery_final_pct": round(battery_final, 3),
        "min_obstacle_m": round(min(min_obstacles), 3) if min_obstacles else None,
        "max_obstacle_risk": round(max(risk_values), 3) if risk_values else None,
        "mean_pose_error_m": round(fmean(pose_errors), 4) if pose_errors else None,
        "max_pose_error_m": round(max(pose_errors), 4) if pose_errors else None,
        "control_total_variation": round(float(final["control_tv"]), 4),
        "final_task_state": str(final["task_state"]),
        "final_motion_mode": str(final["motion_mode"]),
        "samples": len(rows),
    }


def score_summaries(summaries: list[dict[str, object]]) -> None:
    metrics = {
        "active_motion_s": 0.28,
        "battery_used_pct": 0.18,
        "control_total_variation": 0.20,
        "max_obstacle_risk": 0.14,
        "mean_pose_error_m": 0.12,
        "duration_s": 0.08,
    }
    completed = [s for s in summaries if s.get("completed")]
    if not completed:
        for summary in summaries:
            summary["score"] = None
        return

    ranges: dict[str, tuple[float, float]] = {}
    for key in metrics:
        values = [float(s[key]) for s in completed if s.get(key) is not None]
        ranges[key] = (min(values), max(values))

    for summary in summaries:
        if not summary.get("completed"):
            summary["score"] = 999.0
            continue
        score = 0.0
        for key, weight in metrics.items():
            lo, hi = ranges[key]
            value = float(summary[key])
            normalized = 0.0 if abs(hi - lo) < 1e-9 else (value - lo) / (hi - lo)
            score += weight * normalized
        summary["score"] = round(score, 4)


def run_mode(sim, sim_loop, mode: str) -> dict[str, object]:
    if sim.loadScene(str(SCENE)) < 0:
        raise RuntimeError(f"Could not load {SCENE}")
    for _ in range(3):
        sim_loop(None, 0)

    robot = safe_get(sim, "/PioneerP3DX")
    b1 = safe_get(sim, "/B1")
    if robot < 0 or b1 < 0:
        raise RuntimeError("Scene is missing /PioneerP3DX or /B1")

    sim.setStringSignal("phase1ControlMode", mode)
    sim.startSimulation()

    rows: list[dict[str, float | int | str]] = []
    last_sample = -1000.0
    for _ in range(4200):
        sim_step(sim, sim_loop)
        t = float(sim.getSimulationTime())
        if t - last_sample >= 0.10:
            rows.append(sample_row(sim, mode, robot, b1))
            last_sample = t
        completed = read_int_signal(sim, "phase1TaskComplete", 0) == 1
        charging = read_int_signal(sim, "phase1Charging", 0) == 1 or read_string_signal(sim, "phase1TaskState") == "CHARGING"
        if completed and charging and t > 20:
            break
        if t > 170:
            break

    if not rows or float(rows[-1]["t"]) < float(sim.getSimulationTime()):
        rows.append(sample_row(sim, mode, robot, b1))

    sim.stopSimulation()
    while sim.getSimulationState() != sim.simulation_stopped:
        sim_loop(None, 0)

    csv_path = write_csv(mode, rows)
    return summarize_rows(mode, csv_path, rows)


def main() -> int:
    if not SCENE.exists():
        raise FileNotFoundError(SCENE)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    sim, sim_loop, sim_deinitialize = load_coppeliasim()
    try:
        summaries = [run_mode(sim, sim_loop, mode) for mode in MODES]
    finally:
        sim_deinitialize()

    score_summaries(summaries)
    best = min((s for s in summaries if s.get("completed")), key=lambda item: float(item["score"]), default=None)
    result = {
        "scene": str(SCENE),
        "modes": summaries,
        "best_mode": best["mode"] if best else None,
        "scoring": {
            "lower_is_better": [
                "active_motion_s",
                "battery_used_pct",
                "control_total_variation",
                "max_obstacle_risk",
                "mean_pose_error_m",
                "duration_s",
            ],
            "weights": {
                "active_motion_s": 0.28,
                "battery_used_pct": 0.18,
                "control_total_variation": 0.20,
                "max_obstacle_risk": 0.14,
                "mean_pose_error_m": 0.12,
                "duration_s": 0.08,
            },
        },
    }
    SUMMARY_JSON.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if best else 2


if __name__ == "__main__":
    raise SystemExit(main())
