"""Core classes for Home Assistant shim."""
from __future__ import annotations

import asyncio
import inspect
import json
import logging
import os
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Callable

_LOGGER = logging.getLogger(__name__)


def get_supervisor_token() -> str | None:
    """Retrieve Supervisor/Core API token from environment or container files."""
    token = os.environ.get("SUPERVISOR_TOKEN") or os.environ.get("HASSIO_TOKEN")
    if token:
        return token
    for token_path in (
        Path("/run/s6/container_environment/SUPERVISOR_TOKEN"),
        Path("/var/run/s6/container_environment/SUPERVISOR_TOKEN"),
        Path("/run/s6-rc/container_environment/SUPERVISOR_TOKEN"),
        Path("/var/run/s6-rc/container_environment/SUPERVISOR_TOKEN"),
        Path("/run/s6/container_environment/HASSIO_TOKEN"),
        Path("/var/run/s6/container_environment/HASSIO_TOKEN"),
        Path("/etc/s6/container_environment/SUPERVISOR_TOKEN"),
    ):
        if token_path.is_file():
            try:
                t = token_path.read_text(encoding="utf-8").strip()
                if t:
                    return t
            except Exception:
                pass
    return None


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
        """Load entities from .storage/core.restore_state and .storage/core.entity_registry."""
        config_dir = getattr(self.hass.config, "config_dir", "/homeassistant")
        for base in [config_dir, "/homeassistant", "/config"]:
            base_path = Path(base)

            # 1. First load last known runtime states and attributes
            restore_file = base_path / ".storage" / "core.restore_state"
            if restore_file.is_file():
                try:
                    data = json.loads(restore_file.read_text(encoding="utf-8"))
                    items = data.get("data", [])
                    if isinstance(items, list):
                        for item in items:
                            state_obj = item.get("state", {})
                            eid = state_obj.get("entity_id")
                            if eid:
                                st = str(state_obj.get("state", "unknown"))
                                attrs = dict(state_obj.get("attributes", {}))
                                self._states[eid] = State(eid, st, attrs)
                except Exception as e:
                    _LOGGER.debug("Could not read restore_state: %s", e)

            # 2. Merge entity registry definitions (metadata, custom names, icons)
            reg_file = base_path / ".storage" / "core.entity_registry"
            if reg_file.is_file():
                try:
                    data = json.loads(reg_file.read_text(encoding="utf-8"))
                    for ent in data.get("data", {}).get("entities", []):
                        eid = ent.get("entity_id")
                        if not eid:
                            continue
                        name = ent.get("name") or ent.get("original_name") or eid
                        dev_class = ent.get("device_class")
                        icon = ent.get("icon")
                        if eid in self._states:
                            attrs = self._states[eid].attributes
                            if not attrs.get("friendly_name") and name:
                                attrs["friendly_name"] = name
                            if not attrs.get("device_class") and dev_class:
                                attrs["device_class"] = dev_class
                            if not attrs.get("icon") and icon:
                                attrs["icon"] = icon
                        else:
                            attrs = {
                                "friendly_name": name,
                                "device_class": dev_class,
                                "icon": icon,
                            }
                            self._states[eid] = State(eid, "unknown", attrs)
                except Exception as e:
                    _LOGGER.debug("Could not read entity registry: %s", e)

    async def async_update_states(self, force: bool = False) -> None:
        """Fetch live entity states from Supervisor Core API."""
        now = time.monotonic()
        if not force and self._states and (now - self._last_update < 15.0):
            return

        token = get_supervisor_token()
        if token:
            try:
                import aiohttp
                timeout = aiohttp.ClientTimeout(total=5)
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
                        else:
                            _LOGGER.debug("Supervisor states API returned %d", resp.status)
            except Exception as e:
                _LOGGER.debug("Supervisor states fetch failed: %s", e)

        # Fallback to storage if API not available or empty
        if not self._states:
            self._load_from_storage()


class HomeAssistant:
    """Minimal standalone HomeAssistant runtime adapter for Supervisor Add-on."""

    def __init__(self, config_dir: str = "/homeassistant") -> None:
        try:
            self._loop = asyncio.get_running_loop()
        except RuntimeError:
            self._loop = None
        self.config = SimpleNamespace(
            config_dir=config_dir,
            components=set(),
            path=lambda *parts: os.path.join(config_dir, *parts),
        )
        self.data: dict[str, Any] = {}
        self.auth = SimpleNamespace(
            async_get_user=lambda uid: asyncio.sleep(0, result=SimpleNamespace(
                id=uid or "ingress_admin",
                name="Ingress User",
                is_admin=True,
                is_active=True,
            ))
        )
        self.states = StateMachine(self)
        self.bus = SimpleNamespace(
            async_fire=lambda event, data=None: None,
            async_listen=lambda event, cb: lambda: None,
        )
        self.services = SimpleNamespace(
            async_call=self._async_call_service,
        )

    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        """Return the current running event loop, or active fallback loop."""
        try:
            return asyncio.get_running_loop()
        except RuntimeError:
            if self._loop and not self._loop.is_closed():
                return self._loop
            self._loop = asyncio.new_event_loop()
            return self._loop

    @loop.setter
    def loop(self, val: asyncio.AbstractEventLoop) -> None:
        self._loop = val

    def add_job(self, target: Callable, *args: Any) -> Any:
        """Schedule or run a job on the event loop safely from any thread."""
        try:
            loop = self.loop
            if loop.is_running():
                if inspect.iscoroutinefunction(target):
                    return asyncio.run_coroutine_threadsafe(target(*args), loop)
                return loop.call_soon_threadsafe(target, *args)
            else:
                if inspect.iscoroutinefunction(target):
                    return loop.run_until_complete(target(*args))
                return target(*args)
        except Exception as e:
            _LOGGER.debug("Could not schedule job on loop: %s", e)
            try:
                res = target(*args)
                if asyncio.iscoroutine(res):
                    return self.async_create_task(res)
                return res
            except Exception:
                pass

    def async_add_job(self, target: Callable, *args: Any) -> Any:
        """Alias for add_job."""
        return self.add_job(target, *args)

    def async_create_task(self, target: Any) -> asyncio.Task:
        """Create a background task on the running loop."""
        loop = self.loop
        if loop.is_running():
            return loop.create_task(target)
        try:
            cur_loop = asyncio.get_running_loop()
            return cur_loop.create_task(target)
        except RuntimeError:
            return loop.create_task(target)

    async def async_add_executor_job(self, target: Callable, *args: Any) -> Any:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, target, *args)

    async def _async_call_service(
        self,
        domain: str,
        service: str,
        service_data: dict | None = None,
        target: dict | None = None,
        blocking: bool = True,
        return_response: bool = False,
        **kwargs: Any,
    ) -> Any:
        token = get_supervisor_token()
        if token:
            try:
                import aiohttp
                timeout = aiohttp.ClientTimeout(total=10)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                    url = f"http://supervisor/core/api/services/{domain}/{service}"
                    payload = dict(service_data or {})
                    if target:
                        for k, v in target.items():
                            if v:
                                payload[k] = v
                    async with session.post(url, headers=headers, json=payload) as resp:
                        if return_response:
                            return await resp.json()
                        return None
            except Exception as e:
                _LOGGER.warning("Service call to supervisor failed: %s", e)
        return None
