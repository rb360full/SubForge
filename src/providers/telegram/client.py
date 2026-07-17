"""Telegram provider backed by Telethon."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Iterable, Any

from telethon import TelegramClient
from telethon.sessions import StringSession

from models.proxy import ProxyConfig
from parser.subscription_parser import SubscriptionParser
from datetime import datetime, timedelta


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
    default_thread_fetch_window: int = 200


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
                # Determine days window (per-channel `days` or None)
                days_window = channel_spec.get("days")
                days_window = int(days_window) if isinstance(days_window, int) else None
                kwargs = {"limit": limit}
                if isinstance(message_thread_id, int):
                    kwargs["message_thread_id"] = message_thread_id
                try:
                    messages = await client.get_messages(channel, **kwargs)
                except TypeError:
                    # Some Telethon versions don't accept `message_thread_id`.
                    # Fallback: fetch messages without that kwarg and filter by
                    # the attribute on the returned Message objects.
                    # Telethon doesn't accept `message_thread_id` in this runtime.
                    # Respect the per-channel `limit` (or provider default) so we
                    # never fetch more messages than the user expects. If no
                    # per-channel limit is provided, fall back to a bounded window
                    # configured by `default_thread_fetch_window` to increase the
                    # chance of finding thread messages without going unbounded.
                    if isinstance(message_thread_id, int):
                        fetch_limit = limit
                    else:
                        window = int(getattr(self._config, "default_thread_fetch_window", 200))
                        fetch_limit = min(window, limit)
                    messages = await client.get_messages(channel, limit=fetch_limit)
                    if isinstance(message_thread_id, int):
                        filtered = []
                        for m in messages:
                            if getattr(m, "message_thread_id", None) == message_thread_id:
                                filtered.append(m)
                        messages = filtered
                # If we got a list/iterable, apply date filtering if requested
                filtered_messages = []
                cutoff: datetime | None = None
                if days_window is not None:
                    cutoff = datetime.utcnow() - timedelta(days=days_window)

                for message in messages:
                    # message.date is a datetime in Telethon messages
                    msg_date = getattr(message, "date", None)
                    if cutoff is not None and isinstance(msg_date, datetime):
                        if msg_date.replace(tzinfo=None) < cutoff:
                            continue
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
