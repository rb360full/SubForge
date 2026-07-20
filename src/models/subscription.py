"""Subscription output domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class Subscription:
    """A configured subscription output."""

    name: str
    enabled: bool
    subscription_name: str
    format: str
    provider: str  # Provider name (e.g., "telegram")
    channels: tuple[str, ...] = ()  # Override channels (empty = use provider default)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def output_path(self) -> str:
        """Generate output path from subscription name."""
        return f"{self.subscription_name}.txt"

