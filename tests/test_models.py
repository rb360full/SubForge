from models.provider import ProviderConfig, ProviderDefinition
from models.proxy import ProxyConfig
from models.results import GenerationResult, TestResult, ValidationResult
from models.subscription import Subscription


def test_proxy_config_model() -> None:
    proxy = ProxyConfig(protocol="vmess", host="example.com", port=443)
    assert proxy.protocol == "vmess"
    assert proxy.host == "example.com"
    assert proxy.port == 443


def test_provider_models() -> None:
    provider = ProviderDefinition(
        name="telegram",
        config=ProviderConfig(type="telegram", enabled=True, source={"channel": "test"}),
    )
    assert provider.name == "telegram"
    assert provider.config.enabled is True


def test_subscription_model() -> None:
    subscription = Subscription(
        name="default",
        enabled=True,
        subscription_name="Telegram-List1",
        format="plain",
        provider="telegram",
        channels=("https://t.me/channel1", "https://t.me/channel2")
    )
    assert subscription.output_path == "Telegram-List1.txt"
    assert subscription.output_path.endswith(".txt")
    assert subscription.provider == "telegram"
    assert len(subscription.channels) == 2


def test_subscription_model_merged_empty_channels() -> None:
    # Test merged subscription with empty channels
    merged = Subscription(
        name="merged",
        enabled=True,
        subscription_name="Telegram-Merged",
        format="plain",
        provider="telegram",
        channels=()  # Empty - should use all unique channels
    )
    assert merged.output_path == "Telegram-Merged.txt"
    assert len(merged.channels) == 0
    assert merged.name == "merged"


def test_result_models() -> None:
    validation = ValidationResult(is_valid=True)
    test_result = TestResult(is_reachable=True, latency_ms=42)
    generation = GenerationResult(success=True, output_path="subscriptions/Telegram-List1.txt")

    assert validation.is_valid is True
    assert test_result.latency_ms == 42
    assert generation.success is True

