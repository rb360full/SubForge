from __future__ import annotations

from models.node import SubscriptionNode
from runner import (
    filter_nodes_for_subscription,
    normalize_telegram_channel,
    raw_text_from_nodes,
)


def _node(raw: str, source: str) -> SubscriptionNode:
    return SubscriptionNode(
        protocol="vless",
        host="example.com",
        port=443,
        source=source,
        metadata={"raw": raw, "source_channel": source},
    )


def test_normalize_telegram_channel_handles_url_variants() -> None:
    assert normalize_telegram_channel("https://t.me/Capoit") == "capoit"
    assert normalize_telegram_channel("https://t.me/s/Capoit/") == "capoit"
    assert normalize_telegram_channel({"channel": "t.me/Capoit"}) == "capoit"


def test_filter_nodes_for_subscription_uses_channel_sources() -> None:
    nodes = [
        _node("vless://a@example.com:443#a", "https://t.me/PrivateVPNs"),
        _node("vless://b@example.com:443#b", "https://t.me/ConfigsHUB"),
        _node("vless://c@example.com:443#c", "https://t.me/Capoit"),
    ]

    selected = filter_nodes_for_subscription(
        nodes,
        ("https://t.me/PrivateVPNs", "https://t.me/Capoit"),
        {"privatevpns", "configshub", "capoit"},
    )

    assert raw_text_from_nodes(selected) == (
        "vless://a@example.com:443#a\n"
        "vless://c@example.com:443#c"
    )


def test_filter_nodes_for_merged_subscription_uses_all_channels() -> None:
    nodes = [
        _node("vless://a@example.com:443#a", "https://t.me/PrivateVPNs"),
        _node("vless://b@example.com:443#b", "https://t.me/ConfigsHUB"),
    ]

    selected = filter_nodes_for_subscription(nodes, (), {"privatevpns", "configshub"})

    assert raw_text_from_nodes(selected) == (
        "vless://a@example.com:443#a\n"
        "vless://b@example.com:443#b"
    )
