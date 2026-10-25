"""Device automation component shim for Supervisor Add-on."""
from __future__ import annotations

from enum import StrEnum
from typing import Any


class DeviceAutomationType(StrEnum):
    """Device automation types."""
    TRIGGER = "trigger"
    CONDITION = "condition"
    ACTION = "action"


async def async_get_device_automations(
    hass: Any,
    automation_type: DeviceAutomationType,
    device_ids: list[str],
) -> dict[str, list[dict[str, Any]]]:
    """Return device automations for specified devices."""
    return {device_id: [] for device_id in device_ids}
