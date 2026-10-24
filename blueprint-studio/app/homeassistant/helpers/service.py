"""Service helper shim."""
from __future__ import annotations

from typing import Any


async def async_get_all_descriptions(hass: Any) -> dict[str, Any]:
    """Return empty service descriptions fallback."""
    return {}
