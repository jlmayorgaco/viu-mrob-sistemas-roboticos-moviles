"""Build the small Activity 2 Pioneer scene used for guide checks."""

from __future__ import annotations

import json
import math
from pathlib import Path

from scene_common import (
    create_box,
    create_dummy,
    load_coppeliasim,
    load_library_model,
    remove_by_alias,
    safe_get,
    sim_step,
)


ROOT = Path(__file__).resolve().parents[2]
BASE_SCENE = ROOT / "actividad2" / "coppeliasim" / "legacy" / "Actividad2_2_Pioneer.ttt"
OUTPUT_SCENE = ROOT / "actividad2" / "coppeliasim" / "Actividad2_Pioneer_basic.ttt"
CONTROLLER = ROOT / "actividad2" / "coppeliasim" / "pioneer_basic_controller.lua"
VALIDATION_JSON = ROOT / "actividad2" / "coppeliasim" / "Actividad2_Pioneer_basic_validation.json"


def remove_previous_basic(sim) -> None:
    prefixes = (
        "/A2_Basic_",
        "/GoalStation",
        "/mannequin",
    )
    script_aliases = (
        "/PioneerP3DX/Script",
        "/PioneerP3DX/Pioneer_Basic_Controller",
        "/PioneerP3DX/Pioneer_Professional_Controller",
    )

    remove_by_alias(sim, prefixes, script_aliases)


def create_basic_sofa(sim, parent: int) -> None:
    x, y = -4.30, 2.20
    fabric = (0.18, 0.30, 0.40)
    cushion = (0.27, 0.42, 0.52)
    seam = (0.08, 0.12, 0.16)

    create_box(sim, "A2_Basic_Sofa_Seat", (0.42, 1.04, 0.16), (x, y, 0.16), cushion, parent)
    create_box(sim, "A2_Basic_Sofa_Back", (0.11, 1.10, 0.42), (x - 0.27, y, 0.35), fabric, parent)
    create_box(sim, "A2_Basic_Sofa_Arm_North", (0.46, 0.11, 0.27), (x - 0.02, y + 0.58, 0.24), fabric, parent)
    create_box(sim, "A2_Basic_Sofa_Arm_South", (0.46, 0.11, 0.27), (x - 0.02, y - 0.58, 0.24), fabric, parent)
    create_box(sim, "A2_Basic_Sofa_Seat_Divider", (0.36, 0.035, 0.018), (x + 0.02, y, 0.25), seam, parent, respondable=False, detectable=False)
    create_box(sim, "A2_Basic_Sofa_Front_Rail", (0.045, 0.94, 0.075), (x + 0.24, y, 0.23), seam, parent)


def add_basic_robotized_cell(sim) -> int:
    group = sim.createDummy(0.04, None)
    sim.setObjectAlias(group, "A2_Basic_Robotized_Cell")

    create_box(
        sim,
        "A2_Basic_Floor",
        (10.20, 10.20, 0.010),
        (0.0, -0.05, -0.006),
        (0.72, 0.74, 0.76),
        group,
        respondable=False,
        detectable=False,
    )
    create_box(sim, "A2_Basic_SafetyFence_North", (10.00, 0.05, 0.45), (0.0, 4.90, 0.225), (0.05, 0.13, 0.22), group)
    create_box(sim, "A2_Basic_SafetyFence_South", (10.00, 0.05, 0.45), (0.0, -5.00, 0.225), (0.05, 0.13, 0.22), group)
    create_box(sim, "A2_Basic_SafetyFence_West", (0.05, 9.80, 0.45), (-5.00, -0.05, 0.225), (0.05, 0.13, 0.22), group)
    create_box(sim, "A2_Basic_SafetyFence_East", (0.05, 9.80, 0.45), (5.00, -0.05, 0.225), (0.05, 0.13, 0.22), group)

    if load_library_model(
        sim,
        "equipment/conveyors/generic conveyor (belt).ttm",
        "A2_Basic_Conveyor",
        (2.80, 3.50, 0.0),
        group,
        scale=0.38,
    ) < 0:
        create_box(sim, "A2_Basic_Conveyor", (1.10, 0.34, 0.24), (2.80, 3.50, 0.12), (0.13, 0.13, 0.14), group)

    if load_library_model(
        sim,
        "furniture/tables/customizable table.ttm",
        "A2_Basic_WorkTable",
        (3.35, -2.10, 0.0),
        group,
        scale=0.55,
    ) < 0:
        create_box(sim, "A2_Basic_WorkTable", (0.78, 0.48, 0.28), (3.35, -2.10, 0.14), (0.42, 0.28, 0.20), group)
    create_basic_sofa(sim, group)
    create_box(sim, "A2_Basic_Obstacle_Pallet", (0.42, 0.36, 0.30), (-1.35, -1.85, 0.15), (0.66, 0.42, 0.16), group)
    create_box(sim, "A2_Basic_Obstacle_Box", (0.38, 0.38, 0.28), (1.00, 0.65, 0.14), (0.60, 0.36, 0.18), group)

    create_box(
        sim,
        "A2_Basic_GoalZone",
        (0.78, 0.78, 0.014),
        (3.40, 2.60, 0.007),
        (0.84, 0.70, 0.18),
        group,
        respondable=False,
        detectable=False,
    )
    create_box(
        sim,
        "A2_Basic_MissionReady_Panel",
        (0.66, 0.05, 0.34),
        (-4.40, 4.55, 0.52),
        (0.07, 0.10, 0.13),
        group,
        respondable=False,
        detectable=False,
    )
    create_box(
        sim,
        "A2_Basic_MissionReady_Light",
        (0.14, 0.06, 0.10),
        (-4.40, 4.51, 0.58),
        (0.02, 0.68, 0.18),
        group,
        respondable=False,
        detectable=False,
    )

    create_dummy(sim, "GoalStation", (3.40, 2.60, 0.18), group)
    create_dummy(sim, "mannequin", (3.40, 2.60, 0.28), group, size=0.08)
    return group


