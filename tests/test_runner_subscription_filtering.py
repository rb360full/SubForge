from __future__ import annotations

from models.node import SubscriptionNode
from runner import (
    filter_nodes_for_subscription,
    publish_location_subscriptions,
    normalize_telegram_channel,
    raw_text_from_nodes,
)


def _node(raw: str, source: str, message_index: int | None = None) -> SubscriptionNode:
    metadata: dict[str, object] = {"raw": raw, "source_channel": source}
    if message_index is not None:
        metadata["source_message_index"] = message_index
    return SubscriptionNode(
        protocol="vless",
        host="example.com",
        port=443,
        source=source,
        metadata=metadata,
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


def test_filter_nodes_for_subscription_applies_message_limit() -> None:
    nodes = [
        _node("vless://a@example.com:443#a", "https://t.me/PrivateVPNs", 1),
        _node("vless://b@example.com:443#b", "https://t.me/PrivateVPNs", 2),
        _node("vless://c@example.com:443#c", "https://t.me/PrivateVPNs", 3),
    ]

    selected = filter_nodes_for_subscription(
        nodes,
        ("https://t.me/PrivateVPNs",),
        {"privatevpns"},
        message_limit=2,
    )

    assert raw_text_from_nodes(selected) == (
        "vless://a@example.com:443#a\n"
        "vless://b@example.com:443#b"
    )


def test_publish_location_subscriptions_groups_tested_nodes_by_flag(tmp_path) -> None:
    nodes = [
        SubscriptionNode(
            protocol="vless",
            host="de-one.example.com",
            port=443,
            metadata={
                "raw": "vless://a@de-one.example.com:443#%F0%9F%87%A9%F0%9F%87%AA-a",
                "source_channel": "https://t.me/ConfigsHUB",
            },
        ),
        SubscriptionNode(
            protocol="vless",
            host="de-two.example.com",
            port=443,
            metadata={
                "raw": "vless://b@de-two.example.com:443#🇩🇪-b",
                "source_channel": "https://t.me/ConfigsHUB",
            },
        ),
        SubscriptionNode(
            protocol="vless",
            host="gb-one.example.com",
            port=443,
            metadata={
                "raw": "vless://c@gb-one.example.com:443#🇬🇧-c",
                "source_channel": "https://t.me/ConfigsHUB",
            },
        ),
    ]

    paths = publish_location_subscriptions(tmp_path, nodes)

    assert set(paths) == {"DE", "EN"}
    assert (tmp_path / "subscriptions" / "locations" / "DE.txt").exists()
    assert (tmp_path / "subscriptions" / "locations" / "DE.decoded.txt").read_text(encoding="utf-8") == (
        "vless://a@de-one.example.com:443#%F0%9F%87%A9%F0%9F%87%AA-a\n"
        "vless://b@de-two.example.com:443#🇩🇪-b"
    )
    assert (tmp_path / "subscriptions" / "locations" / "EN.decoded.txt").read_text(encoding="utf-8") == (
        "vless://c@gb-one.example.com:443#🇬🇧-c"
    )


def test_publish_location_subscriptions_uses_metadata_country_code(tmp_path) -> None:
    node = SubscriptionNode(
        protocol="vless",
        host="example.com",
        port=443,
        metadata={
            "raw": "vless://a@example.com:443#plain",
            "country_code": "de",
        },
    )

    paths = publish_location_subscriptions(tmp_path, [node])

    assert set(paths) == {"DE"}
    assert (tmp_path / "subscriptions" / "locations" / "DE.decoded.txt").read_text(encoding="utf-8") == (
        "vless://a@example.com:443#plain"
    )
