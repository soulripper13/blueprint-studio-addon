"""Selector helper shim for Blueprint Studio."""
from __future__ import annotations

from typing import Any


class Selector:
    """Base selector."""
    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self.config = config or {}


class ActionSelector(Selector): pass
class AddonSelector(Selector): pass
class AreaSelector(Selector): pass
class AttributeSelector(Selector): pass
class BooleanSelector(Selector): pass
class ColorRGBSelector(Selector): pass
class ColorTempSelector(Selector): pass
class ConfigEntrySelector(Selector): pass
class ConstantSelector(Selector): pass
class ConversationAgentSelector(Selector): pass
class CountrySelector(Selector): pass
class DateTimeSelector(Selector): pass
class DateSelector(Selector): pass
class DeviceSelector(Selector): pass
class DurationSelector(Selector): pass
class EntitySelector(Selector): pass
class FileSelector(Selector): pass
class FloorSelector(Selector): pass
class IconSelector(Selector): pass
class ImageSelector(Selector): pass
class LabelSelector(Selector): pass
class LanguageSelector(Selector): pass
class LocationSelector(Selector): pass
class MediaSelector(Selector): pass
class NavigationSelector(Selector): pass
class NumberSelector(Selector): pass
class ObjectSelector(Selector): pass
class QrCodeSelector(Selector): pass
class SelectSelector(Selector): pass
class StateSelector(Selector): pass
class TargetSelector(Selector): pass
class TemplateSelector(Selector): pass
class TextSelector(Selector): pass
class ThemeSelector(Selector): pass
class TimeSelector(Selector): pass
class TriggerSelector(Selector): pass


def __getattr__(name: str) -> Any:
    return Selector
