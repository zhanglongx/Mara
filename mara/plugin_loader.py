"""Plugin loading for custom indicators."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Callable

from mara.indicator_registry import IndicatorRegistry


def load_plugins(plugin_dir: Path, registry: IndicatorRegistry) -> list[str]:
    loaded: list[str] = []
    if not plugin_dir.exists():
        return loaded

    plugin_paths: list[Path] = sorted(plugin_dir.glob("*.py"))
    for plugin_path in plugin_paths:
        module: ModuleType | None = _load_module_from_path(plugin_path)
        if module is None:
            continue
        register_func: Callable[[IndicatorRegistry], None] | None = getattr(
            module, "register", None
        )
        if register_func is None:
            continue
        register_func(registry)
        loaded.append(plugin_path.name)

    return loaded


def _load_module_from_path(path: Path) -> ModuleType | None:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
