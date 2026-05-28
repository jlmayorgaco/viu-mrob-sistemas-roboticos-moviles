"""Plot telemetry exported by run_phase1_slam_export.py."""

from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path
from statistics import fmean

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "actividad2" / "coppeliasim" / "phase1_slam_logs"
CSV_PATH = LOG_DIR / "phase1_slam_export.csv"
OVERVIEW_PNG = LOG_DIR / "phase1_slam_overview.png"
SIGNALS_PNG = LOG_DIR / "phase1_slam_signals.png"
ESTIMATOR_PNG = LOG_DIR / "phase1_slam_estimator_performance.png"
TIMELINE_PNG = LOG_DIR / "phase1_slam_task_timeline.png"
ANALYSIS_JSON = LOG_DIR / "phase1_slam_analysis.json"
ANALYSIS_MD = LOG_DIR / "phase1_slam_analysis.md"

STRING_COLUMNS = {
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
    "battery_mode",
    "slam_map",
    "grid_map",
}

LANDMARK_RE = re.compile(r"O(?P<id>\d+):(?P<x>-?\d+(?:\.\d+)?),(?P<y>-?\d+(?:\.\d+)?),s(?P<seen>\d+)")


def load_rows() -> list[dict[str, float | int | str]]:
    rows: list[dict[str, float | int | str]] = []
    with CSV_PATH.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            row: dict[str, float | int | str] = {}
            for key, value in raw.items():
                if key in STRING_COLUMNS:
                    row[key] = value
                elif key in {
                    "completed_task_count",
                    "task_complete",
                    "charging",
                    "slam_landmarks",
                    "slam_updates",
                    "slam_new_landmarks",
                    "grid_occupied_cells",
                    "grid_free_cells",
                    "grid_updates",
                    "cartographer_submaps",
                    "loop_closures",
                    "planner_wp_active",
                }:
                    row[key] = int(float(value))
                else:
                    row[key] = float(value)
            rows.append(row)
    return rows


def values(rows: list[dict[str, float | int | str]], key: str) -> list[float]:
    return [float(row[key]) for row in rows]


def strings(rows: list[dict[str, float | int | str]], key: str) -> list[str]:
    return [str(row[key]) for row in rows]


def finite(values_in: list[float]) -> list[float]:
    return [value for value in values_in if math.isfinite(value)]


def percentile(values_in: list[float], q: float) -> float:
    data = sorted(finite(values_in))
    if not data:
        return math.nan
    if len(data) == 1:
        return data[0]
    rank = (len(data) - 1) * q
    lo = math.floor(rank)
    hi = math.ceil(rank)
    if lo == hi:
        return data[lo]
    return data[lo] + (data[hi] - data[lo]) * (rank - lo)


def rmse(values_in: list[float]) -> float:
    data = finite(values_in)
    if not data:
        return math.nan
    return math.sqrt(fmean([value * value for value in data]))


def wrap_angle(angle: float) -> float:
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def parse_landmarks(slam_map: str) -> list[tuple[int, float, float, int]]:
    landmarks: list[tuple[int, float, float, int]] = []
    for match in LANDMARK_RE.finditer(slam_map):
        landmarks.append(
            (
                int(match.group("id")),
                float(match.group("x")),
                float(match.group("y")),
                int(match.group("seen")),
            )
        )
    return landmarks


def decimated_waypoints(rows: list[dict[str, float | int | str]]) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    last: tuple[float, float] | None = None
    for row in rows:
        if int(row["planner_wp_active"]) != 1:
            continue
        point = (float(row["planner_wp_x"]), float(row["planner_wp_y"]))
        if not math.isfinite(point[0]) or not math.isfinite(point[1]):
            continue
        if last is None or math.hypot(point[0] - last[0], point[1] - last[1]) > 0.10:
            points.append(point)
            last = point
    return points


