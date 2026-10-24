"""Service helper shim."""
from __future__ import annotations

import json
import logging
import os
from typing import Any

from homeassistant.core import get_supervisor_token

_LOGGER = logging.getLogger(__name__)


async def async_get_all_descriptions(hass: Any) -> dict[str, Any]:
    """Return all service descriptions using Supervisor Core API or fallback."""
    token = get_supervisor_token()
    if token:
        try:
            import aiohttp
            timeout = aiohttp.ClientTimeout(total=4)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                async with session.get("http://supervisor/core/api/services", headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        res: dict[str, Any] = {}
                        if isinstance(data, list):
                            for item in data:
                                dom = item.get("domain")
                                srvs = item.get("services", {})
                                if dom:
                                    res[dom] = srvs
                        elif isinstance(data, dict):
                            res = data
                        return res
        except Exception as e:
            _LOGGER.debug("Failed to fetch services from supervisor API: %s", e)
    return {}
