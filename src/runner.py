"""Executable entry point for the SubForge MVP pipeline."""

from __future__ import annotations

import sys
from pathlib import Path

from core.config import ConfigurationLoader
from core.pipeline import SubscriptionPipeline
from providers.telegram.client import TelegramProvider, TelegramProviderConfig


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

    channel = str(telegram_provider.config.source.get("channel", "")).strip()
    if not channel:
        print("Telegram provider is missing source.channel in config/providers.json")
        return 1

    subscription = next((item for item in config.subscriptions if item.enabled), None)
    if subscription is None:
        print("No enabled subscription found in config/subscriptions.json")
        return 1

    output_dir = Path(config.settings.output_directory)
    api_id = telegram_provider.config.source.get("api_id")
    api_hash = telegram_provider.config.source.get("api_hash")
    if not isinstance(api_id, int) or not isinstance(api_hash, str) or not api_hash.strip():
        print("Telegram provider is missing api_id/api_hash in config/providers.json")
        return 1

    provider = TelegramProvider(
        TelegramProviderConfig(
            api_id=api_id,
            api_hash=api_hash,
            channel=channel,
            timeout_seconds=config.settings.default_timeout_seconds,
        )
    )
    try:
        nodes = list(provider.collect())
    except Exception as exc:  # noqa: BLE001
        print(str(exc))
        return 1

    if not nodes:
        print(f"No proxy links found in channel {channel}")
        return 1

    pipeline = SubscriptionPipeline(output_dir=output_dir)
    collected_text = "\n".join(
        node.metadata.get("raw", "") for node in nodes if isinstance(node.metadata.get("raw"), str)
    )
    result = pipeline.run(collected_text, subscription.output_path, source=channel)

    print(f"Collected {len(nodes)} Telegram proxy links from {channel}")
    print(f"Generated {len(result.nodes)} subscription nodes")
    print(f"Published subscription to {result.published.output_path}")
    print(f"Subscription payload length: {len(result.content)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