def intervals(rows: list[dict[str, float | int | str]], key: str, value: str) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    start: float | None = None
    last_t = 0.0
    for row in rows:
        t = float(row["t"])
        if row[key] == value and start is None:
            start = t
        elif row[key] != value and start is not None:
            out.append((start, last_t))
            start = None
        last_t = t
    if start is not None:
        out.append((start, last_t))
    return out


def mode_durations(rows: list[dict[str, float | int | str]], key: str) -> dict[str, float]:
    durations: dict[str, float] = {}
    for prev, row in zip(rows, rows[1:]):
        dt = max(0.0, float(row["t"]) - float(prev["t"]))
        mode = str(prev[key])
        durations[mode] = durations.get(mode, 0.0) + dt
    return {key: round(value, 3) for key, value in sorted(durations.items())}


def grouped_pose_error(rows: list[dict[str, float | int | str]], key: str) -> dict[str, dict[str, float | int]]:
    groups: dict[str, list[float]] = {}
    for row in rows:
        group = str(row[key])
        groups.setdefault(group, []).append(float(row["pose_error"]))
    return {
        group: {
            "samples": len(vals),
            "mean_m": round(fmean(vals), 5),
            "p95_m": round(percentile(vals, 0.95), 5),
            "max_m": round(max(vals), 5),
        }
        for group, vals in sorted(groups.items())
        if vals
    }


def task_segments(rows: list[dict[str, float | int | str]]) -> list[tuple[str, float, float]]:
    segments: list[tuple[str, float, float]] = []
    if not rows:
        return segments
    current = str(rows[0]["task_state"])
    start = float(rows[0]["t"])
    previous_t = start
    for row in rows[1:]:
        t = float(row["t"])
        state = str(row["task_state"])
        if state != current:
            segments.append((current, start, previous_t))
            current = state
            start = t
        previous_t = t
    segments.append((current, start, previous_t))
    return segments


def first_landmark_times(rows: list[dict[str, float | int | str]]) -> list[tuple[int, float]]:
    first_seen: list[tuple[int, float]] = []
    previous = -1
    for row in rows:
        count = int(row["slam_landmarks"])
        if count > previous:
            for landmark_id in range(max(previous + 1, 1), count + 1):
                first_seen.append((landmark_id, float(row["t"])))
            previous = count
    return first_seen


def compute_analysis(rows: list[dict[str, float | int | str]], landmarks: list[tuple[int, float, float, int]]) -> dict[str, object]:
    t = values(rows, "t")
    ex = [float(row["est_x"]) - float(row["robot_x"]) for row in rows]
    ey = [float(row["est_y"]) - float(row["robot_y"]) for row in rows]
    eth = [wrap_angle(float(row["est_theta"]) - float(row["robot_theta"])) for row in rows]
    position_error = [math.hypot(dx, dy) for dx, dy in zip(ex, ey)]
    pose_error = values(rows, "pose_error")
    covariance = values(rows, "kalman_covariance")
    min_obstacles = [value for value in values(rows, "min_obstacle") if value > 0]
    final = rows[-1]
    duration = float(final["t"]) - float(rows[0]["t"])
    landmark_times = first_landmark_times(rows)

    return {
        "duration_s": round(duration, 3),
        "samples": len(rows),
        "estimator": {
            "rmse_x_m": round(rmse(ex), 5),
            "rmse_y_m": round(rmse(ey), 5),
            "rmse_position_m": round(rmse(position_error), 5),
            "mean_position_error_m": round(fmean(position_error), 5),
            "median_position_error_m": round(percentile(position_error, 0.50), 5),
            "p95_position_error_m": round(percentile(position_error, 0.95), 5),
            "max_position_error_m": round(max(position_error), 5),
            "rmse_theta_rad": round(rmse(eth), 5),
            "mean_reported_pose_error_m": round(fmean(pose_error), 5),
            "max_reported_pose_error_m": round(max(pose_error), 5),
            "mean_covariance": round(fmean(covariance), 5),
            "max_covariance": round(max(covariance), 5),
        },
        "mapping": {
            "landmarks_final": int(final["slam_landmarks"]),
            "landmarks_from_final_map": len(landmarks),
            "slam_updates": int(final["slam_updates"]),
            "updates_per_second": round(int(final["slam_updates"]) / max(duration, 1e-9), 3),
            "updates_per_landmark": round(int(final["slam_updates"]) / max(int(final["slam_landmarks"]), 1), 2),
            "first_landmark_times_s": [(idx, round(time, 3)) for idx, time in landmark_times],
            "landmark_seen_counts": {f"O{idx}": seen for idx, _, _, seen in landmarks},
        },
        "planning_and_safety": {
            "planner_mode_durations_s": mode_durations(rows, "planner_mode"),
            "motion_mode_durations_s": mode_durations(rows, "motion_mode"),
            "min_obstacle_m": round(min(min_obstacles), 5) if min_obstacles else None,
            "max_obstacle_risk": round(max(values(rows, "obstacle_risk")), 5),
            "battery_start_pct": round(float(rows[0]["battery"]), 5),
            "battery_final_pct": round(float(final["battery"]), 5),
            "battery_used_pct": round(float(rows[0]["battery"]) - float(final["battery"]), 5),
            "completed_tasks": int(final["completed_task_count"]),
            "final_task_state": str(final["task_state"]),
        },
        "pose_error_by_motion_mode": grouped_pose_error(rows, "motion_mode"),
        "pose_error_by_planner_mode": grouped_pose_error(rows, "planner_mode"),
    }


