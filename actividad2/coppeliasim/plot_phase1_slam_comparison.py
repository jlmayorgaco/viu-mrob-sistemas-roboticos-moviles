"""Plot and summarize Phase 1 SLAM algorithm comparison runs."""

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
RUNS = {
    "GMAPPING_GRID": LOG_DIR / "phase1_slam_gmapping_grid.csv",
    "HECTOR_GRID_MATCHING": LOG_DIR / "phase1_slam_hector_grid_matching.csv",
    "CARTOGRAPHER_SUBMAP": LOG_DIR / "phase1_slam_cartographer_submap.csv",
    "KALMAN_LANDMARK": LOG_DIR / "phase1_slam_kalman_landmark.csv",
}
LABELS = {
    "GMAPPING_GRID": "GMapping grid",
    "HECTOR_GRID_MATCHING": "Hector matching",
    "CARTOGRAPHER_SUBMAP": "Cartographer submapas",
    "KALMAN_LANDMARK": "Kalman rasgos",
}
COLORS = {
    "GMAPPING_GRID": "#c9472c",
    "HECTOR_GRID_MATCHING": "#7e4aa8",
    "CARTOGRAPHER_SUBMAP": "#217a3f",
    "KALMAN_LANDMARK": "#1f5fa8",
}
COMPARISON_PNG = LOG_DIR / "phase1_slam_algorithm_comparison.png"
COMPARISON_MD = LOG_DIR / "phase1_slam_algorithm_comparison.md"
COMPARISON_METRICS_JSON = LOG_DIR / "phase1_slam_algorithm_comparison_metrics.json"

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


def load_rows(path: Path) -> list[dict[str, float | int | str]]:
    rows: list[dict[str, float | int | str]] = []
    with path.open(newline="", encoding="utf-8") as fh:
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


def parse_map(text: str) -> list[tuple[int, float, float, int]]:
    return [
        (
            int(match.group("id")),
            float(match.group("x")),
            float(match.group("y")),
            int(match.group("seen")),
        )
        for match in LANDMARK_RE.finditer(text)
    ]


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


def duration_by(rows: list[dict[str, float | int | str]], key: str) -> dict[str, float]:
    out: dict[str, float] = {}
    for prev, row in zip(rows, rows[1:]):
        dt = max(0.0, float(row["t"]) - float(prev["t"]))
        name = str(prev[key])
        out[name] = out.get(name, 0.0) + dt
    return {key: round(value, 3) for key, value in sorted(out.items())}


def metrics(rows: list[dict[str, float | int | str]]) -> dict[str, object]:
    final = rows[-1]
    algorithm = str(final["slam_algorithm"])
    cartographer_mode = algorithm == "CARTOGRAPHER_SUBMAP"
    ex = [float(row["est_x"]) - float(row["robot_x"]) for row in rows]
    ey = [float(row["est_y"]) - float(row["robot_y"]) for row in rows]
    pos_err = [math.hypot(x, y) for x, y in zip(ex, ey)]
    min_obstacles = [float(row["min_obstacle"]) for row in rows if float(row["min_obstacle"]) > 0]
    path = 0.0
    for prev, row in zip(rows, rows[1:]):
        path += math.hypot(float(row["robot_x"]) - float(prev["robot_x"]), float(row["robot_y"]) - float(prev["robot_y"]))

    return {
        "algorithm": algorithm,
        "localization_mode": str(final["localization_mode"]),
        "completed": int(final["task_complete"]) == 1 and int(final["completed_task_count"]) >= 3,
        "duration_s": round(float(final["t"]), 3),
        "samples": len(rows),
        "path_length_m": round(path, 3),
        "rmse_position_m": round(rmse(pos_err), 5),
        "mean_position_error_m": round(fmean(pos_err), 5),
        "p95_position_error_m": round(percentile(pos_err, 0.95), 5),
        "max_position_error_m": round(max(pos_err), 5),
        "map_features_final": int(final["slam_landmarks"]),
        "slam_updates": int(final["slam_updates"]),
        "grid_occupied_cells_final": int(final["grid_occupied_cells"]),
        "grid_free_cells_final": int(final["grid_free_cells"]),
        "grid_entropy_final": round(float(final["grid_entropy"]), 5),
        "scan_match_score_final": round(float(final["scan_match_score"]), 5),
        "cartographer_submaps_final": int(final["cartographer_submaps"]) if cartographer_mode else 0,
        "loop_closures_final": int(final["loop_closures"]) if cartographer_mode else 0,
        "min_obstacle_m": round(min(min_obstacles), 5) if min_obstacles else None,
        "max_obstacle_risk": round(max(values(rows, "obstacle_risk")), 5),
        "battery_used_pct": round(float(rows[0]["battery"]) - float(final["battery"]), 5),
        "planner_durations_s": duration_by(rows, "planner_mode"),
        "motion_durations_s": duration_by(rows, "motion_mode"),
    }


