"""Core classes for Home Assistant shim."""
from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any, Callable


class Context:
    """Context representation."""
    def __init__(self, user_id: str | None = None) -> None:
        self.user_id = user_id
        self.id = "system"


def callback(func: Callable) -> Callable:
    """Pass-through decorator for callbacks."""
    return func


class HomeAssistant:
    """Minimal standalone HomeAssistant runtime adapter for Supervisor Add-on."""

    def __init__(self, config_dir: str = "/config") -> None:
        self.config = SimpleNamespace(
            config_dir=config_dir,
            path=lambda *parts: f"{config_dir}/{'/'.join(parts)}",
        )
        self.data: dict[str, Any] = {}
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
        # In Supervisor Add-on, service calls can be routed to Supervisor Core API if SUPERVISOR_TOKEN is set
        pass