def write_analysis_markdown(analysis: dict[str, object]) -> None:
    est = analysis["estimator"]
    mapping = analysis["mapping"]
    safety = analysis["planning_and_safety"]
    motion_durations = safety["motion_mode_durations_s"]
    planner_durations = safety["planner_mode_durations_s"]

    lines = [
        "# Análisis Phase 1 Basic - estimación, SLAM y planificación",
        "",
        "## Qué hace el estimador",
        "",
        "El estimador implementa un ciclo clásico de predicción y corrección. Primero predice la pose del Pioneer con el modelo cinemático diferencial y la odometría de ruedas. Luego corrige esa pose con una medición simulada con ruido mediante una ganancia tipo Kalman. Con la pose estimada, cada lectura de proximidad se transforma de coordenadas locales del sensor a coordenadas globales del almacén.",
        "",
        "Para el mapa se usa asociación por cercanía: si una detección cae cerca de una landmark existente, esa landmark se actualiza con un filtro Kalman escalar; si cae fuera del radio de asociación, se crea una nueva landmark. El resultado es un mapa disperso de obstáculos adecuado para navegación local en esta celda.",
        "",
        "## Desempeño numérico",
        "",
        f"- RMSE posición: {est['rmse_position_m']} m",
        f"- Error medio de posición: {est['mean_position_error_m']} m",
        f"- Error P95 de posición: {est['p95_position_error_m']} m",
        f"- Error máximo de posición: {est['max_position_error_m']} m",
        f"- RMSE orientación: {est['rmse_theta_rad']} rad",
        f"- Covarianza media publicada: {est['mean_covariance']}",
        "",
        "## Mapeo y planificación",
        "",
        f"- Landmarks finales: {mapping['landmarks_final']}",
        f"- Actualizaciones SLAM/Kalman: {mapping['slam_updates']}",
        f"- Frecuencia media de actualización: {mapping['updates_per_second']} actualizaciones/s",
        f"- Actualizaciones por landmark: {mapping['updates_per_landmark']}",
        f"- Duración por modo de planificador: {planner_durations}",
        f"- Duración por modo de movimiento: {motion_durations}",
        "",
        "## Seguridad operacional",
        "",
        f"- Distancia mínima positiva a obstáculo: {safety['min_obstacle_m']} m",
        f"- Riesgo máximo de obstáculo: {safety['max_obstacle_risk']}",
        f"- Batería inicial/final: {safety['battery_start_pct']}% -> {safety['battery_final_pct']}%",
        f"- Tareas completadas: {safety['completed_tasks']}",
        f"- Estado final: {safety['final_task_state']}",
        "",
        "## Interpretación para la guía",
        "",
        "El comportamiento corresponde a una implementación clásica dentro de CoppeliaSim: EKF para localización de pose, filtro Kalman para landmarks de obstáculos, asociación por distancia y planificación por punto intermedio cuando el mapa detecta bloqueo en la ruta directa.",
        "",
    ]
    ANALYSIS_MD.write_text("\n".join(lines), encoding="utf-8")


