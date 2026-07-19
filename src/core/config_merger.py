"""Configuration merge and preservation logic."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.exceptions import ConfigurationError


class ConfigMerger:
    """Handles merging and preserving previous configurations."""

    def __init__(self, storage_dir: Path | str = "config/.previous") -> None:
        """Initialize config merger with a storage directory.
        
        Args:
            storage_dir: Directory where previous configs are stored for merging.
        """
        self._storage_dir = Path(storage_dir)

    def load_previous_configs(self, provider_name: str) -> list[dict[str, Any]]:
        """Load previously saved configurations for a provider.
        
        Args:
            provider_name: Name of the provider.
            
        Returns:
            List of previous configurations, or empty list if none exist.
        """
        config_file = self._storage_dir / f"{provider_name}.json"
        if not config_file.exists():
            return []
        
        try:
            with config_file.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
                if isinstance(data, list):
                    return data
                return [data] if isinstance(data, dict) else []
        except (json.JSONDecodeError, OSError):
            return []

    def save_current_configs(self, provider_name: str, configs: list[dict[str, Any]]) -> None:
        """Save current configurations for future merging.
        
        Args:
            provider_name: Name of the provider.
            configs: List of configurations to save.
        """
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        config_file = self._storage_dir / f"{provider_name}.json"
        
        try:
            with config_file.open("w", encoding="utf-8") as handle:
                json.dump(configs, handle, indent=2, ensure_ascii=False)
        except OSError as exc:
            raise ConfigurationError(f"Unable to save configurations for {provider_name}: {exc}") from exc

    def merge_configs(
        self,
        new_configs: list[dict[str, Any]],
        previous_configs: list[dict[str, Any]],
        preserve: bool = True,
    ) -> list[dict[str, Any]]:
        """Merge new and previous configurations.
        
        When preserve is True:
        - Combines previous configs with new configs
        - Deduplicates based on configuration content
        - All configs (old and new) must pass validation
        
        When preserve is False:
        - Only returns new configs
        
        Args:
            new_configs: New configurations to merge.
            previous_configs: Previous configurations to potentially preserve.
            preserve: Whether to preserve previous configs.
            
        Returns:
            Merged list of configurations.
        """
        if not preserve:
            return new_configs

        # Combine: previous configs + new configs
        # Give priority to new configs by appending them after previous
        combined = previous_configs + new_configs
        
        # Deduplicate while preserving order
        # Use JSON representation for comparison
        seen = set()
        deduplicated = []
        
        for config in combined:
            # Convert to JSON string for comparison (handles nested dicts)
            config_json = json.dumps(config, sort_keys=True, ensure_ascii=False)
            if config_json not in seen:
                seen.add(config_json)
                deduplicated.append(config)
        
        return deduplicated

    def validate_and_merge(
        self,
        provider_name: str,
        new_configs: list[dict[str, Any]],
        preserve: bool = True,
        validator: callable | None = None,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Load previous configs, merge with new ones, validate all, and save.
        
        Args:
            provider_name: Name of the provider.
            new_configs: New configurations to merge.
            preserve: Whether to preserve previous configs.
            validator: Optional validation function that takes a config dict.
                      Raises an exception if validation fails.
            
        Returns:
            Tuple of (merged_configs, validation_errors).
            validation_errors contains configs that failed validation.
        """
        # Load previous configs
        previous_configs = self.load_previous_configs(provider_name)
        
        # Merge
        merged = self.merge_configs(new_configs, previous_configs, preserve=preserve)
        
        # Validate all configs
        valid_configs = []
        invalid_configs = []
        
        for config in merged:
            try:
                if validator:
                    validator(config)
                valid_configs.append(config)
            except Exception as exc:
                invalid_configs.append({
                    "config": config,
                    "error": str(exc),
                })
        
        # Save only valid configs for future merges
        if valid_configs:
            self.save_current_configs(provider_name, valid_configs)
        
        return valid_configs, invalid_configs
