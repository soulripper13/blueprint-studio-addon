"""aiohttp_client helper shim."""
from __future__ import annotations

import aiohttp
from typing import Any

_session: aiohttp.ClientSession | None = None


def async_get_clientsession(hass: Any = None) -> aiohttp.ClientSession:
    """Return shared aiohttp ClientSession."""
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession()
    return _session
