"""Build a minimal Activity 2 CoppeliaSim scene.

This version intentionally includes only what the official guide asks for:
Pioneer P3DX, potential-field attraction to mannequin/Bill, obstacle
avoidance, and a small robotized cell. It does not include the professional
extensions from the 10/10 scene.
"""

from __future__ import annotations

import json
import math
import os
import sys
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
COPPELIA_DIR = Path(r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu")
BASE_SCENE = ROOT / "actividad2" / "coppeliasim" / "Actividad2_2_Pioneer.ttt"
OUTPUT_SCENE = ROOT / "actividad2" / "coppeliasim" / "Actividad2_Pioneer_basic.ttt"
CONTROLLER = ROOT / "actividad2" / "coppeliasim" / "pioneer_basic_controller.lua"
VALIDATION_JSON = ROOT / "actividad2" / "coppeliasim" / "Actividad2_Pioneer_basic_validation.json"


def load_coppeliasim():
    os.add_dll_directory(str(COPPELIA_DIR))
    sys.path.append(str(COPPELIA_DIR / "programming" / "coppeliaSimClientPython"))
    import builtins

    builtins.coppeliasim_library = str(COPPELIA_DIR / "coppeliaSimHeadless.dll")

    from coppeliasim.lib import appDir, simDeinitialize, simInitialize, simLoop
    import coppeliasim.bridge

    simInitialize(appDir().encode("utf-8"), 0)
    coppeliasim.bridge.load()
    sim = coppeliasim.bridge.require("sim")
    return sim, simLoop, simDeinitialize


def safe_get(sim, path: str) -> int:
    try:
        handle = sim.getObject(path)
    except Exception:
        return -1
    return handle if handle is not None else -1


def all_objects(sim) -> list[int]:
    handles: list[int] = []
    i = 0
    while True:
        handle = sim.getObjects(i, sim.handle_all)
        if handle == -1:
            break
        handles.append(handle)
        i += 1
    return handles


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

    candidates: list[tuple[int, str]] = []
    for handle in all_objects(sim):
        try:
            alias = sim.getObjectAlias(handle, 1)
        except Exception:
            continue
        if alias.startswith(prefixes) or alias in script_aliases:
            candidates.append((handle, alias))

    for handle, _alias in sorted(candidates, key=lambda item: item[1].count("/"), reverse=True):
        try:
            sim.removeObject(handle)
        except Exception:
            pass


def set_color(sim, handle: int, color: Iterable[float]) -> None:
    rgb = list(color)
    try:
        sim.setShapeColor(handle, None, sim.colorcomponent_ambient_diffuse, rgb)
    except Exception:
        sim.setObjectColor(handle, 0, sim.colorcomponent_ambient_diffuse, rgb)


def create_box(
    sim,
    alias: str,
    size: tuple[float, float, float],
    position: tuple[float, float, float],
    color: tuple[float, float, float],
    parent: int,
    *,
    respondable: bool = True,
    detectable: bool = True,
) -> int:
    handle = sim.createPrimitiveShape(sim.primitiveshape_cuboid, list(size), 2)
    sim.setObjectAlias(handle, alias)
    sim.setObjectPosition(handle, list(position))
    set_color(sim, handle, color)
    sim.setObjectInt32Param(handle, sim.shapeintparam_static, 1)
    sim.setObjectInt32Param(handle, sim.shapeintparam_respondable, 1 if respondable else 0)

    special = sim.objectspecialproperty_renderable
    if detectable:
        special += sim.objectspecialproperty_collidable
        special += sim.objectspecialproperty_measurable
        special += sim.objectspecialproperty_detectable_all
    sim.setObjectSpecialProperty(handle, special)
    sim.setObjectParent(handle, parent, True)
    return handle


def create_dummy(sim, alias: str, position: tuple[float, float, float], parent: int, size: float = 0.07) -> int:
    handle = sim.createDummy(size, None)
    sim.setObjectAlias(handle, alias)
    sim.setObjectPosition(handle, list(position))
    sim.setObjectParent(handle, parent, True)
    return handle


def add_basic_robotized_cell(sim) -> int:
    group = sim.createDummy(0.04, None)
    sim.setObjectAlias(group, "A2_Basic_Robotized_Cell")

    create_box(
        sim,
        "A2_Basic_Floor",
        (5.10, 5.10, 0.010),
        (0.0, -0.05, -0.006),
        (0.72, 0.74, 0.76),
        group,
        respondable=False,
        detectable=False,
    )
    create_box(sim, "A2_Basic_SafetyFence_North", (5.00, 0.05, 0.45), (0.0, 2.40, 0.225), (0.05, 0.13, 0.22), group)
    create_box(sim, "A2_Basic_SafetyFence_South", (5.00, 0.05, 0.45), (0.0, -2.50, 0.225), (0.05, 0.13, 0.22), group)
    create_box(sim, "A2_Basic_SafetyFence_West", (0.05, 4.80, 0.45), (-2.50, -0.05, 0.225), (0.05, 0.13, 0.22), group)
    create_box(sim, "A2_Basic_SafetyFence_East", (0.05, 4.80, 0.45), (2.50, -0.05, 0.225), (0.05, 0.13, 0.22), group)

    create_box(sim, "A2_Basic_Conveyor", (1.10, 0.34, 0.24), (0.92, 1.55, 0.12), (0.13, 0.13, 0.14), group)
    create_box(sim, "A2_Basic_WorkTable", (0.78, 0.48, 0.28), (1.18, -0.60, 0.14), (0.42, 0.28, 0.20), group)
    create_box(sim, "A2_Basic_Obstacle_Pallet", (0.36, 0.30, 0.30), (-0.23, -0.76, 0.15), (0.66, 0.42, 0.16), group)
    create_box(sim, "A2_Basic_Obstacle_Box", (0.34, 0.34, 0.26), (0.70, 0.06, 0.13), (0.60, 0.36, 0.18), group)

    create_box(
        sim,
        "A2_Basic_GoalZone",
        (0.78, 0.78, 0.014),
        (1.45, 1.20, 0.007),
        (0.84, 0.70, 0.18),
        group,
        respondable=False,
        detectable=False,
    )
    create_box(
        sim,
        "A2_Basic_MissionReady_Panel",
        (0.66, 0.05, 0.34),
        (-2.08, 2.10, 0.52),
        (0.07, 0.10, 0.13),
        group,
        respondable=False,
        detectable=False,
    )
    create_box(
        sim,
        "A2_Basic_MissionReady_Light",
        (0.14, 0.06, 0.10),
        (-2.08, 2.06, 0.58),
        (0.02, 0.68, 0.18),
        group,
        respondable=False,
        detectable=False,
    )

    create_dummy(sim, "GoalStation", (1.45, 1.20, 0.18), group)
    create_dummy(sim, "mannequin", (1.45, 1.20, 0.28), group, size=0.08)
    return group


def set_initial_layout(sim) -> None:
    pioneer = safe_get(sim, "/PioneerP3DX")
    bill = safe_get(sim, "/Bill")
    plant = safe_get(sim, "/indoorPlant")
    camera = safe_get(sim, "/DefaultCamera")

    if pioneer >= 0:
        sim.setObjectPosition(pioneer, [-1.55, -1.92, 0.1388])
        sim.setObjectOrientation(pioneer, [0.0, 0.0, math.radians(18.0)])
    if bill >= 0:
        sim.setObjectPosition(bill, [1.45, 1.20, 0.0])
        sim.setObjectOrientation(bill, [0.0, 0.0, math.radians(-145.0)])
    if plant >= 0:
        sim.setObjectPosition(plant, [-1.95, 0.92, 0.165])
    if camera >= 0:
        sim.setObjectPosition(camera, [3.05, -4.10, 2.85])
        sim.setObjectOrientation(camera, [math.radians(58), 0.0, math.radians(38)])


def attach_basic_controller(sim, group: int) -> int:
    robot = safe_get(sim, "/PioneerP3DX")
    if robot < 0:
        raise RuntimeError("PioneerP3DX was not found in the base scene")

    script_text = CONTROLLER.read_text(encoding="utf-8")
    script_handle = sim.createScript(sim.scripttype_simulation, script_text, 0, "lua")
    sim.setObjectAlias(script_handle, "Pioneer_Basic_Controller")
    sim.setObjectParent(script_handle, robot, False)

    documentation = """-- VIU SRM Actividad 2 - Basic scene documentation
-- Scope: exactly the official guide.
-- 1. Pioneer P3DX programmed in CoppeliaSim/Lua.
-- 2. Attraction toward mannequin/Bill via potential fields.
-- 3. Obstacle avoidance while advancing to the objective.
-- 4. Basic robotized cell with obstacles, fences, conveyor and missionReady.
-- No fleet, no A*, no battery/HMI extension, no scenario manager.
"""
    doc = sim.createScript(sim.scripttype_passive, documentation, 0, "lua")
    sim.setObjectAlias(doc, "A2_Basic_Delivery_Documentation")
    sim.setObjectParent(doc, group, True)
    return script_handle


def sim_step(sim, sim_loop) -> None:
    if sim.getSimulationState() == sim.simulation_stopped:
        return
    current = sim.getSimulationTime()
    for _ in range(80):
        sim_loop(None, 0)
        if current != sim.getSimulationTime() or sim.getSimulationState() == sim.simulation_stopped:
            break


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
    min_obstacle_seen = math.inf
    max_risk = 0.0
    for _ in range(1600):
        sim_step(sim, sim_loop)
        if sim.getSimulationTime() > 70:
            break
        state = sim.getStringSignal("pioneerState")
        if state:
            states_seen.add(str(state))
        min_obstacle = sim.getFloatSignal("pioneerMinObstacleDistance")
        risk = sim.getFloatSignal("pioneerObstacleRisk")
        if min_obstacle is not None and float(min_obstacle) > 0:
            min_obstacle_seen = min(min_obstacle_seen, float(min_obstacle))
        if risk is not None:
            max_risk = max(max_risk, float(risk))
        if state == "ARRIVED" and sim.getSimulationTime() > 16 and "AVOIDING" in states_seen:
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
            "basic_obstacles_present": safe_get(sim, "/A2_Basic_Obstacle_Pallet") >= 0
            and safe_get(sim, "/A2_Basic_Obstacle_Box") >= 0,
            "robotized_cell_elements_present": safe_get(sim, "/A2_Basic_Conveyor") >= 0
            and safe_get(sim, "/A2_Basic_SafetyFence_North") >= 0
            and safe_get(sim, "/A2_Basic_MissionReady_Panel") >= 0,
            "sensor_suite_active": sensor_count is not None and int(sensor_count) >= 16,
            "potential_field_targeting_active": guide_signal is not None
            and "potential_fields" in str(guide_signal),
            "anti_collision_active": "AVOIDING" in states_seen and max_risk > 0.05,
            "distance_reduced": final_distance < initial_distance,
            "close_to_target": final_distance <= 0.85,
            "arrived": state == "ARRIVED",
            "no_professional_extensions": safe_get(sim, "/VIU_Fleet_Robot_1") < 0
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
