"""Template helper shim for Home Assistant Supervisor Add-on."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import get_supervisor_token

_LOGGER = logging.getLogger(__name__)


class Template:
    """Template shim providing async_render and render."""

    def __init__(self, template_str: str, hass: Any = None) -> None:
        self.template = str(template_str)
        self.hass = hass

    async def async_render(self, variables: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        """Render template via Supervisor Core API if available, or local Jinja2."""
        token = get_supervisor_token()
        if token:
            try:
                import aiohttp
                timeout = aiohttp.ClientTimeout(total=5)
                async with aiohttp.ClientSession(timeout=timeout) as session:
                    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                    url = "http://supervisor/core/api/template"
                    payload = {"template": self.template}
                    if variables:
                        payload["variables"] = variables
                    async with session.post(url, headers=headers, json=payload) as resp:
                        if resp.status == 200:
                            return await resp.text()
                        else:
                            err_text = await resp.text()
                            raise RuntimeError(f"Template render error ({resp.status}): {err_text}")
            except Exception as e:
                _LOGGER.debug("Supervisor template render error: %s", e)
                if not isinstance(e, (ImportError, OSError)):
                    raise

        # Local Jinja2 fallback
        try:
            import jinja2
            env = jinja2.Environment()
            tmpl = env.from_string(self.template)
            return tmpl.render(variables or {})
        except ImportError:
            # Basic fallback evaluator when jinja2 library is not installed
            import re
            def _eval_expr(m):
                expr = m.group(1).strip()
                try:
                    return str(eval(expr, {"__builtins__": {}}, variables or {}))
                except Exception:
                    return m.group(0)
            return re.sub(r"\{\{\s*(.+?)\s*\}\}", _eval_expr, self.template)
        except Exception as e:
            raise RuntimeError(f"Template rendering error: {e}") from e

    def render(self, variables: dict[str, Any] | None = None, **kwargs: Any) -> Any:
        import asyncio
        try:
            loop = asyncio.get_running_loop()
            return loop.run_until_complete(self.async_render(variables=variables, **kwargs))
        except RuntimeError:
            return asyncio.run(self.async_render(variables=variables, **kwargs))
