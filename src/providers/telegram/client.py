"""Telegram provider backed by Telethon."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Iterable, Any

from telethon import TelegramClient
from telethon.sessions import StringSession

from models.proxy import ProxyConfig
from parser.subscription_parser import SubscriptionParser


@dataclass(frozen=True, slots=True)
class TelegramProviderConfig:
    """Configuration required to access Telegram.

    `channels` is a sequence of channel specs. Each spec can be a mapping with
    keys `channel` (string) and optional `message_thread_id` (int), e.g.
    {"channel": "https://t.me/example", "message_thread_id": 12345}.
    """

    api_id: int
    api_hash: str
    channels: tuple[dict[str, Any], ...]
    session_string: str | None = None
    session_name: str = "subforge"
    timeout_seconds: int = 30
    default_message_limit: int = 50


class TelegramProvider:
    """Collect Telegram messages from a configured public channel."""

    def __init__(self, config: TelegramProviderConfig) -> None:
        self._config = config
        self._parser = SubscriptionParser()

    def collect(self) -> Iterable[ProxyConfig]:
        return asyncio.run(self._collect_async())

    async def _collect_async(self) -> list[ProxyConfig]:
        session = StringSession(self._config.session_string) if self._config.session_string else self._config.session_name
        client = TelegramClient(session, self._config.api_id, self._config.api_hash)
        results: list[ProxyConfig] = []
        async with client:
            for channel_spec in self._config.channels:
                # channel_spec is expected to be a mapping with keys:
                # - "channel": str
                # - "message_thread_id": int | None (optional)
                channel = str(channel_spec.get("channel", "")).strip()
                message_thread_id = channel_spec.get("message_thread_id")
                if not channel:
                    continue
                # Pass message_thread_id if provided; Telethon will use it to fetch
                # messages from a specific forum topic when supported by the API.
                # Determine limit: per-channel override `limit` or provider default
                per_channel_limit = channel_spec.get("limit")
                limit = int(per_channel_limit) if isinstance(per_channel_limit, int) else self._config.default_message_limit
                kwargs = {"limit": limit}
                if isinstance(message_thread_id, int):
                    kwargs["message_thread_id"] = message_thread_id
                try:
                    messages = await client.get_messages(channel, **kwargs)
                except TypeError:
                    # Some Telethon versions don't accept `message_thread_id`.
                    # Fallback: fetch messages without that kwarg and filter by
                    # the attribute on the returned Message objects.
                    # If Telethon doesn't accept message_thread_id, fetch a larger
                    # window when filtering by thread to improve chance of matching.
                    fetch_limit = max(200, limit) if isinstance(message_thread_id, int) else limit
                    messages = await client.get_messages(channel, limit=fetch_limit)
                    if isinstance(message_thread_id, int):
                        filtered = []
                        for m in messages:
                            if getattr(m, "message_thread_id", None) == message_thread_id:
                                filtered.append(m)
                        messages = filtered
                for message in messages:
                    text = getattr(message, "message", "") or ""
                    if not text.strip():
                        continue
                    parsed = self._parser.parse_text(text, source=channel)
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
