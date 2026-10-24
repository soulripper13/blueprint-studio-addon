"""Label registry helper shim for Supervisor Add-on."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Any

_LOGGER = logging.getLogger(__name__)


class LabelRegistry:
    """Minimal label registry shim that reads Home Assistant storage."""

    def __init__(self, hass: Any) -> None:
        self.hass = hass
        self.labels: dict[str, SimpleNamespace] = {}
        self._load()

    def _load(self) -> None:
        config_dir = getattr(getattr(self.hass, "config", None), "config_dir", "/homeassistant")
        for base in [config_dir, "/homeassistant", "/config"]:
            reg_file = Path(base) / ".storage" / "core.label_registry"
            if reg_file.is_file():
                try:
                    data = json.loads(reg_file.read_text(encoding="utf-8"))
                    for item in data.get("data", {}).get("labels", []):
                        lid = item.get("label_id")
                        if lid:
                            self.labels[lid] = SimpleNamespace(
                                label_id=lid,
                                id=lid,
                                name=item.get("name") or lid,
                                color=item.get("color"),
                                icon=item.get("icon"),
                            )
                    return
                except Exception as e:
                    _LOGGER.debug("Could not read label registry: %s", e)


def async_get(hass: Any) -> LabelRegistry:
    """Return label registry instance."""
    return LabelRegistry(hass)
