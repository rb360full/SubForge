"""Publish generated subscriptions to disk."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from core.exceptions import GeneratorError


@dataclass(frozen=True, slots=True)
class PublishedSubscription:
    """Information about a written subscription artifact."""

    output_path: Path
    content: str


class FilePublisher:
    """Write generated subscription content to the configured folder."""

    def __init__(self, output_dir: Path | str) -> None:
        self._output_dir = Path(output_dir)

    def publish(self, relative_path: str, content: str) -> PublishedSubscription:
        target = self._output_dir / relative_path
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        except OSError as exc:
            raise GeneratorError(f"Unable to publish subscription to {target}: {exc}") from exc
        return PublishedSubscription(output_path=target, content=content)
