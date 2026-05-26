"""Plot the Bill-follower CSV logs for the selected controller set."""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "actividad2" / "coppeliasim" / "follower_pid_logs"
OUTPUT = LOG_DIR / "follower_pid_comparison.png"
OUTPUT_POWER = LOG_DIR / "follower_wheel_power_comparison.png"
OUTPUT_SMOOTHNESS = LOG_DIR / "follower_wheel_command_smoothness.png"
MODES = ("P", "PI", "PID", "LQR", "NMPC")
COLORS = {
    "P": "#c9472c",
    "PI": "#d19a21",
    "PID": "#217a3f",
    "LQR": "#2f65b0",
    "NMPC": "#008a94",
}


def load_rows(mode: str) -> list[dict[str, float | str]]:
    path = LOG_DIR / f"follower_{mode}.csv"
    rows: list[dict[str, float | str]] = []
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            parsed: dict[str, float | str] = {}
            for key, value in row.items():
                if key in {"mode", "follower_state", "bill_state"}:
                    parsed[key] = value
                else:
                    parsed[key] = float(value)
            rows.append(parsed)
    return rows


def values(rows: list[dict[str, float | str]], key: str) -> list[float]:
    return [float(r[key]) for r in rows]


def metrics(rows: list[dict[str, float | str]]) -> dict[str, float]:
    moving = [r for r in rows if float(r["t"]) > 8.0 and r["bill_state"] == "WALKING"]
    stopped = [r for r in rows if r["bill_state"] == "STOPPED"]
    steady = stopped[-250:] if len(stopped) >= 250 else stopped
    moving_abs = [abs(float(r["error"])) for r in moving]
    moving_pos = [float(r["error"]) for r in moving]
    steady_abs = [abs(float(r["error"])) for r in steady]
    du_norm = [
        math.sqrt(float(r["du_left"]) ** 2 + float(r["du_right"]) ** 2)
        for r in rows
        if float(r["t"]) > 1.0
    ]
    u_pairs = [
        (float(r["u_left"]), float(r["u_right"]))
        for r in rows
        if float(r["t"]) > 1.0
    ]
    wheel_u_tv = sum(
        abs(next_left - left) + abs(next_right - right)
        for (left, right), (next_left, next_right) in zip(u_pairs, u_pairs[1:])
    )
    return {
        "mean_abs_moving": sum(moving_abs) / len(moving_abs) if moving_abs else 0.0,
        "far_overshoot": max(moving_pos) if moving_pos else 0.0,
        "close_overshoot": max(0.0, -min(moving_pos)) if moving_pos else 0.0,
        "final_abs": abs(float(rows[-1]["error"])),
        "steady_abs": sum(steady_abs) / len(steady_abs) if steady_abs else 0.0,
        "mean_power": sum(float(r["total_power"]) for r in rows) / len(rows) if rows else 0.0,
        "energy_wh": float(rows[-1]["energy_j"]) / 3600.0 if rows else 0.0,
        "du_rms": math.sqrt(sum(v * v for v in du_norm) / len(du_norm)) if du_norm else 0.0,
        "du_mean": sum(du_norm) / len(du_norm) if du_norm else 0.0,
        "wheel_u_tv": wheel_u_tv,
    }


def paused_intervals(rows: list[dict[str, float | str]]) -> list[tuple[float, float]]:
    intervals: list[tuple[float, float]] = []
    start: float | None = None
    last_t = 0.0
    for row in rows:
        t = float(row["t"])
        if row["bill_state"] == "PAUSED" and start is None:
            start = t
        elif row["bill_state"] != "PAUSED" and start is not None:
            intervals.append((start, last_t))
            start = None
        last_t = t
    if start is not None:
        intervals.append((start, last_t))
    return intervals


