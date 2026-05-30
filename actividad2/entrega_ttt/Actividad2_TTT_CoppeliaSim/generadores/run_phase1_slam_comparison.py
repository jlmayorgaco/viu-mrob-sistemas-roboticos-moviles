"""Run Phase 1 Basic repeatedly and export comparable SLAM datasets.

The scene uses compact CoppeliaSim variants of the four mapping approaches.
Each run receives the same proximity-ray readings, task sequence, robot, and
controller so the exported metrics are comparable.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

from run_phase1_slam_export import LOG_DIR, run


RUNS = (
    ("GMAPPING_GRID", "gmapping_grid"),
    ("HECTOR_GRID_MATCHING", "hector_grid_matching"),
    ("CARTOGRAPHER_SUBMAP", "cartographer_submap"),
    ("KALMAN_LANDMARK", "kalman_landmark"),
)

COMPARISON_JSON = LOG_DIR / "phase1_slam_comparison_summary.json"


def main() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []

    for algorithm, tag in RUNS:
        csv_path = LOG_DIR / f"phase1_slam_{tag}.csv"
        summary_json = LOG_DIR / f"phase1_slam_{tag}_summary.json"
        result = run(algorithm, csv_path, summary_json)
        results.append(result)

    comparison = {
        "runs": results,
        "completed": all(bool(result["completed"]) for result in results),
        "outputs": {
            "csv": [str(LOG_DIR / f"phase1_slam_{tag}.csv") for _, tag in RUNS],
            "summary_json": [str(LOG_DIR / f"phase1_slam_{tag}_summary.json") for _, tag in RUNS],
        },
        "meta": {
            "run_date": datetime.now().isoformat(timespec="seconds"),
            "python": sys.version.split()[0],
            "n_runs_per_algorithm": 1,
        },
    }
    COMPARISON_JSON.write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    print(json.dumps(comparison, indent=2))
    return 0 if comparison["completed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
