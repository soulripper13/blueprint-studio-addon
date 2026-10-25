"""Area registry helper shim for Supervisor Add-on."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Any

_LOGGER = logging.getLogger(__name__)


class AreaRegistry:
    """Minimal area registry shim that reads Home Assistant storage."""

    def __init__(self, hass: Any) -> None:
        self.hass = hass
        self.areas: dict[str, SimpleNamespace] = {}
        self._load()

    def _load(self) -> None:
        config_dir = getattr(getattr(self.hass, "config", None), "config_dir", "/homeassistant")
        for base in [config_dir, "/homeassistant", "/config"]:
            reg_file = Path(base) / ".storage" / "core.area_registry"
            if reg_file.is_file():
                try:
                    data = json.loads(reg_file.read_text(encoding="utf-8"))
                    for item in data.get("data", {}).get("areas", []):
                        aid = item.get("id")
                        if aid:
                            self.areas[aid] = SimpleNamespace(
                                id=aid,
                                area_id=aid,
                                name=item.get("name") or aid,
                                picture=item.get("picture"),
                                floor_id=item.get("floor_id"),
                            )
                    return
                except Exception as e:
                    _LOGGER.debug("Could not read area registry: %s", e)

    def async_get(self, area_id: str) -> SimpleNamespace | None:
        return self.areas.get(area_id)


def async_get(hass: Any) -> AreaRegistry:
    """Return area registry instance."""
    return AreaRegistry(hass)
