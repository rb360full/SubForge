"""Executable entry point for the SubForge MVP pipeline."""

from __future__ import annotations

import sys
import os
from pathlib import Path

from core.config import ConfigurationLoader
from core.pipeline import SubscriptionPipeline
from providers.telegram.client import TelegramProvider, TelegramProviderConfig
from tester.connectivity_tester import ConnectivityTester


def main(argv: list[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    config_dir = Path("config")
    loader = ConfigurationLoader(config_dir)
    config = loader.load()

    telegram_provider = next(
        (provider for provider in config.providers if provider.name == "telegram" and provider.config.enabled),
        None,
    )
    if telegram_provider is None:
        print("No enabled Telegram provider found in config/providers.json")
        return 1

    raw_channels = telegram_provider.config.source.get("channels")
    channels: tuple[dict[str, object], ...]
    if isinstance(raw_channels, list):
        # Normalize channel entries to mapping form: {"channel": "...", "message_thread_id": 123}
        def _normalize(entry: object) -> dict[str, object] | None:
            if isinstance(entry, str) and entry.strip():
                return {"channel": entry.strip()}
            if isinstance(entry, dict) and entry.get("channel"):
                return {"channel": str(entry.get("channel", "")).strip(), "message_thread_id": entry.get("message_thread_id")}
            return None

        normalized = tuple(_normalize(item) for item in raw_channels)
        channels = tuple(item for item in normalized if item is not None)
    else:
        fallback_channel = str(telegram_provider.config.source.get("channel", "")).strip()
        channels = ({"channel": fallback_channel},) if fallback_channel else ()

    if not channels:
        print("Telegram provider is missing source.channels in config/providers.json")
        return 1

    subscription = next((item for item in config.subscriptions if item.enabled), None)
    if subscription is None:
        print("No enabled subscription found in config/subscriptions.json")
        return 1

    output_dir = Path(config.settings.output_directory)
    api_id = telegram_provider.config.source.get("api_id")
    api_hash = telegram_provider.config.source.get("api_hash")
    session_string = os.getenv("TELEGRAM_SESSION_STRING")
    if not isinstance(api_id, int) or not isinstance(api_hash, str) or not api_hash.strip():
        print("Telegram provider is missing api_id/api_hash in config/providers.json")
        return 1

    provider = TelegramProvider(
        TelegramProviderConfig(
            api_id=api_id,
            api_hash=api_hash,
            channels=channels,
            session_string=session_string.strip() if isinstance(session_string, str) and session_string.strip() else None,
            timeout_seconds=config.settings.default_timeout_seconds,
            default_message_limit=telegram_provider.config.source.get("default_message_limit", 50),
        )
    )
    try:
        nodes = list(provider.collect())
    except Exception as exc:  # noqa: BLE001
        print(str(exc))
        return 1

    if not nodes:
        print(f"No proxy links found in channels: {', '.join(channels)}")
        return 1

    pipeline = SubscriptionPipeline(
        output_dir=output_dir,
        tester=ConnectivityTester(timeout_seconds=config.settings.default_timeout_seconds),
    )
    collected_text = "\n".join(
        node.metadata.get("raw", "") for node in nodes if isinstance(node.metadata.get("raw"), str)
    )
    result = pipeline.run(collected_text, subscription.output_path, source=channels[0])

    channel_names = ', '.join(str(c.get("channel") if isinstance(c, dict) else c) for c in channels)
    print(f"Collected {len(nodes)} Telegram proxy links from {channel_names}")
    print(f"Generated {len(result.nodes)} subscription nodes")
    print(f"Published subscription to {result.published.output_path}")
    print(f"Subscription payload length: {len(result.content)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
