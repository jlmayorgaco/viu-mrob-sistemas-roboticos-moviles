"""Shared CoppeliaSim helpers for Activity 2 scene scripts.

Each scene script keeps its own layout and validation flow. This module only
centralizes repeated calls to the CoppeliaSim API.
"""

from __future__ import annotations

import os
import sys
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable


ROOT = Path(__file__).resolve().parents[2]
COPPELIA_DIR = Path(
    os.environ.get("COPPELIA_DIR", r"C:\Program Files\CoppeliaRobotics\CoppeliaSimEdu")
)
MODEL_DIR = COPPELIA_DIR / "models"


@dataclass
class CoppeliaRuntime:
    sim: object
    sim_loop: Callable[[object | None, int], object]
    deinitialize: Callable[[], object]

    def step(self, max_ticks: int = 80) -> None:
        step_simulation(self.sim, self.sim_loop, max_ticks=max_ticks)

    def close(self) -> None:
        self.deinitialize()


class SceneOps:
    """Convenience wrapper for the CoppeliaSim API calls used in the scenes."""

    def __init__(self, sim) -> None:
        self.sim = sim

    def safe_get(self, path: str) -> int:
        try:
            handle = self.sim.getObject(path)
        except Exception:
            return -1
        return handle if handle is not None else -1

    def all_objects(self) -> list[int]:
        handles: list[int] = []
        index = 0
        while True:
            handle = self.sim.getObjects(index, self.sim.handle_all)
            if handle == -1:
                break
            handles.append(handle)
            index += 1
        return handles

    def set_color(self, handle: int, color: Iterable[float]) -> None:
        rgb = list(color)
        try:
            self.sim.setShapeColor(handle, None, self.sim.colorcomponent_ambient_diffuse, rgb)
        except Exception:
            self.sim.setObjectColor(handle, 0, self.sim.colorcomponent_ambient_diffuse, rgb)

    def create_box(
        self,
        alias: str,
        size: tuple[float, float, float],
        position: tuple[float, float, float],
        color: tuple[float, float, float],
        parent: int,
        *,
        yaw: float = 0.0,
        respondable: bool = True,
        detectable: bool = True,
        orientation: tuple[float, float, float] | None = None,
    ) -> int:
        handle = self.sim.createPrimitiveShape(self.sim.primitiveshape_cuboid, list(size), 2)
        self.sim.setObjectAlias(handle, alias)
        self.sim.setObjectPosition(handle, list(position))
        self.sim.setObjectOrientation(handle, list(orientation) if orientation is not None else [0.0, 0.0, yaw])
        self.set_color(handle, color)
        self.sim.setObjectInt32Param(handle, self.sim.shapeintparam_static, 1)
        self.sim.setObjectInt32Param(handle, self.sim.shapeintparam_respondable, 1 if respondable else 0)
        self.sim.setObjectSpecialProperty(handle, self._special_properties(detectable))
        self.sim.setObjectParent(handle, parent, True)
        return handle

    def create_cylinder(
        self,
        alias: str,
        diameter: float,
        height: float,
        position: tuple[float, float, float],
        color: tuple[float, float, float],
        parent: int,
        *,
        yaw: float = 0.0,
        respondable: bool = True,
        detectable: bool = True,
    ) -> int:
        handle = self.sim.createPrimitiveShape(self.sim.primitiveshape_cylinder, [diameter, diameter, height], 2)
        self.sim.setObjectAlias(handle, alias)
        self.sim.setObjectPosition(handle, list(position))
        self.sim.setObjectOrientation(handle, [0.0, 0.0, yaw])
        self.set_color(handle, color)
        self.sim.setObjectInt32Param(handle, self.sim.shapeintparam_static, 1)
        self.sim.setObjectInt32Param(handle, self.sim.shapeintparam_respondable, 1 if respondable else 0)
        self.sim.setObjectSpecialProperty(handle, self._special_properties(detectable))
        self.sim.setObjectParent(handle, parent, True)
        return handle

    def create_dummy(self, alias: str, position: tuple[float, float, float], parent: int, size: float = 0.06) -> int:
        handle = self.sim.createDummy(size, None)
        self.sim.setObjectAlias(handle, alias)
        self.sim.setObjectPosition(handle, list(position))
        self.sim.setObjectParent(handle, parent, True)
        return handle

    def add_lua_script(self, alias: str, script_path: Path, parent: int, *, threaded: bool = False) -> int:
        script_text = script_path.read_text(encoding="utf-8")
        script_handle = self.sim.createScript(self.sim.scripttype_simulation, script_text, 0, "lua")
        self.sim.setObjectAlias(script_handle, alias)
        self.sim.setObjectParent(script_handle, parent, threaded)
        return script_handle

    def add_passive_script(self, alias: str, script_text: str, parent: int) -> int:
        script_handle = self.sim.createScript(self.sim.scripttype_passive, script_text, 0, "lua")
        self.sim.setObjectAlias(script_handle, alias)
        self.sim.setObjectParent(script_handle, parent, True)
        return script_handle

    def remove_by_alias(
        self,
        prefixes: tuple[str, ...],
        aliases: set[str] | tuple[str, ...] = (),
        contains: tuple[str, ...] = (),
    ) -> None:
        explicit_aliases = set(aliases)
        candidates: list[tuple[int, str]] = []
        for handle in self.all_objects():
            try:
                alias = self.sim.getObjectAlias(handle, 1)
            except Exception:
                continue
            if alias.startswith(prefixes) or alias in explicit_aliases or any(part in alias for part in contains):
                candidates.append((handle, alias))

        for handle, _alias in sorted(candidates, key=lambda item: item[1].count("/"), reverse=True):
            try:
                self.sim.removeObject(handle)
            except Exception:
                pass

    def _special_properties(self, detectable: bool) -> int:
        special = self.sim.objectspecialproperty_renderable
        if detectable:
            special += self.sim.objectspecialproperty_collidable
            special += self.sim.objectspecialproperty_measurable
            special += self.sim.objectspecialproperty_detectable_all
        return special


