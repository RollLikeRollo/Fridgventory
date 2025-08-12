import importlib
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional

from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class PluginSpec:
    name: str
    module_path: str
    on_ready: Optional[Callable[[], None]] = None


def discover_plugins() -> List[PluginSpec]:
    base_dir = Path(settings.BASE_DIR) / "plugins"
    if not base_dir.exists():
        return []
    specs: List[PluginSpec] = []
    for pkg in base_dir.rglob("plugin.py"):
        rel = pkg.relative_to(settings.BASE_DIR)
        module_path = str(rel.with_suffix("")).replace("/", ".")
        name = pkg.parent.name
        specs.append(PluginSpec(name=name, module_path=module_path))
    return specs


def initialize_plugins() -> None:
    plugins = discover_plugins()
    if not plugins:
        logger.info("No plugins discovered")
        return
    # Ensure /plugins is importable
    sys.path.insert(0, str(Path(settings.BASE_DIR)))
    for spec in plugins:
        try:
            module = importlib.import_module(spec.module_path)
            on_ready = getattr(module, "on_ready", None)
            if callable(on_ready):
                on_ready()
            logger.info("Initialized plugin: %s", spec.name)
        except Exception as exc:
            logger.exception("Failed to initialize plugin %s: %s", spec.name, exc)


