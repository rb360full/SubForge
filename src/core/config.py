"""Configuration loading and validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, TypeVar

from core.exceptions import ConfigurationError
from models.provider import ProviderConfig, ProviderDefinition
from models.subscription import Subscription

T = TypeVar("T")


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
        return self._load_items(
            path,
            "providers",
            ("name", "enabled", "type", "source"),
            lambda item, index: self._build_provider_definition(item, index, path),
        )

    def _build_provider_definition(self, item: dict[str, Any], index: int, path: Path) -> ProviderDefinition:
        source_data = self._require_mapping(item["source"], path, f"providers[{index}].source")
        
        # Extract preserve_previous_configs from source
        preserve_previous_configs = source_data.get("preserve_previous_configs", False)
        if not isinstance(preserve_previous_configs, bool):
            raise ConfigurationError(
                f"Expected a boolean for preserve_previous_configs in providers[{index}].source in {path}"
            )
        
        # Create a copy of source without the preserve_previous_configs key
        filtered_source = {k: v for k, v in source_data.items() if k != "preserve_previous_configs"}
        
        return ProviderDefinition(
            name=self._require_str(item["name"], f"providers[{index}].name", path),
            config=ProviderConfig(
                type=self._require_str(item["type"], f"providers[{index}].type", path),
                enabled=self._require_bool(item["enabled"], f"providers[{index}].enabled", path),
                source=filtered_source,
                preserve_previous_configs=preserve_previous_configs,
            ),
        )

    def _load_subscriptions(self, path: Path) -> tuple[Subscription, ...]:
        return self._load_items(
            path,
            "subscriptions",
            ("name", "enabled", "subscription_name", "format", "provider"),
            lambda item, index: Subscription(
                name=self._require_str(item["name"], f"subscriptions[{index}].name", path),
                enabled=self._require_bool(item["enabled"], f"subscriptions[{index}].enabled", path),
                subscription_name=self._require_str(item["subscription_name"], f"subscriptions[{index}].subscription_name", path),
                format=self._require_str(item["format"], f"subscriptions[{index}].format", path),
                provider=self._require_str(item["provider"], f"subscriptions[{index}].provider", path),
                channels=tuple(item.get("channels", [])) if isinstance(item.get("channels"), list) else (),
                metadata={
                    k: v
                    for k, v in item.items()
                    if k not in {"name", "enabled", "subscription_name", "format", "provider", "channels"}
                },
            ),
        )

    def _load_items(
        self,
        path: Path,
        collection_key: str,
        required_keys: tuple[str, ...],
        builder: Callable[[dict[str, Any], int], T],
    ) -> tuple[T, ...]:
        data = self._load_json(path)
        self._ensure_mapping(data, path)
        self._require_keys(data, (collection_key,), path)
        collection = data[collection_key]
        if not isinstance(collection, list):
            raise ConfigurationError(f"Expected '{collection_key}' to be a list in {path}")
        items: list[T] = []
        for index, item in enumerate(collection):
            self._ensure_mapping(item, path, f"{collection_key}[{index}]")
            self._require_keys(item, required_keys, path, f"{collection_key}[{index}]")
            items.append(builder(item, index))
        return tuple(items)

    def _ensure_mapping(self, value: Any, path: Path, location: str | None = None) -> None:
        if not isinstance(value, dict):
            where = f" at {location}" if location else ""
            raise ConfigurationError(f"Expected an object{where} in {path}")

    def _require_keys(
        self,
        value: dict[str, Any],
        keys: tuple[str, ...],
        path: Path,
        location: str | None = None,
    ) -> None:
        missing = [key for key in keys if key not in value]
        if missing:
            where = f" at {location}" if location else ""
            raise ConfigurationError(f"Missing required keys{where} in {path}: {', '.join(missing)}")

    def _require_mapping(self, value: Any, path: Path, location: str) -> dict[str, Any]:
        self._ensure_mapping(value, path, location)
        return value

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
