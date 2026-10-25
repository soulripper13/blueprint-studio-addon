"""Conversation component shim for Supervisor Add-on."""
from __future__ import annotations

import logging
from types import SimpleNamespace
from typing import Any

from homeassistant.core import Context, HomeAssistant

_LOGGER = logging.getLogger(__name__)


async def async_converse(
    hass: HomeAssistant,
    text: str,
    conversation_id: str | None = None,
    context: Context | None = None,
    agent_id: str | None = None,
) -> SimpleNamespace:
    """Send converse request via Home Assistant service call."""
    payload = {"text": text}
    if agent_id:
        payload["agent_id"] = agent_id
    if conversation_id:
        payload["conversation_id"] = conversation_id

    try:
        result = await hass.services.async_call(
            "conversation",
            "process",
            service_data=payload,
            return_response=True,
        )
        if isinstance(result, dict) and "response" in result:
            speech = (
                result.get("response", {})
                .get("speech", {})
                .get("plain", {})
                .get("speech", "")
            )
            return SimpleNamespace(
                response=SimpleNamespace(speech={"plain": {"speech": speech}})
            )
    except Exception as e:
        _LOGGER.debug("async_converse via service call failed: %s", e)

    return SimpleNamespace(response=SimpleNamespace(speech={"plain": {"speech": ""}}))
