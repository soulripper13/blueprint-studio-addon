"""HTTP component shim."""
from __future__ import annotations

from aiohttp import web


class HomeAssistantView(web.View):
    """Shim for HomeAssistantView."""
    requires_auth = False
    name = ""
    url = ""
