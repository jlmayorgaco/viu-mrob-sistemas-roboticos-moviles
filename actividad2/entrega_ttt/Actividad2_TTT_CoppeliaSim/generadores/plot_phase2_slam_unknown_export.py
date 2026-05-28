"""Plot telemetry exported by run_phase2_slam_unknown_export.py."""

from __future__ import annotations

import csv
import json
import math
import re
from pathlib import Path
from statistics import fmean

import matplotlib.patches as patches
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "actividad2" / "coppeliasim" / "phase2_slam_logs"
CSV_PATH = LOG_DIR / "phase2_slam_unknown_export.csv"
SUMMARY_JSON = LOG_DIR / "phase2_slam_unknown_summary.json"
OVERVIEW_PNG = LOG_DIR / "phase2_slam_unknown_overview.png"
SNAPSHOTS_PNG = LOG_DIR / "phase2_slam_mapping_snapshots.png"
SIGNALS_PNG = LOG_DIR / "phase2_slam_unknown_signals.png"
ANALYSIS_JSON = LOG_DIR / "phase2_slam_unknown_analysis.json"
ANALYSIS_MD = LOG_DIR / "phase2_slam_unknown_analysis.md"

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
    "phase2_state",
    "phase2_scenario",
    "phase2_compliance",
    "phase2_motion_model",
    "phase2_moved_objects",
}

INT_COLUMNS = {
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
    "cartographer_submaps",
    "loop_closures",
    "planner_wp_active",
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
    "planner_recovery_count",
}

LANDMARK_RE = re.compile(r"O(?P<id>\d+):(?P<x>-?\d+(?:\.\d+)?),(?P<y>-?\d+(?:\.\d+)?),s(?P<seen>\d+)")

PHASE2_STATIC_OBSTACLES = (
    (-2.28, -0.48),
    (2.22, 0.74),
    (-0.12, 2.04),
)
MAP_MATCH_RADIUS_M = 0.55

UNKNOWN_ZONES = [
    ("Unknown north", (-0.55, 1.26), (1.80, 1.15)),
    ("Unknown center", (-0.10, -0.12), (2.30, 1.30)),
]

FRONTIERS = [
    ("F1", (1.78, 1.38)),
    ("F2", (0.08, 0.20)),
    ("F3", (-2.22, 0.42)),
    ("F4", (1.88, -0.52)),
    ("F5", (-0.42, -1.42)),
    ("F6", (-0.66, 1.62)),
]

STATIC_UNKNOWN_OBSTACLES = [
    ("Crate A", "rect", (-2.28, -0.48), (0.30, 0.46)),
    ("Crate B", "rect", (2.22, 0.74), (0.38, 0.28)),
    ("Drum C", "circle", (-0.12, 2.04), (0.30, 0.30)),
]


def load_rows() -> list[dict[str, float | int | str]]:
    rows: list[dict[str, float | int | str]] = []
    with CSV_PATH.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            row: dict[str, float | int | str] = {}
            for key, value in raw.items():
                if key in STRING_COLUMNS:
                    row[key] = value
                elif key in INT_COLUMNS:
                    row[key] = int(float(value))
                else:
                    row[key] = float(value)
            rows.append(row)
    return rows


def values(rows: list[dict[str, float | int | str]], key: str) -> list[float]:
    return [float(row[key]) for row in rows]


def parse_landmarks(map_string: str) -> list[tuple[int, float, float, int]]:
    return [
        (int(m.group("id")), float(m.group("x")), float(m.group("y")), int(m.group("seen")))
        for m in LANDMARK_RE.finditer(map_string)
    ]


def phase2_obstacle_targets(row: dict[str, float | int | str]) -> list[tuple[float, float]]:
    targets = list(PHASE2_STATIC_OBSTACLES)
    if int(row.get("dynamic_obstacle_active", 0)) == 1:
        targets.append((float(row["dynamic_pallet_x"]), float(row["dynamic_pallet_y"])))
    if int(row.get("temporary_blocker_active", 0)) == 1:
        targets.append((float(row["temporary_blocker_x"]), float(row["temporary_blocker_y"])))
    return targets


