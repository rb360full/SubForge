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
    assert len(config.subscriptions) == 1
    telegram_provider = next(provider for provider in config.providers if provider.name == "telegram")
    assert telegram_provider.config.enabled is True
    assert telegram_provider.config.source["channels"] == [
        "https://t.me/iProxyChannel",
        "https://t.me/c/1796213998/108538",
    ]


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
