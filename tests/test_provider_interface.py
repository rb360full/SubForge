from collections.abc import Iterable

from core.providers import Provider
from models.proxy import ProxyConfig


class DummyProvider(Provider):
    @property
    def name(self) -> str:
        return "dummy"

    def collect(self) -> Iterable[ProxyConfig]:
        return [ProxyConfig(protocol="vmess", host="example.com", port=443)]


def test_provider_interface_contract() -> None:
    provider = DummyProvider()
    results = list(provider.collect())
    assert provider.name == "dummy"
    assert len(results) == 1
    assert results[0].host == "example.com"