def map_quality_proxy(
    features: list[tuple[int, float, float, int]],
    row: dict[str, float | int | str],
) -> dict[str, float]:
    targets = phase2_obstacle_targets(row)
    if not targets:
        return {"recall": 0.0, "precision": 0.0}
    if not features:
        return {"recall": 0.0, "precision": 0.0}

    feature_xy = [(x, y) for _idx, x, y, _seen in features]
    matched_targets = 0
    for tx, ty in targets:
        if any(math.hypot(tx - fx, ty - fy) <= MAP_MATCH_RADIUS_M for fx, fy in feature_xy):
            matched_targets += 1

    matched_features = 0
    for fx, fy in feature_xy:
        if any(math.hypot(tx - fx, ty - fy) <= MAP_MATCH_RADIUS_M for tx, ty in targets):
            matched_features += 1

    return {
        "recall": round(matched_targets / len(targets), 3),
        "precision": round(matched_features / len(feature_xy), 3),
    }


def row_map_string(row: dict[str, float | int | str]) -> str:
    slam_map = str(row.get("slam_map", ""))
    grid_map = str(row.get("grid_map", ""))
    if slam_map:
        return slam_map
    return grid_map


def finite(data: list[float]) -> list[float]:
    return [value for value in data if math.isfinite(value)]


def percentile(data: list[float], q: float) -> float:
    values_in = sorted(finite(data))
    if not values_in:
        return math.nan
    rank = (len(values_in) - 1) * q
    lo = math.floor(rank)
    hi = math.ceil(rank)
    if lo == hi:
        return values_in[lo]
    return values_in[lo] + (values_in[hi] - values_in[lo]) * (rank - lo)


def threshold_row(rows: list[dict[str, float | int | str]], key: str, threshold: float) -> dict[str, float | int | str]:
    for row in rows:
        if float(row[key]) >= threshold:
            return row
    return rows[-1]


def decimated_waypoints(rows: list[dict[str, float | int | str]]) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    last: tuple[float, float] | None = None
    for row in rows:
        if int(row["planner_wp_active"]) != 1:
            continue
        point = (float(row["planner_wp_x"]), float(row["planner_wp_y"]))
        if not math.isfinite(point[0]) or not math.isfinite(point[1]):
            continue
        if last is None or math.hypot(point[0] - last[0], point[1] - last[1]) > 0.12:
            points.append(point)
            last = point
    return points


def mode_durations(rows: list[dict[str, float | int | str]], key: str) -> dict[str, float]:
    durations: dict[str, float] = {}
    for prev, row in zip(rows, rows[1:]):
        dt = max(0.0, float(row["t"]) - float(prev["t"]))
        mode = str(prev[key])
        durations[mode] = durations.get(mode, 0.0) + dt
    return {key: round(value, 3) for key, value in sorted(durations.items())}


def draw_static_context(ax) -> None:
    for label, center, size in UNKNOWN_ZONES:
        x, y = center
        sx, sy = size
        ax.add_patch(
            patches.Rectangle(
                (x - sx / 2.0, y - sy / 2.0),
                sx,
                sy,
                facecolor="#6b7280",
                edgecolor="#d19a21",
                linewidth=1.0,
                alpha=0.12,
            )
        )
        ax.text(x, y + sy / 2.0 - 0.10, label, fontsize=7, ha="center", color="#6b4b12")

    for label, kind, center, size in STATIC_UNKNOWN_OBSTACLES:
        x, y = center
        if kind == "rect":
            sx, sy = size
            ax.add_patch(
                patches.Rectangle(
                    (x - sx / 2.0, y - sy / 2.0),
                    sx,
                    sy,
                    facecolor="#8a4b24",
                    edgecolor="#4b2a12",
                    linewidth=1.1,
                    alpha=0.85,
                )
            )
        else:
            ax.add_patch(
                patches.Circle(
                    (x, y),
                    radius=size[0] / 2.0,
                    facecolor="#3f4247",
                    edgecolor="#111827",
                    linewidth=1.1,
                    alpha=0.85,
                )
            )
        ax.text(x + 0.05, y + 0.05, label, fontsize=7, color="#111827")

    for label, (x, y) in FRONTIERS:
        ax.scatter([x], [y], s=35, marker="*", color="#1f9acb", edgecolor="white", linewidth=0.5, zorder=4)
        ax.text(x + 0.04, y + 0.04, label, fontsize=7, color="#0c4a6e")


