"""Internal normalized node model."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class SubscriptionNode:
    """Normalized proxy node used across the MVP pipeline."""

    protocol: str
    host: str
    port: int
    username: str | None = None
    password: str | None = None
    uuid: str | None = None
    security: str | None = None
    network: str | None = None
    sni: str | None = None
    remark: str | None = None
    source: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def identity(self) -> tuple[Any, ...]:
        """Return a stable identity tuple used for deduplication."""

        return (
            self.protocol,
            self.host,
            self.port,
            self.username,
            self.password,
            self.uuid,
            self.security,
            self.network,
            self.sni,
        )
