"""Plot Phase 1 controller comparison results."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False


ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "actividad2" / "coppeliasim" / "phase1_controller_logs"
SUMMARY_JSON = LOG_DIR / "phase1_controller_summary.json"
OUTPUT_TIMESERIES = LOG_DIR / "phase1_controller_comparison.png"
OUTPUT_METRICS = LOG_DIR / "phase1_controller_metrics.png"
MODES = ("P", "PI", "PID", "LQR", "NMPC")
COLORS = {
    "P": "#c9472c",
    "PI": "#d19a21",
    "PID": "#217a3f",
    "LQR": "#2f65b0",
    "NMPC": "#008a94",
}


def load_rows(mode: str) -> list[dict[str, float | int | str]]:
    path = LOG_DIR / f"phase1_{mode}.csv"
    rows: list[dict[str, float | int | str]] = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            parsed: dict[str, float | int | str] = {}
            for key, value in row.items():
                if key in {"mode", "task_id", "task_state", "motion_mode", "active_tool", "b1_station", "battery_mode"}:
                    parsed[key] = value
                elif key in {"completed_task_count", "task_complete", "charging"}:
                    parsed[key] = int(value)
                else:
                    parsed[key] = float(value)
            rows.append(parsed)
    return rows


def values(rows: list[dict[str, float | int | str]], key: str) -> list[float]:
    return [float(row[key]) for row in rows]


def main() -> int:
    if not SUMMARY_JSON.exists():
        raise FileNotFoundError(SUMMARY_JSON)
    summary = json.loads(SUMMARY_JSON.read_text(encoding="utf-8"))
    stats = {entry["mode"]: entry for entry in summary["modes"]}
    data = {mode: load_rows(mode) for mode in MODES}

    fig, axes = plt.subplots(2, 2, figsize=(13.8, 8.2))
    fig.suptitle("Phase 1 Basic - Comparacion de controladores en la misma secuencia T1/T2", fontsize=15, fontweight="bold")

    ax_xy = axes[0, 0]
    first = data[MODES[0]]
    ax_xy.plot(values(first, "b1_x"), values(first, "b1_y"), color="#111111", linewidth=2.4, label="B1")
    for mode, rows in data.items():
        ax_xy.plot(values(rows, "robot_x"), values(rows, "robot_y"), color=COLORS[mode], linewidth=1.5, label=mode)
    ax_xy.set_title("Trayectorias XY")
    ax_xy.set_xlabel("x [m]")
    ax_xy.set_ylabel("y [m]")
    ax_xy.axis("equal")
    ax_xy.grid(True, alpha=0.25)
    ax_xy.legend(loc="best", fontsize=8)

    ax_progress = axes[0, 1]
    for mode, rows in data.items():
        ax_progress.step(values(rows, "t"), values(rows, "completed_task_count"), where="post", color=COLORS[mode], linewidth=1.7, label=mode)
    ax_progress.set_title("Progreso de tareas completadas")
    ax_progress.set_xlabel("t [s]")
    ax_progress.set_ylabel("tareas completadas")
    ax_progress.set_ylim(-0.1, 4.25)
    ax_progress.grid(True, alpha=0.25)
    ax_progress.legend(loc="best", fontsize=8)

    ax_battery = axes[1, 0]
    for mode, rows in data.items():
        ax_battery.plot(values(rows, "t"), values(rows, "battery"), color=COLORS[mode], linewidth=1.7, label=mode)
    ax_battery.set_title("Bateria")
    ax_battery.set_xlabel("t [s]")
    ax_battery.set_ylabel("bateria [%]")
    ax_battery.grid(True, alpha=0.25)
    ax_battery.legend(loc="best", fontsize=8)

    ax_risk = axes[1, 1]
    for mode, rows in data.items():
        ax_risk.plot(values(rows, "t"), values(rows, "obstacle_risk"), color=COLORS[mode], linewidth=1.5, label=mode)
    ax_risk.set_title("Riesgo de obstaculo")
    ax_risk.set_xlabel("t [s]")
    ax_risk.set_ylabel("riesgo [0-1]")
    ax_risk.grid(True, alpha=0.25)
    ax_risk.legend(loc="best", fontsize=8)

    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(OUTPUT_TIMESERIES, dpi=190)
    plt.close(fig)

    fig, axes = plt.subplots(2, 3, figsize=(14.2, 7.9))
    fig.suptitle("Metricas comparativas - menor es mejor salvo bateria final", fontsize=15, fontweight="bold")
    metric_specs = [
        ("duration_s", "Duracion [s]"),
        ("active_motion_s", "Movimiento activo [s]"),
        ("battery_used_pct", "Bateria usada [%]"),
        ("control_total_variation", "Suavidad: variación total"),
        ("max_obstacle_risk", "Riesgo maximo"),
        ("score", "Score compuesto"),
    ]

    for ax, (key, title) in zip(axes.flat, metric_specs):
        vals = [float(stats[mode][key]) for mode in MODES]
        ax.bar(MODES, vals, color=[COLORS[m] for m in MODES])
        ax.set_title(title)
        ax.tick_params(axis="x", rotation=30)
        ax.grid(True, axis="y", alpha=0.25)
        best_mode = min(MODES, key=lambda m: float(stats[m][key]))
        ax.text(
            0.02,
            0.92,
            f"mejor: {best_mode}",
            transform=ax.transAxes,
            fontsize=9,
            bbox={"boxstyle": "round,pad=0.25", "facecolor": "white", "edgecolor": "#bbbbbb", "alpha": 0.9},
        )

    fig.tight_layout(rect=(0, 0, 1, 0.94))
    fig.savefig(OUTPUT_METRICS, dpi=190)
    plt.close(fig)

    print(json.dumps({"plots": [str(OUTPUT_TIMESERIES), str(OUTPUT_METRICS)], "best_mode": summary.get("best_mode")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
