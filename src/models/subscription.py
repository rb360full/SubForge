"""Subscription output domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Subscription:
    """A configured subscription output."""

    name: str
    enabled: bool
    output_path: str
    format: str
    metadata: dict[str, Any] = field(default_factory=dict)