def plot_estimator_performance(rows: list[dict[str, float | int | str]]) -> None:
    t = values(rows, "t")
    ex = [float(row["est_x"]) - float(row["robot_x"]) for row in rows]
    ey = [float(row["est_y"]) - float(row["robot_y"]) for row in rows]
    eth = [wrap_angle(float(row["est_theta"]) - float(row["robot_theta"])) for row in rows]
    position_error = [math.hypot(dx, dy) for dx, dy in zip(ex, ey)]

    fig, axes = plt.subplots(2, 2, figsize=(13.8, 8.2))
    fig.suptitle("Phase 1 Basic - desempeño del estimador", fontsize=15, fontweight="bold")

    ax = axes[0, 0]
    ax.plot(t, ex, color="#1f5fa8", linewidth=1.4, label="error x")
    ax.plot(t, ey, color="#c9472c", linewidth=1.4, label="error y")
    ax.plot(t, position_error, color="#10a37f", linewidth=1.7, label="error posición")
    ax.set_title("Error de posición")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("m")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")

    ax = axes[0, 1]
    ax.plot(t, eth, color="#7e4aa8", linewidth=1.5)
    ax.set_title("Error angular")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("rad")
    ax.grid(True, alpha=0.25)

    ax = axes[1, 0]
    ax.hist(position_error, bins=28, color="#10a37f", alpha=0.78, edgecolor="white")
    ax.axvline(percentile(position_error, 0.95), color="#c9472c", linewidth=1.8, label="P95")
    ax.axvline(fmean(position_error), color="#111111", linewidth=1.5, linestyle="--", label="media")
    ax.set_title("Distribución del error")
    ax.set_xlabel("error posicion [m]")
    ax.set_ylabel("muestras")
    ax.grid(True, alpha=0.20)
    ax.legend(loc="best")

    ax = axes[1, 1]
    ax.scatter(values(rows, "robot_x"), values(rows, "est_x"), s=10, alpha=0.55, color="#1f5fa8", label="x")
    ax.scatter(values(rows, "robot_y"), values(rows, "est_y"), s=10, alpha=0.55, color="#c9472c", label="y")
    min_axis = min(min(values(rows, "robot_x")), min(values(rows, "robot_y")), min(values(rows, "est_x")), min(values(rows, "est_y")))
    max_axis = max(max(values(rows, "robot_x")), max(values(rows, "robot_y")), max(values(rows, "est_x")), max(values(rows, "est_y")))
    ax.plot([min_axis, max_axis], [min_axis, max_axis], color="#111111", linewidth=1.2, linestyle="--")
    ax.set_title("Real vs estimado")
    ax.set_xlabel("real [m]")
    ax.set_ylabel("estimado [m]")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(ESTIMATOR_PNG, dpi=180)