class SignalReader:
    def __init__(self, sim) -> None:
        self.sim = sim

    def string(self, name: str, default: str = "") -> str:
        value = self.sim.getStringSignal(name)
        return str(value) if value is not None else default

    def float(self, name: str, default: float = 0.0) -> float:
        value = self.sim.getFloatSignal(name)
        return float(value) if value is not None else default

    def int(self, name: str, default: int = 0) -> int:
        value = self.sim.getInt32Signal(name)
        return int(value) if value is not None else default


def load_coppeliasim():
    os.add_dll_directory(str(COPPELIA_DIR))
    client_dir = COPPELIA_DIR / "programming" / "coppeliaSimClientPython"
    if str(client_dir) not in sys.path:
        sys.path.append(str(client_dir))

    import builtins

    builtins.coppeliasim_library = str(COPPELIA_DIR / "coppeliaSimHeadless.dll")

    from coppeliasim.lib import appDir, simDeinitialize, simInitialize, simLoop
    import coppeliasim.bridge

    simInitialize(appDir().encode("utf-8"), 0)
    coppeliasim.bridge.load()
    sim = coppeliasim.bridge.require("sim")
    return sim, simLoop, simDeinitialize


def open_coppeliasim() -> CoppeliaRuntime:
    sim, sim_loop, deinitialize = load_coppeliasim()
    return CoppeliaRuntime(sim=sim, sim_loop=sim_loop, deinitialize=deinitialize)


def step_simulation(sim, sim_loop, *, max_ticks: int = 80) -> None:
    if sim.getSimulationState() == sim.simulation_stopped:
        return
    current = sim.getSimulationTime()
    for _ in range(max_ticks):
        sim_loop(None, 0)
        if current != sim.getSimulationTime() or sim.getSimulationState() == sim.simulation_stopped:
            break


def safe_get(sim, path: str) -> int:
    return SceneOps(sim).safe_get(path)


def all_objects(sim) -> list[int]:
    return SceneOps(sim).all_objects()


def remove_by_alias(
    sim,
    prefixes: tuple[str, ...],
    aliases: set[str] | tuple[str, ...] = (),
    *,
    contains: tuple[str, ...] = (),
) -> None:
    SceneOps(sim).remove_by_alias(prefixes, aliases, contains)


def set_color(sim, handle: int, color: Iterable[float]) -> None:
    SceneOps(sim).set_color(handle, color)


def create_box(
    sim,
    alias: str,
    size: tuple[float, float, float],
    position: tuple[float, float, float],
    color: tuple[float, float, float],
    parent: int,
    *,
    yaw: float = 0.0,
    respondable: bool = True,
    detectable: bool = True,
    orientation: tuple[float, float, float] | None = None,
) -> int:
    return SceneOps(sim).create_box(
        alias,
        size,
        position,
        color,
        parent,
        yaw=yaw,
        respondable=respondable,
        detectable=detectable,
        orientation=orientation,
    )


def create_cylinder(
    sim,
    alias: str,
    diameter: float,
    height: float,
    position: tuple[float, float, float],
    color: tuple[float, float, float],
    parent: int,
    *,
    yaw: float = 0.0,
    respondable: bool = True,
    detectable: bool = True,
) -> int:
    return SceneOps(sim).create_cylinder(
        alias,
        diameter,
        height,
        position,
        color,
        parent,
        yaw=yaw,
        respondable=respondable,
        detectable=detectable,
    )