def draw_map_state(ax, rows: list[dict[str, float | int | str]], row: dict[str, float | int | str], title: str) -> None:
    t_end = float(row["t"])
    partial = [r for r in rows if float(r["t"]) <= t_end]
    landmarks = parse_landmarks(row_map_string(row))

    draw_static_context(ax)
    ax.plot(values(partial, "robot_x"), values(partial, "robot_y"), color="#1f5fa8", linewidth=1.8, label="R1 real")
    ax.plot(values(partial, "est_x"), values(partial, "est_y"), color="#10a37f", linewidth=1.2, linestyle="--", label="R1 estimado")
    ax.plot(values(partial, "dynamic_pallet_x"), values(partial, "dynamic_pallet_y"), color="#c9472c", linewidth=1.3, alpha=0.85, label="pallet dinamico")
    if landmarks:
        ax.scatter([p[1] for p in landmarks], [p[2] for p in landmarks], s=42, marker="x", color="#c9472c", label="mapa SLAM")
        for idx, x, y, _seen in landmarks:
            ax.text(x + 0.03, y + 0.03, f"O{idx}", fontsize=6.6, color="#8a2d1d")
    ax.scatter([float(row["robot_x"])], [float(row["robot_y"])], s=46, color="#1f5fa8", edgecolor="white", zorder=5)
    ax.set_title(title)
    ax.set_xlim(-2.85, 2.85)
    ax.set_ylim(-2.65, 2.55)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.22)


def compute_analysis(rows: list[dict[str, float | int | str]]) -> dict[str, object]:
    final = rows[-1]
    final_landmarks = parse_landmarks(row_map_string(final))
    quality = map_quality_proxy(final_landmarks, final)
    pose_errors = values(rows, "pose_error")
    evidence_key = "mapping_evidence_pct" if "mapping_evidence_pct" in final else "map_revealed_pct"
    evidence = values(rows, evidence_key)
    risks = values(rows, "obstacle_risk")
    min_obstacles = [value for value in values(rows, "min_obstacle") if value > 0]

    return {
        "duration_s": round(float(final["t"]) - float(rows[0]["t"]), 3),
        "samples": len(rows),
        "unknown_map_prior_known": False,
        "final_task_state": str(final["task_state"]),
        "completed_task_count": int(final["completed_task_count"]),
        "phase2_motion_model": str(final.get("phase2_motion_model", "")),
        "phase2_moved_objects": str(final.get("phase2_moved_objects", "")),
        "mapping": {
            "final_evidence_pct": round(float(final[evidence_key]), 3),
            "max_evidence_pct": round(max(evidence), 3),
            "time_to_25pct_s": float(threshold_row(rows, evidence_key, 25.0)["t"]),
            "time_to_50pct_s": float(threshold_row(rows, evidence_key, 50.0)["t"]),
            "time_to_75pct_s": float(threshold_row(rows, evidence_key, 75.0)["t"]),
            "landmarks_final": int(final["slam_landmarks"]),
            "landmarks_from_final_map": len(final_landmarks),
            "phase2_obstacle_recall_proxy": quality["recall"],
            "phase2_feature_precision_proxy": quality["precision"],
            "slam_updates": int(final["slam_updates"]),
            "frontier_count": int(final["frontier_count"]),
            "unknown_cells_declared": int(final["unknown_cells"]),
        },
        "dynamic_obstacles": {
            "pallet_crossings": int(final["obstacle_crossings"]),
            "temporary_blocker_active_samples": sum(int(row["temporary_blocker_active"]) for row in rows),
            "replan_triggers": int(final["replan_triggers"]),
            "planner_recovery_count": int(final.get("planner_recovery_count", 0)),
            "max_obstacle_risk": round(max(risks), 3),
            "min_obstacle_m": round(min(min_obstacles), 3) if min_obstacles else None,
        },
        "estimator": {
            "mean_pose_error_m": round(fmean(pose_errors), 5),
            "p95_pose_error_m": round(percentile(pose_errors, 0.95), 5),
            "max_pose_error_m": round(max(pose_errors), 5),
        },
        "durations": {
            "planner_modes_s": mode_durations(rows, "planner_mode"),
            "motion_modes_s": mode_durations(rows, "motion_mode"),
        },
    }