def set_initial_layout(sim) -> None:
    pioneer = safe_get(sim, "/PioneerP3DX")
    bill = safe_get(sim, "/Bill")
    plant = safe_get(sim, "/indoorPlant")
    camera = safe_get(sim, "/DefaultCamera")

    if pioneer >= 0:
        sim.setObjectPosition(pioneer, [-3.85, -4.15, 0.1388])
        sim.setObjectOrientation(pioneer, [0.0, 0.0, math.radians(18.0)])
    if bill >= 0:
        sim.setObjectPosition(bill, [3.40, 2.60, 0.0])
        sim.setObjectOrientation(bill, [0.0, 0.0, math.radians(-145.0)])
    if plant >= 0:
        sim.setObjectPosition(plant, [-4.50, 0.92, 0.165])
    if camera >= 0:
        sim.setObjectPosition(camera, [6.00, -7.00, 4.90])
        sim.setObjectOrientation(camera, [math.radians(60), 0.0, math.radians(40)])


def attach_basic_controller(sim, group: int) -> int:
    robot = safe_get(sim, "/PioneerP3DX")
    if robot < 0:
        raise RuntimeError("PioneerP3DX was not found in the base scene")

    script_text = CONTROLLER.read_text(encoding="utf-8")
    script_handle = sim.createScript(sim.scripttype_simulation, script_text, 0, "lua")
    sim.setObjectAlias(script_handle, "Pioneer_Basic_Controller")
    sim.setObjectParent(script_handle, robot, False)

    documentation = """-- VIU SRM Actividad 2 - escena base
-- Pioneer navega hacia mannequin/Bill con campos potenciales.
-- Obstaculos y mobiliario fuerzan una ruta con evitacion local.
-- Senales: missionReady, pioneerState, pioneerDistanceToTarget.
"""
    doc = sim.createScript(sim.scripttype_passive, documentation, 0, "lua")
    sim.setObjectAlias(doc, "A2_Basic_Delivery_Documentation")
    sim.setObjectParent(doc, group, True)
    return script_handle

