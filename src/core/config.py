"""Configuration loading and validation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json

from core.exceptions import ConfigurationError
from models.provider import ProviderConfig, ProviderDefinition
from models.subscription import Subscription


@dataclass(frozen=True, slots=True)
class Settings:
    """Global application settings."""

    project_name: str
    environment: str
    log_level: str
    default_timeout_seconds: int
    output_directory: str


@dataclass(frozen=True, slots=True)
class AppConfiguration:
    """Validated application configuration bundle."""

    settings: Settings
    providers: tuple[ProviderDefinition, ...]
    subscriptions: tuple[Subscription, ...]


class ConfigurationLoader:
    """Load and validate configuration files from disk."""

    def __init__(self, config_dir: Path | str) -> None:
        self._config_dir = Path(config_dir)

    def load(self) -> AppConfiguration:
        settings = self._load_settings(self._config_dir / "settings.json")
        providers = self._load_providers(self._config_dir / "providers.json")
        subscriptions = self._load_subscriptions(self._config_dir / "subscriptions.json")
        return AppConfiguration(settings=settings, providers=providers, subscriptions=subscriptions)

    def _load_json(self, path: Path) -> Any:
        if not path.exists():
            raise ConfigurationError(f"Configuration file not found: {path}")
        try:
            with path.open("r", encoding="utf-8") as handle:
                return json.load(handle)
        except json.JSONDecodeError as exc:
            raise ConfigurationError(f"Invalid JSON in configuration file {path}: {exc}") from exc
        except OSError as exc:
            raise ConfigurationError(f"Unable to read configuration file {path}: {exc}") from exc

    def _load_settings(self, path: Path) -> Settings:
        data = self._load_json(path)
        required = ("project_name", "environment", "log_level", "default_timeout_seconds", "output_directory")
        self._ensure_mapping(data, path)
        self._require_keys(data, required, path)
        return Settings(
            project_name=self._require_str(data["project_name"], "project_name", path),
            environment=self._require_str(data["environment"], "environment", path),
            log_level=self._require_str(data["log_level"], "log_level", path),
            default_timeout_seconds=self._require_int(data["default_timeout_seconds"], "default_timeout_seconds", path),
            output_directory=self._require_str(data["output_directory"], "output_directory", path),
        )

    def _load_providers(self, path: Path) -> tuple[ProviderDefinition, ...]:
        data = self._load_json(path)
        self._ensure_mapping(data, path)
        self._require_keys(data, ("providers",), path)
        providers = data["providers"]
        if not isinstance(providers, list):
            raise ConfigurationError(f"Expected 'providers' to be a list in {path}")
        items: list[ProviderDefinition] = []
        for index, item in enumerate(providers):
            self._ensure_mapping(item, path, f"providers[{index}]")
            self._require_keys(item, ("name", "enabled", "type", "source"), path, f"providers[{index}]")
            source = item["source"]
            self._ensure_mapping(source, path, f"providers[{index}].source")
            items.append(
                ProviderDefinition(
                    name=self._require_str(item["name"], f"providers[{index}].name", path),
                    config=ProviderConfig(
                        type=self._require_str(item["type"], f"providers[{index}].type", path),
                        enabled=self._require_bool(item["enabled"], f"providers[{index}].enabled", path),
                        source=dict(source),
                    ),
                )
            )
        return tuple(items)

    def _load_subscriptions(self, path: Path) -> tuple[Subscription, ...]:
        data = self._load_json(path)
        self._ensure_mapping(data, path)
        self._require_keys(data, ("subscriptions",), path)
        subscriptions = data["subscriptions"]
        if not isinstance(subscriptions, list):
            raise ConfigurationError(f"Expected 'subscriptions' to be a list in {path}")
        items: list[Subscription] = []
        for index, item in enumerate(subscriptions):
            self._ensure_mapping(item, path, f"subscriptions[{index}]")
            self._require_keys(item, ("name", "enabled", "output_path", "format"), path, f"subscriptions[{index}]")
            items.append(
                Subscription(
                    name=self._require_str(item["name"], f"subscriptions[{index}].name", path),
                    enabled=self._require_bool(item["enabled"], f"subscriptions[{index}].enabled", path),
                    output_path=self._require_str(item["output_path"], f"subscriptions[{index}].output_path", path),
                    format=self._require_str(item["format"], f"subscriptions[{index}].format", path),
                    metadata={k: v for k, v in item.items() if k not in {"name", "enabled", "output_path", "format"}},
                )
            )
        return tuple(items)

    def _ensure_mapping(self, value: Any, path: Path, location: str | None = None) -> None:
        if not isinstance(value, dict):
            where = f" at {location}" if location else ""
            raise ConfigurationError(f"Expected an object{where} in {path}")

    def _require_keys(self, value: dict[str, Any], keys: tuple[str, ...], path: Path, location: str | None = None) -> None:
        missing = [key for key in keys if key not in value]
        if missing:
            where = f" at {location}" if location else ""
            raise ConfigurationError(f"Missing required keys{where} in {path}: {', '.join(missing)}")

    def _require_str(self, value: Any, location: str, path: Path) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ConfigurationError(f"Expected a non-empty string for {location} in {path}")
        return value

    def _require_int(self, value: Any, location: str, path: Path) -> int:
        if isinstance(value, bool) or not isinstance(value, int):
            raise ConfigurationError(f"Expected an integer for {location} in {path}")
        return value

    def _require_bool(self, value: Any, location: str, path: Path) -> bool:
        if not isinstance(value, bool):
            raise ConfigurationError(f"Expected a boolean for {location} in {path}")
        return value

