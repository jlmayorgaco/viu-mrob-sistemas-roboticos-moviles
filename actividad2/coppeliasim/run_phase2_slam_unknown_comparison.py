"""Run Phase 2 unknown-map scene with each available SLAM mode."""

from __future__ import annotations

import json

from run_phase2_slam_unknown_export import LOG_DIR, run


RUNS = (
    ("GMAPPING_GRID", "gmapping_grid"),
    ("HECTOR_GRID_MATCHING", "hector_grid_matching"),
    ("CARTOGRAPHER_SUBMAP", "cartographer_submap"),
    ("KALMAN_LANDMARK", "kalman_landmark"),
)

COMPARISON_JSON = LOG_DIR / "phase2_slam_unknown_comparison_summary.json"


def main() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, object]] = []

    for algorithm, tag in RUNS:
        csv_path = LOG_DIR / f"phase2_slam_unknown_{tag}.csv"
        summary_json = LOG_DIR / f"phase2_slam_unknown_{tag}_summary.json"
        result = run(algorithm, csv_path, summary_json)
        results.append(result)

    comparison = {
        "runs": results,
        "completed": all(bool(result["completed"]) for result in results),
        "datasets_exported": len(results) == len(RUNS),
        "failed_algorithms": [str(result["requested_slam_algorithm"]) for result in results if not bool(result["completed"])],
        "outputs": {
            "csv": [str(LOG_DIR / f"phase2_slam_unknown_{tag}.csv") for _, tag in RUNS],
            "summary_json": [str(LOG_DIR / f"phase2_slam_unknown_{tag}_summary.json") for _, tag in RUNS],
        },
    }
    COMPARISON_JSON.write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    print(json.dumps(comparison, indent=2))
    return 0 if comparison["datasets_exported"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
