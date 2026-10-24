"""Storage helper shim."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class Store:
    """Standalone JSON store compatible with HA Store interface."""

    def __init__(self, hass: Any, version: int, key: str, private: bool = True) -> None:
        self.hass = hass
        self.version = version
        self.key = key
        # Determine store directory: prefer /data if available, otherwise /config/.storage
        data_dir = Path("/data")
        if data_dir.is_dir():
            self._path = data_dir / f"{key}.json"
        elif hass and hasattr(hass, "config") and hasattr(hass.config, "config_dir"):
            self._path = Path(hass.config.config_dir) / ".storage" / key
        else:
            self._path = Path(f".storage/{key}.json")

    async def async_load(self) -> dict[str, Any] | None:
        if not self._path.exists():
            return None
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except Exception:
            return None

    async def async_save(self, data: dict[str, Any]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(data, indent=2), encoding="utf-8")
