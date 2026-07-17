"""Connectivity testing for normalized subscription nodes."""

from __future__ import annotations

import socket
import time
from dataclasses import dataclass

from models.node import SubscriptionNode
from models.results import TestResult


@dataclass(frozen=True, slots=True)
class ConnectivityTester:
    """Test whether a node's host and port are reachable."""

    timeout_seconds: float = 3.0

    def test(self, node: SubscriptionNode) -> TestResult:
        start = time.perf_counter()
        try:
            with socket.create_connection((node.host, node.port), timeout=self.timeout_seconds):
                latency_ms = int((time.perf_counter() - start) * 1000)
                return TestResult(is_reachable=True, latency_ms=latency_ms, metadata={"node": node})
        except OSError as exc:
            return TestResult(
                is_reachable=False,
                error=str(exc),
                metadata={"node": node},
            )
