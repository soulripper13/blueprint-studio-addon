"""Selector helper shim."""
from __future__ import annotations

import typing

def __getattr__(name: str) -> typing.Any:
    return object
