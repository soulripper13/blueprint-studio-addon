"""Hassio coordinator shim."""
from __future__ import annotations

from typing import Any


def get_addons_list(hass: Any) -> list[dict[str, Any]]:
    """Return empty list fallback for get_addons_list."""
    return []
