"""Orchestrate the MVP subscription pipeline."""

from __future__ import annotations

from dataclasses import dataclass
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
    ) -> SubscriptionPipelineResult:
        parsed = self._parser.parse_text(text, source=source)
        deduplicated = self._deduplicator.deduplicate(parsed.nodes)

        if skip_tests:
            nodes = tuple(deduplicated)
        else:
            with ThreadPoolExecutor(max_workers=test_workers) as ex:
                futures = [ex.submit(self._tester.test, node) for node in deduplicated]
                nodes = tuple(node for node, fut in zip(deduplicated, futures) if fut.result().is_reachable)
        content = self._generator.generate(nodes)
        published = self._publisher.publish(output_path, content)
        return SubscriptionPipelineResult(nodes=nodes, content=content, published=published)
