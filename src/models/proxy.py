"""Proxy configuration domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ProxyConfig:
    """Normalized proxy configuration passed through the pipeline."""

    protocol: str
    host: str
    port: int
    name: str | None = None
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

