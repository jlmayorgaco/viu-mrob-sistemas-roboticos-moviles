"""Compare Phase 2 unknown-map SLAM runs."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from statistics import fmean

import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

import plot_phase2_slam_unknown_export as phase2_plot


ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "actividad2" / "coppeliasim" / "phase2_slam_logs"
RUNS = {
    "GMAPPING_GRID": LOG_DIR / "phase2_slam_unknown_gmapping_grid.csv",
    "HECTOR_GRID_MATCHING": LOG_DIR / "phase2_slam_unknown_hector_grid_matching.csv",
    "CARTOGRAPHER_SUBMAP": LOG_DIR / "phase2_slam_unknown_cartographer_submap.csv",
    "KALMAN_LANDMARK": LOG_DIR / "phase2_slam_unknown_kalman_landmark.csv",
}
LABELS = {
    "GMAPPING_GRID": "GMapping grid",
    "HECTOR_GRID_MATCHING": "Hector matching",
    "CARTOGRAPHER_SUBMAP": "Cartographer submap",
    "KALMAN_LANDMARK": "Kalman landmarks",
}
COLORS = {
    "GMAPPING_GRID": "#c9472c",
    "HECTOR_GRID_MATCHING": "#7e4aa8",
    "CARTOGRAPHER_SUBMAP": "#217a3f",
    "KALMAN_LANDMARK": "#1f5fa8",
}

COMPARISON_PNG = LOG_DIR / "phase2_slam_unknown_algorithm_comparison.png"
RECONSTRUCTION_PNG = LOG_DIR / "phase2_slam_unknown_reconstruction_t60.png"
COMPARISON_MD = LOG_DIR / "phase2_slam_unknown_algorithm_comparison.md"
COMPARISON_METRICS_JSON = LOG_DIR / "phase2_slam_unknown_algorithm_metrics.json"
RECONSTRUCTION_TIME_S = 60.0


def load_rows(path: Path) -> list[dict[str, float | int | str]]:
    rows: list[dict[str, float | int | str]] = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            row: dict[str, float | int | str] = {}
            for key, value in raw.items():
                if key in phase2_plot.STRING_COLUMNS:
                    row[key] = value
                elif key in phase2_plot.INT_COLUMNS:
                    row[key] = int(float(value))
                else:
                    row[key] = float(value)
            rows.append(row)
    return rows


def values(rows: list[dict[str, float | int | str]], key: str) -> list[float]:
    return [float(row[key]) for row in rows]


def finite(data: list[float]) -> list[float]:
    return [value for value in data if math.isfinite(value)]


def rmse(data: list[float]) -> float:
    vals = finite(data)
    if not vals:
        return math.nan
    return math.sqrt(fmean([value * value for value in vals]))


def percentile(data: list[float], q: float) -> float:
    vals = sorted(finite(data))
    if not vals:
        return math.nan
    rank = (len(vals) - 1) * q
    lo = math.floor(rank)
    hi = math.ceil(rank)
    if lo == hi:
        return vals[lo]
    return vals[lo] + (vals[hi] - vals[lo]) * (rank - lo)


def threshold_time(rows: list[dict[str, float | int | str]], key: str, threshold: float) -> float | None:
    for row in rows:
        if float(row[key]) >= threshold:
            return round(float(row["t"]), 3)
    return None


def nearest_row(rows: list[dict[str, float | int | str]], target_t: float) -> dict[str, float | int | str]:
    return min(rows, key=lambda row: abs(float(row["t"]) - target_t))


def path_length(rows: list[dict[str, float | int | str]]) -> float:
    total = 0.0
    for prev, row in zip(rows, rows[1:]):
        dx = float(row["robot_x"]) - float(prev["robot_x"])
        dy = float(row["robot_y"]) - float(prev["robot_y"])
        if math.isfinite(dx) and math.isfinite(dy):
            total += math.hypot(dx, dy)
    return total


def duration_by(rows: list[dict[str, float | int | str]], key: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for prev, row in zip(rows, rows[1:]):
        dt = max(0.0, float(row["t"]) - float(prev["t"]))
        name = str(prev[key])
        out[name] = out.get(name, 0.0) + dt
    return {key: round(value, 3) for key, value in sorted(out.items())}


def metrics(rows: list[dict[str, float | int | str]]) -> dict[str, object]:
    final = rows[-1]
    evidence_key = "mapping_evidence_pct" if "mapping_evidence_pct" in final else "map_revealed_pct"
    ex = [float(row["est_x"]) - float(row["robot_x"]) for row in rows]
    ey = [float(row["est_y"]) - float(row["robot_y"]) for row in rows]
    pos_err = [math.hypot(x, y) for x, y in zip(ex, ey)]
    pose_error = values(rows, "pose_error")
    min_obstacles = [float(row["min_obstacle"]) for row in rows if float(row["min_obstacle"]) > 0]
    t60 = nearest_row(rows, RECONSTRUCTION_TIME_S)
    t60_map = phase2_plot.parse_landmarks(phase2_plot.row_map_string(t60))
    final_map = phase2_plot.parse_landmarks(phase2_plot.row_map_string(final))
    t60_quality = phase2_plot.map_quality_proxy(t60_map, t60)
    final_quality = phase2_plot.map_quality_proxy(final_map, final)

    return {
        "algorithm": str(final["slam_algorithm"]),
        "localization_mode": str(final["localization_mode"]),
        "phase2_motion_model": str(final.get("phase2_motion_model", "")),
        "phase2_moved_objects": str(final.get("phase2_moved_objects", "")),
        "completed": int(final["task_complete"]) == 1 and int(final["completed_task_count"]) >= 4,
        "duration_s": round(float(final["t"]), 3),
        "samples": len(rows),
        "path_length_m": round(path_length(rows), 3),
        "rmse_position_m": round(rmse(pos_err), 5),
        "mean_pose_error_m": round(fmean(pose_error), 5),
        "p95_pose_error_m": round(percentile(pose_error, 0.95), 5),
        "max_pose_error_m": round(max(pose_error), 5),
        "mapping_evidence_final_pct": round(float(final[evidence_key]), 3),
        "map_revealed_final_pct": round(float(final.get("map_revealed_pct", final[evidence_key])), 3),
        "mapping_evidence_50pct_time_s": threshold_time(rows, evidence_key, 50.0),
        "mapping_evidence_75pct_time_s": threshold_time(rows, evidence_key, 75.0),
        "map_features_t60": len(t60_map),
        "map_features_final": len(final_map),
        "phase2_obstacle_recall_t60": t60_quality["recall"],
        "phase2_feature_precision_t60": t60_quality["precision"],
        "phase2_obstacle_recall_final": final_quality["recall"],
        "phase2_feature_precision_final": final_quality["precision"],
        "slam_count_final": int(final["slam_landmarks"]),
        "slam_updates": int(final["slam_updates"]),
        "grid_occupied_cells_final": int(final["grid_occupied_cells"]),
        "grid_updates": int(final["grid_updates"]),
        "cartographer_submaps_final": int(final["cartographer_submaps"]),
        "loop_closures_final": int(final["loop_closures"]),
        "replan_triggers": int(final["replan_triggers"]),
        "planner_recovery_count": int(final.get("planner_recovery_count", 0)),
        "dynamic_obstacle_crossings": int(final["obstacle_crossings"]),
        "min_obstacle_m": round(min(min_obstacles), 5) if min_obstacles else None,
        "max_obstacle_risk": round(max(values(rows, "obstacle_risk")), 5),
        "battery_used_pct": round(float(rows[0]["battery"]) - float(final["battery"]), 5),
        "planner_durations_s": duration_by(rows, "planner_mode"),
        "motion_durations_s": duration_by(rows, "motion_mode"),
    }


def draw_reconstruction(ax, name: str, rows: list[dict[str, float | int | str]], target_t: float) -> None:
    row = nearest_row(rows, target_t)
    evidence_key = "mapping_evidence_pct" if "mapping_evidence_pct" in row else "map_revealed_pct"
    upto = [item for item in rows if float(item["t"]) <= float(row["t"])]
    mapped = phase2_plot.parse_landmarks(phase2_plot.row_map_string(row))

    phase2_plot.draw_static_context(ax)
    ax.plot(values(upto, "robot_x"), values(upto, "robot_y"), color=COLORS[name], linewidth=1.8, label="R1")
    ax.plot(values(upto, "est_x"), values(upto, "est_y"), color=COLORS[name], linewidth=1.1, linestyle="--", alpha=0.75, label="estimado")
    ax.plot(values(upto, "dynamic_pallet_x"), values(upto, "dynamic_pallet_y"), color="#111827", linewidth=1.0, alpha=0.65, label="pallet")
    if mapped:
        marker = "s" if name in {"GMAPPING_GRID", "HECTOR_GRID_MATCHING", "CARTOGRAPHER_SUBMAP"} else "x"
        ax.scatter([p[1] for p in mapped], [p[2] for p in mapped], s=28, marker=marker, color=COLORS[name], alpha=0.78, label="reconstruccion")
    ax.scatter([float(row["robot_x"])], [float(row["robot_y"])], s=44, color=COLORS[name], edgecolor="white", zorder=5)
    ax.set_title(f"{LABELS[name]} | t={float(row['t']):.1f}s | evid={float(row[evidence_key]):.1f}% | n={len(mapped)}")
    ax.set_xlim(-2.85, 2.85)
    ax.set_ylim(-2.65, 2.55)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.22)


def write_markdown(all_metrics: dict[str, dict[str, object]]) -> None:
    ordered = [name for name in RUNS if name in all_metrics]
    header = "| Métrica | " + " | ".join(ordered) + " |"
    separator = "|---|" + "|".join(["---:" for _ in ordered]) + "|"

    def row(label: str, key: str) -> str:
        return "| " + label + " | " + " | ".join(str(all_metrics[name][key]) for name in ordered) + " |"

    lines = [
        "# Comparación SLAM - Phase 2 Unknown Map",
        "",
        "## Alcance",
        "",
        "La comparación usa la misma escena `Sim_T2_Phase2_SLAM_Unknown.ttt`, el mismo controlador PID y los mismos sensores de proximidad visualizados como rayos. R1 parte sin mapa completo y reconstruye obstáculos desde lecturas en línea. Los nombres GMapping, Hector y Cartographer identifican el enfoque implementado en Lua dentro de CoppeliaSim.",
        "",
        "Solo `P2_Dynamic_Pallet` y `P2_Temporary_Blocker` se mueven por script. Su movimiento es determinístico y periódico; las cajas y marcadores desconocidos permanecen fijos.",
        "",
        f"La figura `phase2_slam_unknown_reconstruction_t60.png` compara la reconstrucción del mapa al mismo instante común: t={RECONSTRUCTION_TIME_S:.1f} s.",
        "",
        "## Resultados",
        "",
        header,
        separator,
        row("Completado", "completed"),
        row("Duración [s]", "duration_s"),
        row("Evidencia mapa final [%]", "mapping_evidence_final_pct"),
        row("Tiempo a 50% evidencia [s]", "mapping_evidence_50pct_time_s"),
        row("Tiempo a 75% evidencia [s]", "mapping_evidence_75pct_time_s"),
        row("Rasgos t=60s", "map_features_t60"),
        row("Rasgos finales", "map_features_final"),
        row("Recall proxy t=60s", "phase2_obstacle_recall_t60"),
        row("Precisión proxy final", "phase2_feature_precision_final"),
        row("Actualizaciones SLAM", "slam_updates"),
        row("RMSE posición [m]", "rmse_position_m"),
        row("Error P95 pose [m]", "p95_pose_error_m"),
        row("Replanificaciones", "replan_triggers"),
        row("Recuperaciones del planificador", "planner_recovery_count"),
        row("Cruces pallet", "dynamic_obstacle_crossings"),
        row("Distancia mínima a obstáculo [m]", "min_obstacle_m"),
        row("Riesgo máximo", "max_obstacle_risk"),
        row("Batería usada [%]", "battery_used_pct"),
        row("Submapas", "cartographer_submaps_final"),
        row("Cierres de ciclo", "loop_closures_final"),
        "",
        "## Interpretación técnica",
        "",
        "La evidencia de mapa mide actividad de mapeo. La calidad geométrica se reporta con proxies de recall y precisión frente a obstáculos Phase 2 conocidos. `GMAPPING_GRID`, `HECTOR_GRID_MATCHING` y `CARTOGRAPHER_SUBMAP` reconstruyen una grilla dispersa desde rayos; `KALMAN_LANDMARK` reconstruye landmarks puntuales. Hector agrega ajuste local de escaneos y Cartographer agrega submapas con cierres de ciclo locales.",
        "",
        "La columna `Completado` tiene prioridad sobre RMSE o evidencia de mapa al seleccionar el método operativo.",
        "",
    ]
    COMPARISON_MD.write_text("\n".join(lines), encoding="utf-8")


def plot_comparison(datasets: dict[str, list[dict[str, float | int | str]]], all_metrics: dict[str, dict[str, object]]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(15.8, 9.4))
    fig.suptitle("Phase 2 Unknown Map - comparación SLAM con rayos de proximidad", fontsize=15, fontweight="bold")

    ax = axes[0, 0]
    phase2_plot.draw_static_context(ax)
    for name, rows in datasets.items():
        ax.plot(values(rows, "robot_x"), values(rows, "robot_y"), linewidth=1.6, color=COLORS[name], label=LABELS[name])
        mapped = phase2_plot.parse_landmarks(phase2_plot.row_map_string(rows[-1]))
        if mapped:
            ax.scatter([p[1] for p in mapped], [p[2] for p in mapped], s=15, marker="x", color=COLORS[name], alpha=0.45)
    ax.plot(values(next(iter(datasets.values())), "dynamic_pallet_x"), values(next(iter(datasets.values())), "dynamic_pallet_y"), color="#111827", linewidth=1.1, alpha=0.55, label="pallet")
    ax.set_title("Trayectorias y mapas finales")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.set_xlim(-2.85, 2.85)
    ax.set_ylim(-2.65, 2.55)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, alpha=0.24)
    ax.legend(loc="best", fontsize=7)

    ax = axes[0, 1]
    for name, rows in datasets.items():
        evidence_key = "mapping_evidence_pct" if "mapping_evidence_pct" in rows[-1] else "map_revealed_pct"
        ax.plot(values(rows, "t"), values(rows, evidence_key), linewidth=1.55, color=COLORS[name], label=LABELS[name])
    ax.set_title("Evidencia de mapa vs tiempo")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("[%]")
    ax.grid(True, alpha=0.24)
    ax.legend(loc="best")

    ax = axes[1, 0]
    for name, rows in datasets.items():
        pos_err = [math.hypot(float(row["est_x"]) - float(row["robot_x"]), float(row["est_y"]) - float(row["robot_y"])) for row in rows]
        ax.plot(values(rows, "t"), pos_err, linewidth=1.35, color=COLORS[name], label=LABELS[name])
    ax.set_title("Error de estimación de posición")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("m")
    ax.grid(True, alpha=0.24)
    ax.legend(loc="best")

    ax = axes[1, 1]
    ax.axis("off")
    ax.set_title("Métricas comparativas")
    metric_rows = [
        ("Evid final [%]", "mapping_evidence_final_pct"),
        ("Rasgos t60", "map_features_t60"),
        ("Rasgos final", "map_features_final"),
        ("Recall t60", "phase2_obstacle_recall_t60"),
        ("Prec final", "phase2_feature_precision_final"),
        ("Actualiz.", "slam_updates"),
        ("RMSE pos [m]", "rmse_position_m"),
        ("P95 pose [m]", "p95_pose_error_m"),
        ("Replanif.", "replan_triggers"),
        ("Recup.", "planner_recovery_count"),
        ("Riesgo max", "max_obstacle_risk"),
        ("Submapas", "cartographer_submaps_final"),
        ("Cierres", "loop_closures_final"),
    ]
    table_data = [[label] + [str(all_metrics[name][key]) for name in RUNS] for label, key in metric_rows]
    table = ax.table(
        cellText=table_data,
        colLabels=["Métrica"] + [LABELS[name] for name in RUNS],
        loc="center",
        cellLoc="center",
        colLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(7.2)
    table.scale(1.0, 1.36)

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(COMPARISON_PNG, dpi=180)
    plt.close(fig)


def plot_reconstructions(datasets: dict[str, list[dict[str, float | int | str]]]) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(13.8, 8.8))
    fig.suptitle(f"Phase 2 - reconstruccion SLAM en t={RECONSTRUCTION_TIME_S:.1f}s", fontsize=15, fontweight="bold")

    for ax, name in zip(axes.flat, RUNS):
        draw_reconstruction(ax, name, datasets[name], RECONSTRUCTION_TIME_S)

    handles, labels = axes.flat[-1].get_legend_handles_labels()
    if handles:
        fig.legend(handles, labels, loc="lower center", ncol=4, fontsize=8)
    fig.tight_layout(rect=(0, 0.04, 1, 0.95))
    fig.savefig(RECONSTRUCTION_PNG, dpi=180)
    plt.close(fig)


def main() -> int:
    datasets: dict[str, list[dict[str, float | int | str]]] = {}
    for name, path in RUNS.items():
        if not path.exists():
            raise FileNotFoundError(path)
        datasets[name] = load_rows(path)

    all_metrics = {name: metrics(rows) for name, rows in datasets.items()}
    COMPARISON_METRICS_JSON.write_text(json.dumps(all_metrics, indent=2), encoding="utf-8")
    write_markdown(all_metrics)
    plot_comparison(datasets, all_metrics)
    plot_reconstructions(datasets)

    print(
        json.dumps(
            {
                "comparison_plot": str(COMPARISON_PNG),
                "reconstruction_plot": str(RECONSTRUCTION_PNG),
                "metrics": str(COMPARISON_METRICS_JSON),
                "markdown": str(COMPARISON_MD),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