def main() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    data = {mode: load_rows(mode) for mode in MODES}
    stats = {mode: metrics(rows) for mode, rows in data.items()}
    pause_windows = paused_intervals(data["P"])

    fig, axes = plt.subplots(2, 2, figsize=(13.5, 8.0))
    fig.suptitle("Actividad 2.1 - Pioneer siguiendo a Bill en circulo: P, PI, PID, LQR y NMPC", fontsize=15, fontweight="bold")

    ax_xy = axes[0, 0]
    first = data["P"]
    ax_xy.plot(values(first, "bill_x"), values(first, "bill_y"), color="#111111", linewidth=2.8, label="Bill")
    for mode, rows in data.items():
        ax_xy.plot(values(rows, "pioneer_x"), values(rows, "pioneer_y"), color=COLORS[mode], linewidth=1.8, label=f"Pioneer {mode}")
    ax_xy.set_title("Trayectorias XY")
    ax_xy.set_xlabel("x [m]")
    ax_xy.set_ylabel("y [m]")
    ax_xy.axis("equal")
    ax_xy.grid(True, alpha=0.25)
    ax_xy.legend(loc="best")

    ax_error = axes[0, 1]
    for idx, (start, end) in enumerate(pause_windows):
        ax_error.axvspan(start, end, color="#6b7280", alpha=0.12, label="pausa" if idx == 0 else None)
    for mode, rows in data.items():
        ax_error.plot(values(rows, "t"), values(rows, "error"), color=COLORS[mode], linewidth=1.7, label=mode)
    stop_times = [float(r["t"]) for r in first if r["bill_state"] == "STOPPED"]
    if stop_times:
        ax_error.axvline(min(stop_times), color="#333333", linestyle="--", linewidth=1.2, label="Bill se detiene")
    ax_error.axhline(0, color="#111111", linewidth=0.9)
    ax_error.set_title("Error de distancia respecto al setpoint")
    ax_error.set_xlabel("t [s]")
    ax_error.set_ylabel("error [m]")
    ax_error.grid(True, alpha=0.25)
    ax_error.legend(loc="best")
    metric_lines = [
        f"{mode}: prom|e|={stats[mode]['mean_abs_moving']:.3f} m, pasa={stats[mode]['close_overshoot']:.3f} m, lejos={stats[mode]['far_overshoot']:.3f} m"
        for mode in MODES
    ]
    ax_error.text(
        0.02,
        0.03,
        "\n".join(metric_lines),
        transform=ax_error.transAxes,
        fontsize=8.0,
        va="bottom",
        ha="left",
        bbox={"boxstyle": "round,pad=0.32", "facecolor": "white", "edgecolor": "#bbbbbb", "alpha": 0.88},
    )

    ax_distance = axes[1, 0]
    for start, end in pause_windows:
        ax_distance.axvspan(start, end, color="#6b7280", alpha=0.10)
    for mode, rows in data.items():
        ax_distance.plot(values(rows, "t"), values(rows, "distance"), color=COLORS[mode], linewidth=1.7, label=mode)
    ax_distance.axhline(0.82, color="#111111", linestyle="--", linewidth=1.1, label="setpoint 0.82 m")
    ax_distance.set_title("Distancia Bill-Pioneer")
    ax_distance.set_xlabel("t [s]")
    ax_distance.set_ylabel("distancia [m]")
    ax_distance.grid(True, alpha=0.25)
    ax_distance.legend(loc="best")

    ax_control = axes[1, 1]
    ax_control.plot(values(first, "t"), values(first, "bill_speed"), color="#111111", linestyle="--", linewidth=1.7, label="v Bill")
    for mode, rows in data.items():
        ax_control.plot(values(rows, "t"), values(rows, "control_v"), color=COLORS[mode], linewidth=1.6, label=f"v {mode}")
    ax_control.set_title("Velocidad de Bill y velocidad lineal comandada")
    ax_control.set_xlabel("t [s]")
    ax_control.set_ylabel("v [m/s]")
    ax_control.grid(True, alpha=0.25)
    ax_control.legend(loc="best")

    fig.tight_layout(rect=(0, 0, 1, 0.96))
    fig.savefig(OUTPUT, dpi=180)

    fig2, axes2 = plt.subplots(2, 2, figsize=(13.5, 8.0))
    fig2.suptitle("Actividad 2.1 - Datos de ruedas y potencia estimada", fontsize=15, fontweight="bold")

    ax_power = axes2[0, 0]
    for start, end in pause_windows:
        ax_power.axvspan(start, end, color="#6b7280", alpha=0.10)
    for mode, rows in data.items():
        ax_power.plot(values(rows, "t"), values(rows, "total_power"), color=COLORS[mode], linewidth=1.35, label=mode)
    ax_power.set_title("Potencia mecánica estimada")
    ax_power.set_xlabel("t [s]")
    ax_power.set_ylabel("P [W]")
    ax_power.grid(True, alpha=0.25)
    ax_power.legend(loc="best")

    ax_energy = axes2[0, 1]
    for mode, rows in data.items():
        ax_energy.plot(values(rows, "t"), [v / 3600.0 for v in values(rows, "energy_j")], color=COLORS[mode], linewidth=1.6, label=mode)
    ax_energy.set_title("Energía acumulada")
    ax_energy.set_xlabel("t [s]")
    ax_energy.set_ylabel("E [Wh]")
    ax_energy.grid(True, alpha=0.25)
    ax_energy.legend(loc="best")

    ax_omega = axes2[1, 0]
    nmpc_rows = data["NMPC"]
    ax_omega.plot(values(nmpc_rows, "t"), values(nmpc_rows, "wheel_left_omega"), color="#1f77b4", linewidth=1.2, label="NMPC rueda izq.")
    ax_omega.plot(values(nmpc_rows, "t"), values(nmpc_rows, "wheel_right_omega"), color="#ff7f0e", linewidth=1.2, label="NMPC rueda der.")
    ax_omega.set_title("Velocidad angular de ruedas - NMPC")
    ax_omega.set_xlabel("t [s]")
    ax_omega.set_ylabel("omega [rad/s]")
    ax_omega.grid(True, alpha=0.25)
    ax_omega.legend(loc="best")

    ax_bar = axes2[1, 1]
    labels = list(MODES)
    mean_power = [stats[mode]["mean_power"] for mode in labels]
    energy_wh = [stats[mode]["energy_wh"] for mode in labels]
    x = range(len(labels))
    ax_bar.bar([i - 0.18 for i in x], mean_power, width=0.36, color=[COLORS[m] for m in labels], alpha=0.78, label="Potencia media [W]")
    ax_bar_2 = ax_bar.twinx()
    ax_bar_2.bar([i + 0.18 for i in x], energy_wh, width=0.36, color=[COLORS[m] for m in labels], alpha=0.35, label="Energía [Wh]")
    ax_bar.set_title("Resumen de esfuerzo por modo")
    ax_bar.set_xticks(list(x), labels)
    ax_bar.set_ylabel("P media [W]")
    ax_bar_2.set_ylabel("E [Wh]")
    ax_bar.grid(True, axis="y", alpha=0.25)
    lines1, labels1 = ax_bar.get_legend_handles_labels()
    lines2, labels2 = ax_bar_2.get_legend_handles_labels()
    ax_bar.legend(lines1 + lines2, labels1 + labels2, loc="best")

    fig2.tight_layout(rect=(0, 0, 1, 0.96))
    fig2.savefig(OUTPUT_POWER, dpi=180)

    fig3, axes3 = plt.subplots(2, 2, figsize=(13.5, 8.0))
    fig3.suptitle("Actividad 2.1 - Suavidad de comandos de rueda u y delta-u", fontsize=15, fontweight="bold")

    ax_u_left = axes3[0, 0]
    for start, end in pause_windows:
        ax_u_left.axvspan(start, end, color="#6b7280", alpha=0.10)
    for mode, rows in data.items():
        ax_u_left.plot(values(rows, "t"), values(rows, "u_left"), color=COLORS[mode], linewidth=1.25, label=mode)
    ax_u_left.set_title("u izquierda: comando rueda izquierda")
    ax_u_left.set_xlabel("t [s]")
    ax_u_left.set_ylabel("u_izq [rad/s]")
    ax_u_left.grid(True, alpha=0.25)
    ax_u_left.legend(loc="best")

    ax_u_right = axes3[0, 1]
    for start, end in pause_windows:
        ax_u_right.axvspan(start, end, color="#6b7280", alpha=0.10)
    for mode, rows in data.items():
        ax_u_right.plot(values(rows, "t"), values(rows, "u_right"), color=COLORS[mode], linewidth=1.25, label=mode)
    ax_u_right.set_title("u derecha: comando rueda derecha")
    ax_u_right.set_xlabel("t [s]")
    ax_u_right.set_ylabel("u_der [rad/s]")
    ax_u_right.grid(True, alpha=0.25)
    ax_u_right.legend(loc="best")

    ax_du = axes3[1, 0]
    for start, end in pause_windows:
        ax_du.axvspan(start, end, color="#6b7280", alpha=0.10)
    for mode, rows in data.items():
        t_values = values(rows, "t")
        du_values = [
            math.sqrt(float(r["du_left"]) ** 2 + float(r["du_right"]) ** 2)
            for r in rows
        ]
        ax_du.plot(t_values, du_values, color=COLORS[mode], linewidth=1.15, label=mode)
    ax_du.set_title("Magnitud de delta-u por paso de control")
    ax_du.set_xlabel("t [s]")
    ax_du.set_ylabel("||delta u|| [rad/s]")
    ax_du.grid(True, alpha=0.25)
    ax_du.legend(loc="best")

    ax_smooth = axes3[1, 1]
    du_rms = [stats[mode]["du_rms"] for mode in labels]
    tracking_error = [stats[mode]["mean_abs_moving"] for mode in labels]
    ax_smooth.bar(
        [i - 0.18 for i in x],
        du_rms,
        width=0.36,
        color=[COLORS[m] for m in labels],
        alpha=0.82,
        label="RMS delta-u [rad/s]",
    )
    ax_smooth_2 = ax_smooth.twinx()
    ax_smooth_2.bar(
        [i + 0.18 for i in x],
        tracking_error,
        width=0.36,
        color=[COLORS[m] for m in labels],
        alpha=0.34,
        label="error medio |e| [m]",
    )
    ax_smooth.set_title("Resumen: suavidad vs error")
    ax_smooth.set_xticks(list(x), labels)
    ax_smooth.set_ylabel("RMS delta-u [rad/s]")
    ax_smooth_2.set_ylabel("error medio |e| [m]")
    ax_smooth.grid(True, axis="y", alpha=0.25)
    lines1, labels1 = ax_smooth.get_legend_handles_labels()
    lines2, labels2 = ax_smooth_2.get_legend_handles_labels()
    ax_smooth.legend(lines1 + lines2, labels1 + labels2, loc="upper right")

    fig3.tight_layout(rect=(0, 0, 1, 0.96))
    fig3.savefig(OUTPUT_SMOOTHNESS, dpi=180)
    print(OUTPUT)
    print(OUTPUT_POWER)
    print(OUTPUT_SMOOTHNESS)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
