"""Generate the Phase 1 top-view layout diagram used in the report."""

from __future__ import annotations

from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt

matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['font.sans-serif'] = ['DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False

from matplotlib.lines import Line2D
from matplotlib.patches import Circle, Rectangle


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "actividad2" / "figures" / "phase1" / "phase1_layout_diagram.png"


def add_rect(ax, xy, width, height, color, label, text_xy=None, edge="white") -> None:
    ax.add_patch(Rectangle(xy, width, height, facecolor=color, edgecolor=edge, linewidth=1.7, alpha=0.86))
    tx, ty = text_xy if text_xy else (xy[0] + width / 2, xy[1] + height + 0.10)
    ax.text(tx, ty, label, ha="center", va="bottom", fontsize=10, fontweight="bold", color="#1f1f1f")


def add_marker(ax, xy, color, size, label, offset=(0.0, 0.0)) -> None:
    ax.add_patch(Circle(xy, size, facecolor=color, edgecolor="white", linewidth=1.6, zorder=5))
    ax.text(xy[0] + offset[0], xy[1] + offset[1], label, ha="center", va="center", fontsize=10, fontweight="bold", color="#1f1f1f", zorder=6)


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(9.5, 8.8), constrained_layout=True)
    fig.suptitle("Sim_T2_Phase1_Basic: vista superior de la celda y flujo B1/R1", fontsize=17, fontweight="bold")

    ax.set_facecolor("#edf0f2")
    ax.add_patch(Rectangle((-2.65, -2.55), 5.30, 5.10, fill=False, edgecolor="#25323b", linewidth=2.0))
    ax.add_patch(Rectangle((-2.62, -2.52), 5.24, 5.04, fill=False, edgecolor="#25323b", linewidth=0.8, alpha=0.55))

    add_rect(ax, (-2.60, 1.46), 0.96, 0.58, "#8a5d3e", "Mesa WS1")
    add_rect(ax, (1.64, -2.05), 0.96, 0.58, "#607f5b", "Mesa WS2", text_xy=(2.12, -1.37))
    add_rect(ax, (-1.90, -2.22), 0.88, 0.34, "#4b5961", "Rack T1", text_xy=(-1.46, -1.78))
    add_rect(ax, (1.03, 1.84), 0.88, 0.34, "#4b5961", "Rack T2", text_xy=(1.47, 2.28))
    add_rect(ax, (-0.47, -2.44), 0.74, 0.74, "#176aa6", "C1 carga", text_xy=(-0.42, -1.43))
    add_rect(ax, (-0.91, -1.27), 0.34, 0.42, "#a06431", "Pallet A", text_xy=(-0.74, -0.74))
    add_rect(ax, (-0.32, -0.56), 0.28, 0.28, "#2f363b", "Pilar B", text_xy=(-0.18, -0.18))
    add_rect(ax, (0.33, 0.65), 0.42, 0.34, "#967238", "Caja C", text_xy=(0.54, 1.08))

    route = [
        (-2.12, 1.10),
        (-1.50, 1.10),
        (-1.50, -1.60),
        (-0.40, -1.60),
        (0.80, -1.60),
        (2.12, -1.10),
        (1.50, -1.10),
        (1.50, 1.10),
        (0.70, 1.10),
        (-0.70, 1.10),
        (-2.12, 1.10),
    ]
    xs, ys = zip(*route)
    ax.plot(xs, ys, color="#0b78b6", linewidth=3.0, solid_capstyle="round")
    ax.scatter(xs, ys, s=120, color="#056b9f", edgecolor="white", linewidth=0.9, zorder=4)

    add_marker(ax, (-0.10, -2.05), "#ef542e", 0.16, "R1\nPioneer", offset=(0.46, 0.34))
    add_marker(ax, (-2.12, 1.10), "#1aa36f", 0.13, "B1\nBill", offset=(0.00, -0.28))
    add_marker(ax, (-1.46, -2.01), "#f1b447", 0.08, "T1", offset=(-0.28, 0.34))
    add_marker(ax, (1.46, 1.96), "#5ab2df", 0.08, "T2", offset=(0.35, -0.25))

    ax.annotate("tarea 1: T1 -> B1", xy=(-2.12, 1.10), xytext=(-1.85, -1.25), fontsize=10, color="#b7411d",
                arrowprops={"arrowstyle": "->", "color": "#ef542e", "linewidth": 2.2})
    ax.annotate("tarea 3: T2 -> B1", xy=(2.12, -1.10), xytext=(1.10, 1.35), fontsize=10, color="#0b5f91",
                arrowprops={"arrowstyle": "->", "color": "#4aa0d8", "linewidth": 2.2})

    handles = [
        Line2D([0], [0], color="#0b78b6", lw=3, label="Ruta peatonal de Bill"),
        Line2D([0], [0], marker="o", markersize=9, color="white", markerfacecolor="#ef542e", label="R1 Pioneer"),
        Line2D([0], [0], marker="o", markersize=9, color="white", markerfacecolor="#1aa36f", label="B1 Bill"),
    ]
    ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, -0.12), ncol=3, frameon=True, fontsize=11)

    ax.set_xlim(-2.90, 2.90)
    ax.set_ylim(-2.80, 2.80)
    ax.set_xlabel("x [m]", fontsize=11)
    ax.set_ylabel("y [m]", fontsize=11)
    ax.set_aspect("equal", adjustable="box")
    ax.grid(True, color="white", linewidth=0.65, alpha=0.78)
    fig.savefig(OUT, dpi=180)
    print(OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
