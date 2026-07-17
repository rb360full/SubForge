from __future__ import annotations

import base64
import json
from pathlib import Path

from core.pipeline import SubscriptionPipeline
from filter.deduplicator import SubscriptionDeduplicator
from generator.subscription_generator import SubscriptionGenerator
from parser.subscription_parser import SubscriptionParser
from publisher.file_publisher import FilePublisher


def test_parser_extracts_supported_links() -> None:
    payload = base64.b64encode(
        json.dumps(
            {
                "v": "2",
                "ps": "Example",
                "add": "vmess.example.com",
                "port": "443",
                "id": "11111111-1111-1111-1111-111111111111",
                "aid": "0",
                "scy": "auto",
                "net": "ws",
                "type": "none",
                "host": "",
                "path": "",
                "tls": "tls",
                "sni": "vmess.example.com",
            }
        ).encode("utf-8")
    ).decode("ascii")
    text = f"""
    hello world
    vmess://{payload}
    vless://uuid@example.com:443?security=tls&type=tcp#example
    trojan://password@example.net:8443?sni=example.net
    ss://YWVzLTI1Ni1nY206cGFzc3dvcmQ=@example.org:8388#shadow
    socks://user:pass@example.io:1080
    """

    parsed = SubscriptionParser().parse_text(text, source="telegram://channel")

    assert len(parsed.nodes) == 5
    assert parsed.nodes[0].protocol == "vmess"
    assert parsed.nodes[1].protocol == "vless"
    assert parsed.nodes[2].protocol == "trojan"
    assert parsed.nodes[3].protocol == "ss"
    assert parsed.nodes[4].protocol == "socks"


def test_deduplicator_removes_duplicates_preserving_order() -> None:
    parser = SubscriptionParser()
    text = "vless://uuid@example.com:443#one\nvless://uuid@example.com:443#one"
    nodes = parser.parse_text(text).nodes

    unique = SubscriptionDeduplicator().deduplicate(nodes)

    assert len(unique) == 1


def test_generator_preserves_original_links_when_available() -> None:
    text = "vless://uuid@example.com:443#example"
    nodes = SubscriptionParser().parse_text(text).nodes

    encoded = SubscriptionGenerator().generate(nodes)
    decoded = base64.b64decode(encoded).decode("utf-8")

    assert decoded == text


def test_pipeline_publishes_subscription_file(tmp_path: Path) -> None:
    text = "vless://uuid@example.com:443#example\nvless://uuid@example.com:443#example"
    pipeline = SubscriptionPipeline(output_dir=tmp_path)

    result = pipeline.run(text, "subscriptions/default.txt", source="telegram://channel")

    assert len(result.nodes) == 1
    assert result.published.output_path == tmp_path / "subscriptions/default.txt"
    assert result.published.output_path.exists()
    assert base64.b64decode(result.content).decode("utf-8") == "vless://uuid@example.com:443#example"
