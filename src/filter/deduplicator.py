"""Deduplicate normalized subscription nodes."""

from __future__ import annotations

from models.node import SubscriptionNode


class SubscriptionDeduplicator:
    """Remove duplicate nodes while preserving order."""

    def deduplicate(self, nodes: tuple[SubscriptionNode, ...]) -> tuple[SubscriptionNode, ...]:
        seen: set[tuple[object, ...]] = set()
        unique: list[SubscriptionNode] = []
        for node in nodes:
            key = node.identity()
            if key in seen:
                continue
            seen.add(key)
            unique.append(node)
        return tuple(unique)
