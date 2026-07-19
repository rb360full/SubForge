"""Executable entry point for the SubForge MVP pipeline."""

from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path

from core.config import ConfigurationLoader
from core.config_merger import ConfigMerger
from core.node_serializer import dicts_to_nodes, nodes_to_dicts
from core.pipeline import SubscriptionPipeline
from providers.telegram.client import TelegramProvider, TelegramProviderConfig
from tester.connectivity_tester import ConnectivityTester


def resolve_telegram_session_config(
    env_value: str | None = None,
    session_file: Path | None = None,
) -> tuple[str | None, str]:
    """Resolve Telegram auth input from the environment or a local session file."""
    resolved_value = env_value if env_value is not None else os.getenv("TELEGRAM_SESSION_STRING")
    if isinstance(resolved_value, str) and resolved_value.strip():
        return resolved_value.strip(), "environment"

    candidate = session_file or Path("subforge.session")
    if candidate.exists():
        return None, "subforge"

    return None, "subforge"


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

    # Handle config preservation and merging
    config_merger = ConfigMerger(Path("config") / ".previous")
    preserve_configs = telegram_provider.config.preserve_previous_configs
    
    raw_channels = telegram_provider.config.source.get("channels")
    channels: tuple[dict[str, object], ...]
    if isinstance(raw_channels, list):
        # Normalize channel entries to mapping form: {"channel": "...", "message_thread_id": 123}
        def _normalize(entry: object) -> dict[str, object] | None:
            if isinstance(entry, str) and entry.strip():
                return {"channel": entry.strip()}
            if isinstance(entry, dict) and entry.get("channel"):
                # Preserve optional per-channel keys like message_thread_id and limit
                return {
                    "channel": str(entry.get("channel", "")).strip(),
                    "message_thread_id": entry.get("message_thread_id"),
                    "limit": entry.get("limit"),
                    "days": entry.get("days"),
                }
            return None

        normalized_channels = [item for item in (_normalize(item) for item in raw_channels) if item is not None]
        
        # Merge with previous configs if preserve is enabled
        if preserve_configs:
            # Validate channel format: must have "channel" key with non-empty value
            def validate_channel(config: dict[str, object]) -> None:
                if not isinstance(config.get("channel"), str) or not str(config.get("channel", "")).strip():
                    raise ValueError(f"Invalid channel format: missing or empty 'channel' field in {config}")
            
            merged_channels, invalid = config_merger.validate_and_merge(
                provider_name="telegram_channels",
                new_configs=normalized_channels,
                preserve=True,
                validator=validate_channel,
            )
            
            if invalid:
                print(f"WARNING: {len(invalid)} channel configs failed validation and were skipped:")
                for item in invalid:
                    print(f"  - {item['config']}: {item['error']}")
            
            channels = tuple(merged_channels)
        else:
            # Just validate new channels without preserving old ones
            valid_channels = []
            for channel in normalized_channels:
                if isinstance(channel.get("channel"), str) and str(channel.get("channel", "")).strip():
                    valid_channels.append(channel)
            channels = tuple(valid_channels)
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
    session_string, session_name = resolve_telegram_session_config()
    if not isinstance(api_id, int) or not isinstance(api_hash, str) or not api_hash.strip():
        print("Telegram provider is missing api_id/api_hash in config/providers.json")
        return 1

    provider = TelegramProvider(
        TelegramProviderConfig(
            api_id=api_id,
            api_hash=api_hash,
            channels=channels,
            session_string=session_string.strip() if isinstance(session_string, str) and session_string.strip() else None,
            session_name=session_name,
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

    # Handle proxy node preservation and merging
    if preserve_configs:
        # Convert nodes to dictionaries for merging
        new_node_dicts = nodes_to_dicts(nodes)
        
        # Validate node format: must have required fields
        def validate_node(config: dict[str, object]) -> None:
            if not isinstance(config.get("protocol"), str) or not str(config.get("protocol", "")).strip():
                raise ValueError(f"Invalid node: missing or empty 'protocol' field in {config}")
            if not isinstance(config.get("host"), str) or not str(config.get("host", "")).strip():
                raise ValueError(f"Invalid node: missing or empty 'host' field in {config}")
            if not isinstance(config.get("port"), int) or config.get("port", 0) <= 0:
                raise ValueError(f"Invalid node: missing or invalid 'port' field in {config}")
        
        merged_node_dicts, invalid_nodes = config_merger.validate_and_merge(
            provider_name="telegram_proxy_nodes",
            new_configs=new_node_dicts,
            preserve=True,
            validator=validate_node,
        )
        
        if invalid_nodes:
            print(f"WARNING: {len(invalid_nodes)} proxy node(s) failed validation and were skipped:")
            for item in invalid_nodes:
                print(f"  - {item['error']}")
        
        # Convert back to nodes
        nodes = dicts_to_nodes(merged_node_dicts)
        print(f"Merged {len(nodes)} proxy nodes (new + preserved, deduplicated)")
    
    if not nodes:
        print("No valid proxy nodes available after merge and validation")
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
    print(f"Collected {len(nodes)} total proxy links from {channel_names}")
    print(f"Generated {len(result.nodes)} subscription nodes after validation and deduplication")
    print(f"Published subscription to {result.published.output_path}")
    print(f"Subscription payload length: {len(result.content)}")
    # also write decoded file next to the published output for inspection
    try:
        pub_path = Path(result.published.output_path)
        decoded_path = pub_path.with_name(pub_path.stem + ".decoded.txt")
        decoded_bytes = base64.b64decode(result.content.encode("utf-8"), validate=False)
        decoded_path.write_bytes(decoded_bytes)
        print(f"Wrote decoded subscription to {decoded_path}")
    except Exception as exc:  # noqa: BLE001
        print(f"Failed to write decoded subscription: {exc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
