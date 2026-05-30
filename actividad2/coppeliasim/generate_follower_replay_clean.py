"""Generate follower_replay_clean.png — clean single-mode follower replay figure.

Uses PI mode (best overall score) to show trajectory, reference point and
distance-to-Bill over time.  DejaVu Sans ensures all accented labels render
correctly in every environment.
"""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

import math

ROOT = Path(__file__).resolve().parents[2]
LOG_DIR = ROOT / "actividad2" / "coppeliasim" / "follower_pid_logs"
OUT_FIGURES = ROOT / "actividad2" / "figures" / "phase1" / "follower_replay_clean.png"
OUT_ASSETS  = ROOT / "actividad2" / "slides"   / "assets"   / "follower_replay_clean.png"

MODE = "PI"
D_DES = 0.82


def load(mode: str) -> list[dict]:
    path = LOG_DIR / f"follower_{mode}.csv"
    with path.open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def v(rows: list[dict], col: str) -> list[float]:
    return [float(r[col]) for r in rows]


def ref_point(bx: float, by: float, theta_b: float) -> tuple[float, float]:
    return bx - D_DES * math.cos(theta_b), by - D_DES * math.sin(theta_b)


def main() -> None:
    rows = load(MODE)

    bill_x  = v(rows, "bill_x")
    bill_y  = v(rows, "bill_y")
    pio_x   = v(rows, "pioneer_x")
    pio_y   = v(rows, "pioneer_y")
    ts      = v(rows, "t")
    dist    = v(rows, "distance")
    err     = v(rows, "error")

    # Approximate Bill heading from finite differences
    ref_x, ref_y = [], []
    for i in range(len(rows)):
        if i + 1 < len(rows):
            dx = float(rows[i + 1]["bill_x"]) - float(rows[i]["bill_x"])
            dy = float(rows[i + 1]["bill_y"]) - float(rows[i]["bill_y"])
        else:
            dx, dy = 0.0, 0.0
        th = math.atan2(dy, dx) if (dx or dy) else 0.0
        rx, ry = ref_point(bill_x[i], bill_y[i], th)
        ref_x.append(rx)
        ref_y.append(ry)

    stop_t = next((float(r["t"]) for r in rows if r["bill_state"] == "STOPPED"), None)

    fig, (ax_xy, ax_err) = plt.subplots(
        1, 2, figsize=(13.0, 5.2), gridspec_kw={"width_ratios": [1.1, 1]}
    )
    fig.suptitle(
        "Seguimiento de Bill — modo PI (mejor puntuación ponderada)",
        fontsize=13, fontweight="bold",
    )

    # XY trajectory
    ax_xy.plot(bill_x, bill_y, color="#111111", linewidth=2.4, label="Bill (trayectoria real)")
    ax_xy.plot(ref_x, ref_y, color="#6b7280", linewidth=1.2, linestyle="--", label=f"Referencia $p^*$ ($d_{{des}}={D_DES}$ m)")
    ax_xy.plot(pio_x, pio_y, color="#d19a21", linewidth=1.8, label=f"Pioneer PI (posición estimada)")
    ax_xy.plot(pio_x[0], pio_y[0], "o", color="#217a3f", markersize=7, label="Inicio Pioneer")
    ax_xy.plot(bill_x[0], bill_y[0], "s", color="#111111", markersize=6, label="Inicio Bill")
    ax_xy.set_title("Trayectorias XY")
    ax_xy.set_xlabel("x [m]")
    ax_xy.set_ylabel("y [m]")
    ax_xy.axis("equal")
    ax_xy.grid(True, alpha=0.22)
    ax_xy.legend(fontsize=8, loc="best")

    # Distance / error over time
    ax_err.plot(ts, dist, color="#2f65b0", linewidth=1.8, label="distancia a Bill [m]")
    ax_err.axhline(D_DES, color="#6b7280", linewidth=1.0, linestyle="--", label=f"$d_{{des}}={D_DES}$ m")
    ax_err.plot(ts, err, color="#c9472c", linewidth=1.4, alpha=0.75, label="error de distancia [m]")
    ax_err.axhline(0, color="#111111", linewidth=0.7)
    if stop_t is not None:
        ax_err.axvline(stop_t, color="#333333", linewidth=1.0, linestyle=":", label="Bill se detiene")
    ax_err.set_title("Distancia y error respecto a Bill")
    ax_err.set_xlabel("t [s]")
    ax_err.set_ylabel("distancia / error [m]")
    ax_err.grid(True, alpha=0.22)
    ax_err.legend(fontsize=8, loc="best")

    fig.tight_layout()
    for out in (OUT_FIGURES, OUT_ASSETS):
        out.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out, dpi=180, bbox_inches="tight")
        print(f"Saved: {out}")
    plt.close(fig)


if __name__ == "__main__":
    main()
