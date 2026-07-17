"""Provider abstractions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Iterable

from models.proxy import ProxyConfig


class Provider(ABC):
    """Abstract provider interface for all source integrations."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the configured provider name."""

    @abstractmethod
    def collect(self) -> Iterable[ProxyConfig]:
        """Collect raw proxy configurations from the provider."""

