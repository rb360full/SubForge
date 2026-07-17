"""Telegram provider backed by Telethon."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Iterable

from telethon import TelegramClient

from models.proxy import ProxyConfig
from parser.subscription_parser import SubscriptionParser


@dataclass(frozen=True, slots=True)
class TelegramProviderConfig:
    """Configuration required to access Telegram."""

    api_id: int
    api_hash: str
    channel: str
    session_name: str = "subforge"
    timeout_seconds: int = 30


class TelegramProvider:
    """Collect Telegram messages from a configured public channel."""

    def __init__(self, config: TelegramProviderConfig) -> None:
        self._config = config
        self._parser = SubscriptionParser()

    def collect(self) -> Iterable[ProxyConfig]:
        return asyncio.run(self._collect_async())

    async def _collect_async(self) -> list[ProxyConfig]:
        client = TelegramClient(self._config.session_name, self._config.api_id, self._config.api_hash)
        results: list[ProxyConfig] = []
        async with client:
            messages = await client.get_messages(self._config.channel, limit=50)
            for message in messages:
                text = getattr(message, "message", "") or ""
                if not text.strip():
                    continue
                parsed = self._parser.parse_text(text, source=self._config.channel)
                for node in parsed.nodes:
                    results.append(
                        ProxyConfig(
                            protocol=node.protocol,
                            host=node.host,
                            port=node.port,
                            name=node.remark,
                            source=node.source,
                            metadata=node.metadata,
                        )
                    )
        return results
