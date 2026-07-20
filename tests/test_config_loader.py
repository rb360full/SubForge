from pathlib import Path

import pytest

from core.config import AppConfiguration, ConfigurationLoader
from core.exceptions import ConfigurationError


def test_configuration_loader_loads_project_config() -> None:
    loader = ConfigurationLoader(Path("config"))
    config = loader.load()

    assert isinstance(config, AppConfiguration)
    assert config.settings.project_name == "SubForge"
    assert len(config.providers) == 3
    assert len(config.subscriptions) == 3
    telegram_provider = next(provider for provider in config.providers if provider.name == "telegram")
    assert telegram_provider.config.enabled is True
    assert telegram_provider.config.preserve_previous_configs is False
    assert telegram_provider.config.source["channels"] == []
    assert telegram_provider.config.source["default_message_limit"] == 1
    assert config.subscriptions[0].channels == (
        "https://t.me/PrivateVPNs",
        "https://t.me/bored_vpn",
    )
    assert config.subscriptions[2].name == "merged"
    assert config.subscriptions[2].channels == ()


def test_configuration_loader_missing_file(tmp_path: Path) -> None:
    loader = ConfigurationLoader(tmp_path)

    with pytest.raises(ConfigurationError, match="Configuration file not found"):
        loader.load()


def test_configuration_loader_invalid_json(tmp_path: Path) -> None:
    (tmp_path / "settings.json").write_text("{", encoding="utf-8")
    (tmp_path / "providers.json").write_text('{"providers": []}', encoding="utf-8")
    (tmp_path / "subscriptions.json").write_text('{"subscriptions": []}', encoding="utf-8")

    loader = ConfigurationLoader(tmp_path)

    with pytest.raises(ConfigurationError, match="Invalid JSON"):
        loader.load()


def test_configuration_loader_validates_required_keys(tmp_path: Path) -> None:
    (tmp_path / "settings.json").write_text(
        '{"project_name":"SubForge","environment":"development","default_timeout_seconds":30,"output_directory":"subscriptions"}',
        encoding="utf-8",
    )
    (tmp_path / "providers.json").write_text('{"providers": []}', encoding="utf-8")
    (tmp_path / "subscriptions.json").write_text('{"subscriptions": []}', encoding="utf-8")

    loader = ConfigurationLoader(tmp_path)

    with pytest.raises(ConfigurationError, match="Missing required keys"):
        loader.load()
