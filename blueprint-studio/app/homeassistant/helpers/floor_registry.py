"""Floor registry helper shim for Supervisor Add-on."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Any

_LOGGER = logging.getLogger(__name__)


class FloorRegistry:
    """Minimal floor registry shim that reads Home Assistant storage."""

    def __init__(self, hass: Any) -> None:
        self.hass = hass
        self.floors: dict[str, SimpleNamespace] = {}
        self._load()

    def _load(self) -> None:
        config_dir = getattr(getattr(self.hass, "config", None), "config_dir", "/homeassistant")
        for base in [config_dir, "/homeassistant", "/config"]:
            reg_file = Path(base) / ".storage" / "core.floor_registry"
            if reg_file.is_file():
                try:
                    data = json.loads(reg_file.read_text(encoding="utf-8"))
                    for item in data.get("data", {}).get("floors", []):
                        fid = item.get("floor_id")
                        if fid:
                            self.floors[fid] = SimpleNamespace(
                                floor_id=fid,
                                id=fid,
                                name=item.get("name") or fid,
                                level=item.get("level"),
                            )
                    return
                except Exception as e:
                    _LOGGER.debug("Could not read floor registry: %s", e)


def async_get(hass: Any) -> FloorRegistry:
    """Return floor registry instance."""
    return FloorRegistry(hass)