def write_analysis_markdown(analysis: dict[str, object]) -> None:
    mapping = analysis["mapping"]
    dynamic = analysis["dynamic_obstacles"]
    estimator = analysis["estimator"]
    durations = analysis["durations"]
    motion_model = analysis.get("phase2_motion_model", "")
    moved_objects = analysis.get("phase2_moved_objects", "")

    lines = [
        "# Phase 2 Unknown SLAM - export de mapeo",
        "",
        "## Supuesto de mapa desconocido",
        "",
        "R1 no recibe el mapa completo al inicio. La escena contiene zonas desconocidas, frontiers, obstaculos estaticos no modelados, una tarima dinamica y un bloque temporal. El mapa publicado crece con lecturas de proximidad y actualizaciones SLAM.",
        "",
        f"Los objetos que se mueven por script son: {moved_objects}. El modelo de movimiento es {motion_model}.",
        "",
        "## Evidencia exportada",
        "",
        f"- Evidencia de mapeo final: {mapping['final_evidence_pct']}%",
        f"- Tiempo hasta 25/50/75%: {mapping['time_to_25pct_s']} s / {mapping['time_to_50pct_s']} s / {mapping['time_to_75pct_s']} s",
        f"- Landmarks finales: {mapping['landmarks_final']}",
        f"- Recall proxy de obstaculos Phase 2: {mapping['phase2_obstacle_recall_proxy']}",
        f"- Precision proxy de features: {mapping['phase2_feature_precision_proxy']}",
        f"- Actualizaciones SLAM: {mapping['slam_updates']}",
        f"- Frontiers declarados: {mapping['frontier_count']}",
        f"- Celdas desconocidas declaradas: {mapping['unknown_cells_declared']}",
        "",
        "La evidencia de mapeo no es cobertura geometrica contra ground truth. Es un indicador de actividad del mapa; la calidad geometrica se estima con proxies de obstaculos detectados.",
        "",
        "## Obstaculos dinamicos y replanning",
        "",
        f"- Cruces de la tarima dinamica: {dynamic['pallet_crossings']}",
        f"- Triggers de replanning: {dynamic['replan_triggers']}",
        f"- Recuperaciones del planner: {dynamic['planner_recovery_count']}",
        f"- Riesgo maximo de obstaculo: {dynamic['max_obstacle_risk']}",
        f"- Distancia minima positiva a obstaculo: {dynamic['min_obstacle_m']} m",
        "",
        "## Estimador",
        "",
        f"- Error medio de pose: {estimator['mean_pose_error_m']} m",
        f"- Error P95 de pose: {estimator['p95_pose_error_m']} m",
        f"- Error maximo de pose: {estimator['max_pose_error_m']} m",
        "",
        "## Modos",
        "",
        f"- Planner: {durations['planner_modes_s']}",
        f"- Movimiento: {durations['motion_modes_s']}",
        "",
    ]
    ANALYSIS_MD.write_text("\n".join(lines), encoding="utf-8")


