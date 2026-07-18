from __future__ import annotations

import base64
import json
import socket
import threading
from contextlib import closing
from pathlib import Path

from core.pipeline import SubscriptionPipeline
from filter.deduplicator import SubscriptionDeduplicator
from generator.subscription_generator import SubscriptionGenerator
from models.results import TestResult
from parser.subscription_parser import SubscriptionParser
from publisher.file_publisher import FilePublisher
from tester.connectivity_tester import ConnectivityTester


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


def test_generator_preserves_raw_vless_query_parameters() -> None:
    text = (
        "vless://uuid@example.com:443?encryption=none&flow=xtls-rprx-vision&security=reality"
        "&sni=example.com&pbk=abcdef&type=tcp&headerType=none#example"
    )
    nodes = SubscriptionParser().parse_text(text).nodes

    encoded = SubscriptionGenerator().generate(nodes)
    decoded = base64.b64decode(encoded).decode("utf-8")

    assert decoded == text


def test_generator_preserves_original_links_for_supported_protocols() -> None:
    vmess_payload = base64.b64encode(
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

    cases = [
        "vless://uuid@example.com:443?security=tls&type=tcp&sni=example.com#example",
        "trojan://password@example.net:8443?sni=example.net#example",
        f"vmess://{vmess_payload}",
        "ss://YWVzLTI1Ni1nY206cGFzc3dvcmQ=@example.org:8388#shadow",
        "socks://user:pass@example.io:1080#example",
    ]

    for text in cases:
        nodes = SubscriptionParser().parse_text(text).nodes
        encoded = SubscriptionGenerator().generate(nodes)
        decoded = base64.b64decode(encoded).decode("utf-8")
        assert decoded == text


def test_parser_parses_ss_link() -> None:
    text = "ss://YWVzLTI1Ni1nY206cGFzc3dvcmQ=@example.org:8388#shadow"
    nodes = SubscriptionParser().parse_text(text).nodes

    assert len(nodes) == 1
    assert nodes[0].protocol == "ss"
    assert nodes[0].host == "example.org"
    assert nodes[0].port == 8388
    assert nodes[0].username == "aes-256-gcm"
    assert nodes[0].password == "password"
    assert nodes[0].remark == "shadow"


def test_generator_serializes_ss_link() -> None:
    text = "ss://YWVzLTI1Ni1nY206cGFzc3dvcmQ=@example.org:8388#shadow"
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


def test_connectivity_tester_marks_live_tcp_endpoint_reachable() -> None:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as server:
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]

        def accept_once() -> None:
            conn, _ = server.accept()
            conn.close()

        thread = threading.Thread(target=accept_once, daemon=True)
        thread.start()

        node = SubscriptionParser().parse_text(f"vless://uuid@127.0.0.1:{port}#live").nodes[0]
        result = ConnectivityTester(timeout_seconds=1.0).test(node)

        assert result.is_reachable is True
        assert result.latency_ms is not None


def test_connectivity_tester_marks_dead_tcp_endpoint_unreachable() -> None:
    node = SubscriptionParser().parse_text("vless://uuid@127.0.0.1:65534#dead").nodes[0]
    result = ConnectivityTester(timeout_seconds=0.1).test(node)

    assert result.is_reachable is False
    assert result.error is not None


def test_pipeline_filters_out_dead_nodes(tmp_path: Path) -> None:
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as server:
        server.bind(("127.0.0.1", 0))
        server.listen(1)
        port = server.getsockname()[1]

        def accept_once() -> None:
            conn, _ = server.accept()
            conn.close()

        thread = threading.Thread(target=accept_once, daemon=True)
        thread.start()

        text = (
            f"vless://uuid@127.0.0.1:{port}#live\n"
            "vless://uuid@127.0.0.1:65534#dead"
        )
        pipeline = SubscriptionPipeline(output_dir=tmp_path)
        result = pipeline.run(text, "subscriptions/default.txt", source="telegram://channel")

        assert len(result.nodes) == 1
        assert "127.0.0.1" in base64.b64decode(result.content).decode("utf-8")


def test_pipeline_prefers_faster_reachable_nodes(tmp_path: Path) -> None:
    class StubTester:
        def test(self, node: object) -> TestResult:
            if node.host == "dead.example.com":
                return TestResult(is_reachable=False, error="down")
            if node.host == "slow.example.com":
                return TestResult(is_reachable=True, latency_ms=120, metadata={"node": node})
            if node.host == "fast.example.com":
                return TestResult(is_reachable=True, latency_ms=20, metadata={"node": node})
            return TestResult(is_reachable=True, latency_ms=50, metadata={"node": node})

    text = (
        "vless://uuid@slow.example.com:443#slow\n"
        "vless://uuid@fast.example.com:443#fast\n"
        "vless://uuid@dead.example.com:443#dead"
    )
    pipeline = SubscriptionPipeline(output_dir=tmp_path, tester=StubTester())

    result = pipeline.run(text, "subscriptions/default.txt", source="telegram://channel")

    assert [node.remark for node in result.nodes] == ["fast", "slow"]