def write_markdown(all_metrics: dict[str, dict[str, object]]) -> None:
    ordered = [name for name in RUNS if name in all_metrics]
    header = "| Métrica | " + " | ".join(ordered) + " |"
    separator = "|---|" + "|".join(["---:" for _ in ordered]) + "|"

    def row(label: str, key: str) -> str:
        return "| " + label + " | " + " | ".join(str(all_metrics[name][key]) for name in ordered) + " |"

    lines = [
        "# Comparación SLAM - Phase 1 Basic",
        "",
        "## Alcance",
        "",
        "La comparación usa modos implementados en CoppeliaSim con los mismos sensores, tarea, controlador y escenario. Los nombres GMapping, Hector y Cartographer identifican el enfoque usado en cada variante, no la ejecución de paquetes ROS externos:",
        "",
        "- `GMAPPING_GRID`: mapeo tipo GMapping basado en grilla de ocupación con actualización log-odds por rayos de proximidad.",
        "- `HECTOR_GRID_MATCHING`: ajuste local de escaneos contra grilla de ocupación, inspirado en Hector SLAM.",
        "- `CARTOGRAPHER_SUBMAP`: grilla con submapas y cierres de ciclo locales, inspirado en Google Cartographer.",
        "- `KALMAN_LANDMARK`: localización Kalman/EKF y rasgos de obstáculos actualizados con Kalman.",
        "",
        "## Resultados",
        "",
        header,
        separator,
        row("Completado", "completed"),
        row("Duración [s]", "duration_s"),
        row("Longitud de ruta [m]", "path_length_m"),
        row("RMSE posición [m]", "rmse_position_m"),
        row("Error P95 [m]", "p95_position_error_m"),
        row("Error máximo [m]", "max_position_error_m"),
        row("Rasgos/celdas finales", "map_features_final"),
        row("Actualizaciones SLAM", "slam_updates"),
        row("Submapas", "cartographer_submaps_final"),
        row("Cierres de ciclo", "loop_closures_final"),
        row("Distancia mínima a obstáculo [m]", "min_obstacle_m"),
        row("Riesgo máximo", "max_obstacle_risk"),
        row("Batería usada [%]", "battery_used_pct"),
        "",
        "## Interpretación técnica",
        "",
        "`GMAPPING_GRID`, `HECTOR_GRID_MATCHING` y `CARTOGRAPHER_SUBMAP` producen mapas de ocupación. `KALMAN_LANDMARK` produce un mapa compacto de puntos de obstáculo. Hector usa ajuste local de escaneos contra la grilla. Cartographer mantiene submapas y registra cierres de ciclo locales. La comparación queda acotada a CoppeliaSim y a los sensores de proximidad de la escena.",
        "",
        "Conclusión: los resultados comparan cuatro estrategias de estimación y mapeo dentro de la misma misión simulada.",
        "",
    ]
    COMPARISON_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    datasets = {}
    for name, path in RUNS.items():
        if not path.exists():
            raise FileNotFoundError(path)
        datasets[name] = load_rows(path)

    all_metrics = {name: metrics(rows) for name, rows in datasets.items()}
    COMPARISON_METRICS_JSON.write_text(json.dumps(all_metrics, indent=2), encoding="utf-8")
    write_markdown(all_metrics)

    fig, axes = plt.subplots(2, 2, figsize=(15.8, 9.2))
    fig.suptitle("Phase 1 Basic - comparación SLAM con rayos de proximidad", fontsize=15, fontweight="bold")

    ax = axes[0, 0]
    for name, rows in datasets.items():
        ax.plot(values(rows, "robot_x"), values(rows, "robot_y"), linewidth=1.7, color=COLORS[name], label=f"{LABELS[name]} R1")
        ax.plot(values(rows, "est_x"), values(rows, "est_y"), linewidth=1.0, linestyle="--", color=COLORS[name], alpha=0.75)
        final_map = str(rows[-1]["slam_map"])
        mapped = parse_map(final_map)
        if mapped:
            ax.scatter([p[1] for p in mapped], [p[2] for p in mapped], s=18, marker="x", color=COLORS[name], alpha=0.50)
    ax.set_title("Trayectoria, estimación y mapa final")
    ax.set_xlabel("x [m]")
    ax.set_ylabel("y [m]")
    ax.axis("equal")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")

    ax = axes[0, 1]
    for name, rows in datasets.items():
        pos_err = [math.hypot(float(row["est_x"]) - float(row["robot_x"]), float(row["est_y"]) - float(row["robot_y"])) for row in rows]
        ax.plot(values(rows, "t"), pos_err, linewidth=1.35, color=COLORS[name], label=LABELS[name])
    ax.set_title("Error de estimación de posición")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("m")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")

    ax = axes[1, 0]
    for name, rows in datasets.items():
        ax.step(values(rows, "t"), values(rows, "slam_landmarks"), where="post", linewidth=1.45, color=COLORS[name], label=LABELS[name])
    ax.set_title("Crecimiento del mapa")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("rasgos / celdas ocupadas")
    ax.grid(True, alpha=0.25)
    ax.legend(loc="best")

    ax = axes[1, 1]
    ordered = list(RUNS)
    x_pos = list(range(len(ordered)))
    rmse_values = [float(all_metrics[name]["rmse_position_m"]) for name in ordered]
    p95_values = [float(all_metrics[name]["p95_position_error_m"]) for name in ordered]
    width = 0.36
    ax.bar([x - width / 2 for x in x_pos], rmse_values, width=width, color=[COLORS[name] for name in ordered], alpha=0.78, label="RMSE")
    ax.bar([x + width / 2 for x in x_pos], p95_values, width=width, color=[COLORS[name] for name in ordered], alpha=0.38, hatch="//", label="P95")
    for x, value in zip(x_pos, rmse_values):
        ax.text(x - width / 2, value + 0.002, f"{value:.3f}", ha="center", va="bottom", fontsize=8)
    for x, value in zip(x_pos, p95_values):
        ax.text(x + width / 2, value + 0.002, f"{value:.3f}", ha="center", va="bottom", fontsize=8)
    ax.set_title("Resumen de error de posición")
    ax.set_xticks(x_pos, [LABELS[name].replace(" ", "\n") for name in ordered], fontsize=8)
    ax.set_ylabel("m")
    ax.set_ylim(0, max(p95_values) * 1.28)
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(loc="upper left", fontsize=8)

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(COMPARISON_PNG, dpi=180)

    print(json.dumps({"plot": str(COMPARISON_PNG), "metrics": str(COMPARISON_METRICS_JSON), "markdown": str(COMPARISON_MD)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
