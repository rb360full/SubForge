"""Pipeline result domain models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Validation outcome for a proxy configuration."""

    is_valid: bool
    errors: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class TestResult:
    """Connectivity test outcome for a proxy configuration."""

    __test__ = False

    is_reachable: bool
    latency_ms: int | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class GenerationResult:
    """Subscription generation outcome."""

    success: bool
    output_path: str | None = None
    content: str | None = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
