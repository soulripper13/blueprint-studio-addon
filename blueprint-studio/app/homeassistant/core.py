"""Core classes for Home Assistant shim."""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

_LOGGER = logging.getLogger(__name__)


class Context:
    """Context representation."""
    def __init__(self, user_id: str | None = None) -> None:
        self.user_id = user_id
        self.id = "system"


def callback(func: Callable) -> Callable:
    """Pass-through decorator for callbacks."""
    return func


class State:
    """Home Assistant State representation."""
    def __init__(self, entity_id: str, state: str = "unknown", attributes: dict | None = None) -> None:
        self.entity_id = entity_id
        self.state = str(state)
        self.attributes = attributes or {}
        self.domain = entity_id.partition(".")[0]

    def __repr__(self) -> str:
        return f"<State {self.entity_id}={self.state}>"


class StateMachine:
    """State machine representation supporting live Supervisor API and storage fallbacks."""
    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self._states: dict[str, State] = {}
        self._last_update: float = 0.0

    def get(self, entity_id: str) -> State | None:
        if not self._states:
            self._load_from_storage()
        return self._states.get(entity_id)

    def async_all(self, domain: str | None = None) -> list[State]:
        if not self._states:
            self._load_from_storage()
        states = list(self._states.values())
        if domain:
            return [s for s in states if s.domain == domain]
        return states

    def _load_from_storage(self) -> None:
        """Load entities from .storage/core.entity_registry."""
        config_dir = getattr(self.hass.config, "config_dir", "/homeassistant")
        for base in [config_dir, "/homeassistant", "/config"]:
            reg_file = Path(base) / ".storage" / "core.entity_registry"
            if reg_file.is_file():
                try:
                    data = json.loads(reg_file.read_text(encoding="utf-8"))
                    for ent in data.get("data", {}).get("entities", []):
                        eid = ent.get("entity_id")
                        if eid and eid not in self._states:
                            name = ent.get("name") or ent.get("original_name") or eid
                            attrs = {
                                "friendly_name": name,
                                "device_class": ent.get("device_class"),
                                "icon": ent.get("icon"),
                            }
                            self._states[eid] = State(eid, "unknown", attrs)
                    return
                except Exception as e:
                    _LOGGER.debug("Could not read entity registry: %s", e)

    async def async_update_states(self, force: bool = False) -> None:
        """Fetch live entity states from Supervisor Core API."""
        now = time.monotonic()
        if not force and self._states and (now - self._last_update < 30.0):
            return

        token = os.environ.get("SUPERVISOR_TOKEN") or os.environ.get("HASSIO_TOKEN")
        if token:
            try:
                import aiohttp
                timeout = aiohttp.ClientTimeout(total=4)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                    async with session.get("http://supervisor/core/api/states", headers=headers) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            new_states: dict[str, State] = {}
                            for item in data:
                                eid = item.get("entity_id")
                                if eid:
                                    new_states[eid] = State(
                                        eid,
                                        item.get("state", "unknown"),
                                        item.get("attributes", {}),
                                    )
                            self._states = new_states
                            self._last_update = now
                            return
            except Exception as e:
                _LOGGER.debug("Supervisor states fetch failed: %s", e)

        # Fallback to storage if API not available
        self._load_from_storage()


class HomeAssistant:
    """Minimal standalone HomeAssistant runtime adapter for Supervisor Add-on."""

    def __init__(self, config_dir: str = "/homeassistant") -> None:
        self.config = SimpleNamespace(
            config_dir=config_dir,
            path=lambda *parts: os.path.join(config_dir, *parts),
        )
        self.data: dict[str, Any] = {}
        self.states = StateMachine(self)
        self.bus = SimpleNamespace(
            async_fire=lambda event, data=None: None,
            async_listen=lambda event, cb: lambda: None,
        )
        self.services = SimpleNamespace(
            async_call=self._async_call_service,
        )

    async def async_add_executor_job(self, target: Callable, *args: Any) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, target, *args)

    async def _async_call_service(self, domain: str, service: str, service_data: dict | None = None) -> None:
        token = os.environ.get("SUPERVISOR_TOKEN") or os.environ.get("HASSIO_TOKEN")
        if token:
            try:
                import aiohttp
                timeout = aiohttp.ClientTimeout(total=5)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                    url = f"http://supervisor/core/api/services/{domain}/{service}"
                    await session.post(url, headers=headers, json=service_data or {})
            except Exception as e:
                _LOGGER.warning("Service call to supervisor failed: %s", e)