def plot_overview(rows: list[dict[str, float | int | str]]) -> None:
    final = rows[-1]
    landmarks = parse_landmarks(row_map_string(final))
    waypoints = decimated_waypoints(rows)

    fig, axes = plt.subplots(2, 2, figsize=(13.8, 8.4))
    fig.suptitle("Phase 2 - unknown-map SLAM with dynamic obstacles", fontsize=15, fontweight="bold")

    ax = axes[0, 0]
    draw_static_context(ax)
    ax.plot(values(rows, "robot_x"), values(rows, "robot_y"), color="#1f5fa8", linewidth=2.0, label="R1 real")
    ax.plot(values(rows, "est_x"), values(rows, "est_y"), color="#10a37f", linewidth=1.4, linestyle="--", label="R1 estimado")
    ax.plot(values(rows, "b1_x"), values(rows, "b1_y"), color="#111827", linewidth=1.8, label="B1")
    ax.plot(values(rows, "dynamic_pallet_x"), values(rows, "dynamic_pallet_y"), color="#c9472c", linewidth=1.7, label="pallet dinamico")
    active_blocker = [row for row in rows if int(row["temporary_blocker_active"]) == 1]
    if active_blocker:
        ax.scatter(values(active_blocker, "temporary_blocker_x"), values(active_blocker, "temporary_blocker_y"), s=10, color="#d19a21", alpha=0.35, label="blocker activo")
    if waypoints:
        ax.scatter([p[0] for p in waypoints], [p[1] for p in waypoints], s=28, marker="D", color="#7e4aa8", label="waypoints SLAM")
    if landmarks:
        ax.scatter([p[1] for p in landmarks], [p[2] for p in landmarks], s=56, marker="x", color="#c9472c", label="landmarks mapeados")
    ax.set_title("Trayectoria y mapa final")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_xlim(-2.85, 2.85)
    ax.set_ylim(-2.65, 2.55)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.24)
    ax.legend(loc="best", fontsize=7)

    ax = axes[0, 1]
    evidence_key = "mapping_evidence_pct" if "mapping_evidence_pct" in rows[-1] else "map_revealed_pct"
    ax.plot(values(rows, "t"), values(rows, evidence_key), color="#10a37f", linewidth=2.0, label="evidencia mapa")
    ax2 = ax.twinx()
    ax2.step(values(rows, "t"), values(rows, "slam_landmarks"), where="post", color="#c9472c", linewidth=1.5, label="landmarks")
    ax.set_title("Crecimiento del mapa")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("[%]")
    ax2.set_ylabel("landmarks")
    ax.grid(True, alpha=0.24)
    ax.legend(loc="upper left")
    ax2.legend(loc="lower right")

    ax = axes[1, 0]
    ax.plot(values(rows, "t"), values(rows, "min_obstacle"), color="#1f5fa8", linewidth=1.3, label="distancia obstaculo")
    ax2 = ax.twinx()
    ax2.plot(values(rows, "t"), values(rows, "obstacle_risk"), color="#c9472c", linewidth=1.5, label="riesgo")
    ax.fill_between(values(rows, "t"), 0, values(rows, "temporary_blocker_active"), color="#d19a21", alpha=0.15, transform=ax.get_xaxis_transform(), label="blocker activo")
    ax.set_title("Lecturas de obstaculos")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("m")
    ax2.set_ylabel("riesgo [0-1]")
    ax.grid(True, alpha=0.24)
    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")

    ax = axes[1, 1]
    ax.step(values(rows, "t"), values(rows, "replan_triggers"), where="post", color="#7e4aa8", linewidth=1.8, label="replanning")
    ax.step(values(rows, "t"), values(rows, "obstacle_crossings"), where="post", color="#c9472c", linewidth=1.5, label="cruces pallet")
    ax2 = ax.twinx()
    ax2.plot(values(rows, "t"), values(rows, "battery"), color="#217a3f", linewidth=1.3, label="bateria")
    ax.set_title("Replanning y mision")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("eventos")
    ax2.set_ylabel("bateria [%]")
    ax.grid(True, alpha=0.24)
    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(OVERVIEW_PNG, dpi=180)
    plt.close(fig)


def plot_snapshots(rows: list[dict[str, float | int | str]]) -> None:
    evidence_key = "mapping_evidence_pct" if "mapping_evidence_pct" in rows[-1] else "map_revealed_pct"
    snapshots = [
        ("25% evidencia", threshold_row(rows, evidence_key, 25.0)),
        ("50% evidencia", threshold_row(rows, evidence_key, 50.0)),
        ("75% evidencia", threshold_row(rows, evidence_key, 75.0)),
        ("final", rows[-1]),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(13.8, 8.8))
    fig.suptitle("Phase 2 - snapshots de como R1 construye el mapa", fontsize=15, fontweight="bold")

    for ax, (label, row) in zip(axes.flat, snapshots):
        title = f"{label}: t={float(row['t']):.1f}s, evid={float(row[evidence_key]):.1f}%, L={int(row['slam_landmarks'])}"
        draw_map_state(ax, rows, row, title)

    handles, labels = axes.flat[-1].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.savefig(SNAPSHOTS_PNG, dpi=180)
    plt.close(fig)


