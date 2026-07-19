"""Provider configuration domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    """Runtime configuration for a provider definition."""

    type: str
    enabled: bool
    source: dict[str, Any] = field(default_factory=dict)
    preserve_previous_configs: bool = field(default=False)


@dataclass(frozen=True, slots=True)
class ProviderDefinition:
    """Configured provider entry."""

    name: str
    config: ProviderConfig

