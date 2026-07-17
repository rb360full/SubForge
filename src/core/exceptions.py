"""Custom exception hierarchy for SubForge."""

from __future__ import annotations


class SubForgeError(Exception):
    """Base exception for the project."""


class ConfigurationError(SubForgeError):
    """Raised when configuration loading or validation fails."""


class ProviderError(SubForgeError):
    """Raised when a provider cannot be initialized or used."""


class ValidationError(SubForgeError):
    """Raised when data validation fails."""


class GeneratorError(SubForgeError):
    """Raised when subscription generation fails."""