def plot_signals(rows: list[dict[str, float | int | str]]) -> None:
    t = values(rows, "t")

    fig, axes = plt.subplots(3, 1, figsize=(13.8, 8.6), sharex=True)
    fig.suptitle("Phase 2 - senales exportadas para justificar el mapeo", fontsize=15, fontweight="bold")

    ax = axes[0]
    evidence_key = "mapping_evidence_pct" if "mapping_evidence_pct" in rows[-1] else "map_revealed_pct"
    ax.plot(t, values(rows, evidence_key), color="#10a37f", linewidth=1.9, label="evidencia mapa")
    ax2 = ax.twinx()
    ax2.step(t, values(rows, "slam_updates"), where="post", color="#7e4aa8", linewidth=1.2, label="updates SLAM")
    ax.set_ylabel("[%]")
    ax2.set_ylabel("updates")
    ax.set_title("Evidencia acumulada de mapa")
    ax.grid(True, alpha=0.24)
    ax.legend(loc="upper left")
    ax2.legend(loc="lower right")

    ax = axes[1]
    ax.plot(t, values(rows, "dynamic_pallet_x"), color="#c9472c", linewidth=1.4, label="pallet x")
    ax.plot(t, values(rows, "dynamic_pallet_y"), color="#8a2d1d", linewidth=1.1, label="pallet y")
    ax.step(t, values(rows, "temporary_blocker_active"), where="post", color="#d19a21", linewidth=1.4, label="blocker activo")
    ax.set_ylabel("m / activo")
    ax.set_title("Obstaculos no modelados")
    ax.grid(True, alpha=0.24)
    ax.legend(loc="best")

    ax = axes[2]
    planner_codes = {"DIRECT": 0, "SLAM_WAYPOINT": 1, "DIRECT_AFTER_WAYPOINT": 2, "RECOVERY_DIRECT": 3}
    motion_codes = {"ROUTE": 0, "AVOIDING": 1, "MANIPULATING": 2, "WAIT_B1": 3, "ARRIVED_TARGET": 4, "SLAM_PATH": 5}
    ax.step(t, [planner_codes.get(str(row["planner_mode"]), -1) for row in rows], where="post", color="#7e4aa8", linewidth=1.5, label="planner")
    ax.step(t, [motion_codes.get(str(row["motion_mode"]), -1) for row in rows], where="post", color="#1f5fa8", linewidth=1.2, label="movimiento")
    ax2 = ax.twinx()
    ax2.step(t, values(rows, "replan_triggers"), where="post", color="#c9472c", linewidth=1.3, label="replan triggers")
    ax.set_yticks([0, 1, 2, 3, 4, 5], ["direct/route", "slam/avoid", "after/manip", "recovery/wait", "arrived", "slam_path"])
    ax.set_xlabel("t [s]")
    ax.set_title("Decisiones de navegacion")
    ax.grid(True, alpha=0.24)
    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(SIGNALS_PNG, dpi=180)
    plt.close(fig)


def main() -> int:
    if not CSV_PATH.exists():
        raise FileNotFoundError(CSV_PATH)

    rows = load_rows()
    analysis = compute_analysis(rows)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSIS_JSON.write_text(json.dumps(analysis, indent=2), encoding="utf-8")
    write_analysis_markdown(analysis)

    plot_overview(rows)
    plot_snapshots(rows)
    plot_signals(rows)
    evidence_key = "mapping_evidence_pct" if "mapping_evidence_pct" in rows[-1] else "map_revealed_pct"

    outputs = {
        "csv": str(CSV_PATH),
        "summary": str(SUMMARY_JSON),
        "analysis": [str(ANALYSIS_JSON), str(ANALYSIS_MD)],
        "plots": [str(OVERVIEW_PNG), str(SNAPSHOTS_PNG), str(SIGNALS_PNG)],
        "rows": len(rows),
        "final_mapping_evidence_pct": float(rows[-1][evidence_key]),
        "final_landmarks": int(rows[-1]["slam_landmarks"]),
    }
    print(json.dumps(outputs, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
