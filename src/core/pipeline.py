"""Orchestrate the MVP subscription pipeline."""

from __future__ import annotations

from dataclasses import dataclass, replace
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from filter.deduplicator import SubscriptionDeduplicator
from generator.subscription_generator import SubscriptionGenerator
from models.node import SubscriptionNode
from tester.connectivity_tester import ConnectivityTester
from parser.subscription_parser import SubscriptionParser
from publisher.file_publisher import FilePublisher, PublishedSubscription


@dataclass(frozen=True, slots=True)
class SubscriptionPipelineResult:
    """Result of running the MVP pipeline."""

    nodes: tuple[SubscriptionNode, ...]
    content: str
    published: PublishedSubscription


class SubscriptionPipeline:
    """Parse, normalize, deduplicate, generate, and publish subscriptions."""

    def __init__(
        self,
        output_dir: Path | str,
        parser: SubscriptionParser | None = None,
        deduplicator: SubscriptionDeduplicator | None = None,
        tester: ConnectivityTester | None = None,
        generator: SubscriptionGenerator | None = None,
        publisher: FilePublisher | None = None,
    ) -> None:
        self._parser = parser or SubscriptionParser()
        self._deduplicator = deduplicator or SubscriptionDeduplicator()
        self._tester = tester or ConnectivityTester()
        self._generator = generator or SubscriptionGenerator()
        self._publisher = publisher or FilePublisher(output_dir)

    def run(
        self,
        text: str,
        output_path: str,
        source: str | None = None,
        *,
        skip_tests: bool = False,
        test_workers: int = 32,
        sort_configs: bool = True,
        config_count: int | None = None,
    ) -> SubscriptionPipelineResult:
        parsed = self._parser.parse_text(text, source=source)
        deduplicated = self._deduplicator.deduplicate(parsed.nodes)

        if skip_tests:
            nodes = tuple(deduplicated)
        else:
            with ThreadPoolExecutor(max_workers=test_workers) as ex:
                futures = [ex.submit(self._tester.test, node) for node in deduplicated]
                tested = []
                for node, fut in zip(deduplicated, futures):
                    test_result = fut.result()
                    if not test_result.is_reachable:
                        continue
                    tested.append((self._node_with_test_metadata(node, test_result.metadata), test_result))
                if sort_configs:
                    tested.sort(key=lambda item: (item[1].latency_ms is None, item[1].latency_ms or 0))
                else:
                    tested.sort(
                        key=lambda item: self._message_timestamp(item[0]),
                        reverse=True,
                    )
                if config_count is not None and config_count > 0:
                    tested = self._newest_tested_configs(tested, config_count)
                nodes = tuple(node for node, _ in tested)
        if skip_tests and config_count is not None and config_count > 0:
            nodes = nodes[:config_count]
        content = self._generator.generate(nodes)
        published = self._publisher.publish(output_path, content)
        return SubscriptionPipelineResult(nodes=nodes, content=content, published=published)

    def _node_with_test_metadata(
        self,
        node: SubscriptionNode,
        test_metadata: dict[str, object],
    ) -> SubscriptionNode:
        metadata = dict(node.metadata)
        for key, value in test_metadata.items():
            if key != "node":
                metadata[key] = value
        return replace(node, metadata=metadata)

    def _message_timestamp(self, node: SubscriptionNode) -> float:
        """Return message time for newest-first ordering across channels."""
        value = node.metadata.get("source_message_timestamp")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        return float("-inf")

    def _newest_tested_configs(
        self,
        tested: list[tuple[SubscriptionNode, object]],
        config_count: int,
    ) -> list[tuple[SubscriptionNode, object]]:
        """Select the newest healthy configs before applying output ordering."""
        newest = sorted(tested, key=lambda item: self._message_timestamp(item[0]), reverse=True)
        selected = newest[:config_count]
        if selected and all(self._message_timestamp(node) == float("-inf") for node, _ in selected):
            return tested[:config_count]
        return selected