def plot_task_timeline(rows: list[dict[str, float | int | str]]) -> None:
    segments = task_segments(rows)
    task_names = list(dict.fromkeys(state for state, _, _ in segments))
    task_index = {state: i for i, state in enumerate(task_names)}
    colors = plt.cm.tab20([i % 20 for i in range(len(task_names))])

    fig, axes = plt.subplots(3, 1, figsize=(13.8, 8.2), sharex=True)
    fig.suptitle("Phase 1 Basic - linea temporal de tareas y decisiones", fontsize=15, fontweight="bold")

    ax = axes[0]
    for state, start, end in segments:
        ax.barh(task_index[state], max(end - start, 0.05), left=start, height=0.72, color=colors[task_index[state]], edgecolor="white")
    ax.set_yticks(range(len(task_names)), task_names, fontsize=7)
    ax.set_title("Estados de tarea")
    ax.grid(True, axis="x", alpha=0.25)

    ax = axes[1]
    ax.step(values(rows, "t"), values(rows, "slam_landmarks"), where="post", color="#c9472c", linewidth=1.7, label="landmarks")
    ax2 = ax.twinx()
    ax2.step(values(rows, "t"), values(rows, "slam_updates"), where="post", color="#7e4aa8", linewidth=1.4, label="updates")
    ax.set_title("Crecimiento del mapa")
    ax.set_ylabel("landmarks")
    ax2.set_ylabel("updates")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")

    ax = axes[2]
    ax.plot(values(rows, "t"), values(rows, "distance_to_target"), color="#1f5fa8", linewidth=1.5, label="distancia al objetivo")
    ax.plot(values(rows, "t"), values(rows, "min_obstacle"), color="#c9472c", linewidth=1.2, label="distancia obstaculo")
    ax.set_title("Distancias de navegacion")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("m")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(TIMELINE_PNG, dpi=180)


