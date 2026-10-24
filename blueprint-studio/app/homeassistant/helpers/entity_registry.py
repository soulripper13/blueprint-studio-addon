"""Entity registry helper shim for Supervisor Add-on."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Any

_LOGGER = logging.getLogger(__name__)


class EntityRegistry:
    """Minimal entity registry shim that reads Home Assistant storage."""

    def __init__(self, hass: Any) -> None:
        self.hass = hass
        self.entities: dict[str, SimpleNamespace] = {}
        self._load()

    def _load(self) -> None:
        config_dir = getattr(getattr(self.hass, "config", None), "config_dir", "/homeassistant")
        for base in [config_dir, "/homeassistant", "/config"]:
            reg_file = Path(base) / ".storage" / "core.entity_registry"
            if reg_file.is_file():
                try:
                    data = json.loads(reg_file.read_text(encoding="utf-8"))
                    for ent in data.get("data", {}).get("entities", []):
                        eid = ent.get("entity_id")
                        if eid:
                            self.entities[eid] = SimpleNamespace(
                                entity_id=eid,
                                platform=ent.get("platform"),
                                name=ent.get("name") or ent.get("original_name"),
                                device_id=ent.get("device_id"),
                                area_id=ent.get("area_id"),
                                icon=ent.get("icon"),
                                device_class=ent.get("device_class"),
                            )
                    return
                except Exception as e:
                    _LOGGER.debug("Could not read entity registry: %s", e)

    def async_get(self, entity_id: str) -> SimpleNamespace | None:
        return self.entities.get(entity_id)


def async_get(hass: Any) -> EntityRegistry:
    """Return entity registry instance."""
    return EntityRegistry(hass)