def create_dummy(sim, alias: str, position: tuple[float, float, float], parent: int, size: float = 0.06) -> int:
    return SceneOps(sim).create_dummy(alias, position, parent, size=size)


def create_path_segment(
    sim,
    alias: str,
    start: tuple[float, float],
    end: tuple[float, float],
    parent: int,
    color: tuple[float, float, float],
    *,
    z: float = 0.012,
    width: float = 0.045,
    thickness: float = 0.012,
) -> int:
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = math.hypot(dx, dy)
    yaw = math.atan2(dy, dx)
    mid = ((start[0] + end[0]) * 0.5, (start[1] + end[1]) * 0.5, z)
    return create_box(
        sim,
        alias,
        (length, width, thickness),
        mid,
        color,
        parent,
        yaw=yaw,
        respondable=False,
        detectable=False,
    )


def load_library_model(
    sim,
    relative_path: str,
    alias: str,
    position: tuple[float, float, float],
    parent: int,
    *,
    yaw: float = 0.0,
    scale: float = 1.0,
    visual_only: bool = True,
    align_bottom: bool = True,
) -> int:
    model_path = MODEL_DIR / relative_path
    if not model_path.exists():
        return -1

    try:
        handle = sim.loadModel(str(model_path))
    except Exception:
        return -1
    if handle is None or handle < 0:
        return -1

    if scale != 1.0:
        try:
            sim.scaleModel(handle, scale)
        except Exception:
            try:
                sim.scaleObject(handle, scale, scale, scale, 0)
            except Exception:
                pass

    sim.setObjectAlias(handle, alias)
    sim.setObjectPosition(handle, list(position))
    sim.setObjectOrientation(handle, [0.0, 0.0, yaw])
    sim.setObjectParent(handle, parent, True)
    if align_bottom:
        align_model_bottom_to_z(sim, handle, position[2])
    if visual_only:
        set_model_visual_only(sim, handle)
    return handle


def align_model_bottom_to_z(sim, root: int, z_floor: float) -> None:
    try:
        min_z = sim.getObjectFloatParam(root, sim.objfloatparam_modelbbox_min_z)
        pos = sim.getObjectPosition(root, -1)
        pos[2] = pos[2] + (z_floor - min_z)
        sim.setObjectPosition(root, -1, pos)
    except Exception:
        try:
            min_z = sim.getObjectFloatParam(root, sim.objfloatparam_modelbbox_min_z)
            pos = sim.getObjectPosition(root)
            pos[2] = pos[2] + (z_floor - min_z)
            sim.setObjectPosition(root, pos)
        except Exception:
            pass


def set_model_visual_only(sim, root: int) -> None:
    scripts_to_remove: list[int] = []
    for handle in SceneOps(sim).all_objects():
        if handle != root and not _is_descendant(sim, handle, root):
            continue
        try:
            object_type = sim.getObjectType(handle)
            if object_type == sim.object_script_type:
                scripts_to_remove.append(handle)
                continue
            if object_type != sim.object_shape_type:
                continue
            sim.setObjectInt32Param(handle, sim.shapeintparam_static, 1)
            sim.setObjectInt32Param(handle, sim.shapeintparam_respondable, 0)
            sim.setObjectSpecialProperty(handle, sim.objectspecialproperty_renderable)
        except Exception:
            pass
    for handle in scripts_to_remove:
        try:
            sim.removeObjects([handle])
        except Exception:
            try:
                sim.removeObject(handle)
            except Exception:
                pass


def _is_descendant(sim, handle: int, root: int) -> bool:
    try:
        parent = sim.getObjectParent(handle)
        while parent is not None and parent >= 0:
            if parent == root:
                return True
            parent = sim.getObjectParent(parent)
    except Exception:
        return False
    return False


def sim_step(sim, sim_loop) -> None:
    step_simulation(sim, sim_loop)


def read_string_signal(sim, name: str, default: str = "") -> str:
    return SignalReader(sim).string(name, default)


def read_float_signal(sim, name: str, default: float = 0.0) -> float:
    return SignalReader(sim).float(name, default)


def read_int_signal(sim, name: str, default: int = 0) -> int:
    return SignalReader(sim).int(name, default)


def world_pose(sim, handle: int) -> tuple[float, float, float]:
    if handle < 0:
        return (math.nan, math.nan, math.nan)
    try:
        position = sim.getObjectPosition(handle, -1)
        orientation = sim.getObjectOrientation(handle, -1)
    except Exception:
        return (math.nan, math.nan, math.nan)
    return (float(position[0]), float(position[1]), float(orientation[2]))


def world_xy(sim, handle: int) -> tuple[float, float]:
    x, y, _theta = world_pose(sim, handle)
    return (x, y)


def positive(values: Iterable[float]) -> list[float]:
    return [value for value in values if math.isfinite(value) and value > 0]
