"""WebSocket API component shim."""
from __future__ import annotations

from typing import Any, Callable


def async_register_command(hass: Any, command: str, handler: Callable, schema: Any = None) -> None:
    pass