def validate_scene(sim, sim_loop) -> dict:
    robot = safe_get(sim, "/PioneerP3DX")
    target = safe_get(sim, "/mannequin")
    if robot < 0 or target < 0:
        raise RuntimeError("Cannot validate without /PioneerP3DX and /mannequin")

    rel = sim.getObjectPosition(target, robot)
    initial_distance = math.hypot(rel[0], rel[1])

    sim.setInt32Signal("missionReady", 1)
    sim.startSimulation()
    states_seen: set[str] = set()
    min_distance_seen = initial_distance
    min_obstacle_seen = math.inf
    max_risk = 0.0
    for _ in range(1600):
        sim_step(sim, sim_loop)
        if sim.getSimulationTime() > 70:
            break
        current_rel = sim.getObjectPosition(target, robot)
        current_distance = math.hypot(current_rel[0], current_rel[1])
        min_distance_seen = min(min_distance_seen, current_distance)
        state = sim.getStringSignal("pioneerState")
        if state:
            states_seen.add(str(state))
        min_obstacle = sim.getFloatSignal("pioneerMinObstacleDistance")
        risk = sim.getFloatSignal("pioneerObstacleRisk")
        if min_obstacle is not None and float(min_obstacle) > 0:
            min_obstacle_seen = min(min_obstacle_seen, float(min_obstacle))
        if risk is not None:
            max_risk = max(max_risk, float(risk))
        if state == "ARRIVED" and sim.getSimulationTime() > 16:
            break

    final_rel = sim.getObjectPosition(target, robot)
    final_distance = math.hypot(final_rel[0], final_rel[1])
    state = sim.getStringSignal("pioneerState")
    sensor_count = sim.getInt32Signal("pioneerSensorCount")
    guide_signal = sim.getStringSignal("basicGuideCompliance")
    min_obstacle = sim.getFloatSignal("pioneerMinObstacleDistance")
    obstacle_risk = sim.getFloatSignal("pioneerObstacleRisk")

    sim.stopSimulation()
    while sim.getSimulationState() != sim.simulation_stopped:
        sim_loop(None, 0)

    if min_obstacle_seen == math.inf:
        min_obstacle_seen = -1.0

    result = {
        "scene": str(OUTPUT_SCENE),
        "initial_distance_m": round(initial_distance, 3),
        "final_distance_m": round(final_distance, 3),
        "min_distance_seen_m": round(min_distance_seen, 3),
        "last_state": state,
        "states_seen": sorted(states_seen),
        "sensor_count": int(sensor_count) if sensor_count is not None else None,
        "min_obstacle_distance_m": round(float(min_obstacle), 3) if min_obstacle is not None else None,
        "min_obstacle_seen_m": round(min_obstacle_seen, 3),
        "obstacle_risk": round(float(obstacle_risk), 3) if obstacle_risk is not None else None,
        "max_obstacle_risk": round(max_risk, 3),
        "basic_guide_compliance": guide_signal,
        "checks": {
            "pioneer_present": robot >= 0,
            "mannequin_present": target >= 0,
            "bill_present": safe_get(sim, "/Bill") >= 0,
            "basic_controller_attached": safe_get(sim, "/PioneerP3DX/Pioneer_Basic_Controller") >= 0,
            "basic_cell_present": safe_get(sim, "/A2_Basic_Robotized_Cell") >= 0,
            "basic_sofa_present": safe_get(sim, "/A2_Basic_Sofa") >= 0
            or (
                safe_get(sim, "/A2_Basic_Sofa_Seat") >= 0
                and safe_get(sim, "/A2_Basic_Sofa_Back") >= 0
            ),
            "basic_obstacles_present": safe_get(sim, "/A2_Basic_Obstacle_Pallet") >= 0
            and safe_get(sim, "/A2_Basic_Obstacle_Box") >= 0,
            "robotized_cell_elements_present": safe_get(sim, "/A2_Basic_Conveyor") >= 0
            and safe_get(sim, "/A2_Basic_SafetyFence_North") >= 0
            and safe_get(sim, "/A2_Basic_MissionReady_Panel") >= 0,
            "sensor_suite_active": sensor_count is not None and int(sensor_count) >= 16,
            "potential_field_targeting_active": guide_signal is not None
            and "potential_fields" in str(guide_signal),
            "anti_collision_active": "AVOIDING" in states_seen or max_risk > 0.05,
            "distance_reduced": min_distance_seen < initial_distance,
            "close_to_target": min_distance_seen <= 0.85,
            "arrived": "ARRIVED" in states_seen,
            "no_legacy_scene_extensions": safe_get(sim, "/VIU_Fleet_Robot_1") < 0
            and safe_get(sim, "/VIU_MultiRobot_AStar_Manager") < 0
            and safe_get(sim, "/VIU_Scenario_Event_Manager") < 0,
        },
    }
    result["passed"] = all(result["checks"].values())
    return result


def main() -> int:
    if not BASE_SCENE.exists():
        raise FileNotFoundError(BASE_SCENE)
    if not CONTROLLER.exists():
        raise FileNotFoundError(CONTROLLER)

    sim, sim_loop, sim_deinitialize = load_coppeliasim()
    try:
        if sim.loadScene(str(BASE_SCENE)) < 0:
            raise RuntimeError(f"Could not load {BASE_SCENE}")
        for _ in range(3):
            sim_loop(None, 0)

        remove_previous_basic(sim)
        set_initial_layout(sim)
        group = add_basic_robotized_cell(sim)
        attach_basic_controller(sim, group)

        sim.saveScene(str(OUTPUT_SCENE))
        validation = validate_scene(sim, sim_loop)
        VALIDATION_JSON.write_text(json.dumps(validation, indent=2), encoding="utf-8")

        if not validation["passed"]:
            print(json.dumps(validation, indent=2))
            return 2
        print(json.dumps(validation, indent=2))
        return 0
    finally:
        sim_deinitialize()


if __name__ == "__main__":
    raise SystemExit(main())
