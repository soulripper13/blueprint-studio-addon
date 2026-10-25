"""Device registry helper shim for Supervisor Add-on."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from types import SimpleNamespace
from typing import Any

_LOGGER = logging.getLogger(__name__)


class DeviceRegistry:
    """Minimal device registry shim that reads Home Assistant storage."""

    def __init__(self, hass: Any) -> None:
        self.hass = hass
        self.devices: dict[str, SimpleNamespace] = {}
        self._load()

    def _load(self) -> None:
        config_dir = getattr(getattr(self.hass, "config", None), "config_dir", "/homeassistant")
        for base in [config_dir, "/homeassistant", "/config"]:
            reg_file = Path(base) / ".storage" / "core.device_registry"
            if reg_file.is_file():
                try:
                    data = json.loads(reg_file.read_text(encoding="utf-8"))
                    for dev in data.get("data", {}).get("devices", []):
                        did = dev.get("id")
                        if did:
                            self.devices[did] = SimpleNamespace(
                                id=did,
                                name=dev.get("name") or did,
                                name_by_user=dev.get("name_by_user"),
                                manufacturer=dev.get("manufacturer"),
                                model=dev.get("model"),
                                area_id=dev.get("area_id"),
                                identifiers=dev.get("identifiers") or [],
                                connections=dev.get("connections") or [],
                            )
                    return
                except Exception as e:
                    _LOGGER.debug("Could not read device registry: %s", e)

    def async_get(self, device_id: str) -> SimpleNamespace | None:
        return self.devices.get(device_id)


def async_get(hass: Any) -> DeviceRegistry:
    """Return device registry instance."""
    return DeviceRegistry(hass)