def main() -> int:
    if not CSV_PATH.exists():
        raise FileNotFoundError(CSV_PATH)

    rows = load_rows()
    final_map = str(rows[-1]["slam_map"])
    landmarks = parse_landmarks(final_map)
    waypoints = decimated_waypoints(rows)
    slam_windows = intervals(rows, "planner_mode", "SLAM_WAYPOINT")
    avoid_windows = intervals(rows, "motion_mode", "AVOIDING")
    analysis = compute_analysis(rows, landmarks)

    fig, axes = plt.subplots(2, 2, figsize=(13.8, 8.2))
    fig.suptitle("Phase 1 Basic - EKF/SLAM obstacle mapping and path planning", fontsize=15, fontweight="bold")

    ax = axes[0, 0]
    ax.plot(values(rows, "robot_x"), values(rows, "robot_y"), color="#1f5fa8", linewidth=2.0, label="R1 real")
    ax.plot(values(rows, "est_x"), values(rows, "est_y"), color="#10a37f", linewidth=1.4, linestyle="--", label="R1 estimado")
    ax.plot(values(rows, "b1_x"), values(rows, "b1_y"), color="#111111", linewidth=2.0, label="B1")
    if waypoints:
        ax.scatter([p[0] for p in waypoints], [p[1] for p in waypoints], s=34, marker="D", color="#d19a21", label="waypoints SLAM")
    if landmarks:
        ax.scatter([p[1] for p in landmarks], [p[2] for p in landmarks], s=54, marker="x", color="#c9472c", label="landmarks obstaculo")
        for idx, x, y, seen in landmarks:
            ax.text(x + 0.03, y + 0.03, f"O{idx}", fontsize=7.5, color="#8a2d1d")
    ax.set_title("Trayectoria, estimacion y mapa")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.axis("equal")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")

    ax = axes[0, 1]
    for start, end in slam_windows:
        ax.axvspan(start, end, color="#d19a21", alpha=0.12)
    ax.plot(values(rows, "t"), values(rows, "pose_error"), color="#10a37f", linewidth=1.8, label="error pose")
    ax.plot(values(rows, "t"), values(rows, "kalman_covariance"), color="#6b7280", linewidth=1.3, label="covarianza")
    ax.set_title("Estimacion Kalman")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("m / cov")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")

    ax = axes[1, 0]
    for start, end in avoid_windows:
        ax.axvspan(start, end, color="#c9472c", alpha=0.10)
    ax.plot(values(rows, "t"), values(rows, "min_obstacle"), color="#1f5fa8", linewidth=1.6, label="distancia minima")
    ax2 = ax.twinx()
    ax2.plot(values(rows, "t"), values(rows, "obstacle_risk"), color="#c9472c", linewidth=1.4, label="riesgo")
    ax.set_title("Obstaculos detectados")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("distancia [m]")
    ax2.set_ylabel("riesgo [0-1]")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")

    ax = axes[1, 1]
    ax.step(values(rows, "t"), values(rows, "completed_task_count"), where="post", color="#217a3f", linewidth=2.0, label="tareas")
    ax2 = ax.twinx()
    ax2.plot(values(rows, "t"), values(rows, "slam_landmarks"), color="#c9472c", linewidth=1.7, label="landmarks")
    ax.set_title("Progreso y crecimiento del mapa")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("tareas completadas")
    ax2.set_ylabel("landmarks")
    ax.set_ylim(-0.05, 3.25)
    ax.grid(True, alpha=0.25)
    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")

    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(OVERVIEW_PNG, dpi=180)

    fig2, axes2 = plt.subplots(2, 2, figsize=(13.8, 8.0))
    fig2.suptitle("Phase 1 Basic - senales para el reporte", fontsize=15, fontweight="bold")

    ax = axes2[0, 0]
    ax.plot(values(rows, "t"), values(rows, "battery"), color="#217a3f", linewidth=1.8)
    ax.set_title("Bateria")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("[%]")
    ax.grid(True, alpha=0.25)

    ax = axes2[0, 1]
    ax.plot(values(rows, "t"), values(rows, "control_v"), color="#1f5fa8", linewidth=1.6, label="v")
    ax.plot(values(rows, "t"), values(rows, "control_w"), color="#d19a21", linewidth=1.3, label="w")
    ax.set_title("Comandos de control")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("m/s, rad/s")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")

    ax = axes2[1, 0]
    ax.plot(values(rows, "t"), values(rows, "slam_updates"), color="#7e4aa8", linewidth=1.7)
    ax.set_title("Actualizaciones del mapa")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("updates")
    ax.grid(True, alpha=0.25)

    ax = axes2[1, 1]
    planner_codes = {"DIRECT": 0, "SLAM_WAYPOINT": 1, "DIRECT_AFTER_WAYPOINT": 2}
    motion_codes = {"ROUTE": 0, "AVOIDING": 1, "MANIPULATING": 2, "WAIT_B1": 3, "ARRIVED_TARGET": 4}
    ax.step(values(rows, "t"), [planner_codes.get(str(row["planner_mode"]), -1) for row in rows], where="post", color="#d19a21", linewidth=1.7, label="planner")
    ax.step(values(rows, "t"), [motion_codes.get(str(row["motion_mode"]), -1) for row in rows], where="post", color="#1f5fa8", linewidth=1.3, label="movimiento")
    ax.set_title("Modos discretos")
    ax.set_xlabel("t [s]")
    ax.set_yticks([0, 1, 2, 3, 4], ["direct/route", "slam/avoid", "after/manip", "wait", "arrived"])
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")

    fig2.tight_layout(rect=(0, 0, 1, 0.95))
    fig2.savefig(SIGNALS_PNG, dpi=180)

    plot_estimator_performance(rows)
    plot_task_timeline(rows)
    ANALYSIS_JSON.write_text(json.dumps(analysis, indent=2), encoding="utf-8")
    write_analysis_markdown(analysis)

    print(
        {
            "plots": [str(OVERVIEW_PNG), str(SIGNALS_PNG), str(ESTIMATOR_PNG), str(TIMELINE_PNG)],
            "csv": str(CSV_PATH),
            "analysis": [str(ANALYSIS_JSON), str(ANALYSIS_MD)],
            "rows": len(rows),
            "landmarks": len(landmarks),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
