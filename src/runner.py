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

    # Validate telegram provider
    telegram_provider = next(
        (provider for provider in config.providers if provider.name == "telegram" and provider.config.enabled),
        None,
    )
    if telegram_provider is None:
        print("No enabled Telegram provider found in config/providers.json")
        return 1

    # Validate subscriptions
    enabled_subscriptions = [sub for sub in config.subscriptions if sub.enabled]
    if not enabled_subscriptions:
        print("No enabled subscriptions found in config/subscriptions.json")
        return 1

    print(f"Found {len(enabled_subscriptions)} enabled subscription(s): {', '.join(s.subscription_name for s in enabled_subscriptions)}")

    # Extract unique channels from all enabled subscriptions (excluding merged for now)
    unique_channels_set: set[str] = set()
    non_merged_subscriptions = []
    merged_subscription = None
    
    for subscription in enabled_subscriptions:
        if subscription.name == "merged":
            merged_subscription = subscription
        else:
            non_merged_subscriptions.append(subscription)
            unique_channels_set.update(subscription.channels)
    
    # If merged subscription exists and has empty channels, it will use all unique channels
    # Otherwise add merged subscription's channels to unique set
    if merged_subscription:
        if merged_subscription.channels:
            unique_channels_set.update(merged_subscription.channels)
        # If empty, it will use unique_channels_set which is built from other subscriptions
    
    # Re-create enabled_subscriptions list with proper order
    final_subscriptions = non_merged_subscriptions.copy()
    if merged_subscription:
        final_subscriptions.append(merged_subscription)
    
    if not unique_channels_set:
        print("No channels defined in any enabled subscription")
        return 1

    print(f"Extracting {len(unique_channels_set)} unique channel(s)...")

    # Normalize channels to provider format
    provider_channels: list[dict[str, object]] = []
    for channel_url in unique_channels_set:
        provider_channels.append({"channel": channel_url.strip()})

    if not provider_channels:
        print("No valid channels found")
        return 1

    # Setup provider
    output_dir = Path(config.settings.output_directory)
    api_id = telegram_provider.config.source.get("api_id")
    api_hash = telegram_provider.config.source.get("api_hash")
    session_string, session_name = resolve_telegram_session_config()
    
    if not isinstance(api_id, int) or not isinstance(api_hash, str) or not api_hash.strip():
        print("Telegram provider is missing api_id/api_hash in config/providers.json")
        return 1

    # Collect proxy nodes from unique channels (once)
    provider = TelegramProvider(
        TelegramProviderConfig(
            api_id=api_id,
            api_hash=api_hash,
            channels=tuple(provider_channels),
            session_string=session_string.strip() if isinstance(session_string, str) and session_string.strip() else None,
            session_name=session_name,
            timeout_seconds=config.settings.default_timeout_seconds,
            default_message_limit=telegram_provider.config.source.get("default_message_limit", 50),
        )
    )
    
    try:
        all_nodes = list(provider.collect())
    except Exception as exc:  # noqa: BLE001
        print(f"Error collecting from Telegram: {exc}")
        return 1

    if not all_nodes:
        print(f"No proxy links found in channels: {', '.join(unique_channels_set)}")
        return 1

    print(f"✓ Collected {len(all_nodes)} proxy nodes from {len(unique_channels_set)} channel(s)")

    # Handle proxy node preservation and merging
    config_merger = ConfigMerger(Path("config") / ".previous")
    preserve_configs = telegram_provider.config.preserve_previous_configs
    
    if preserve_configs:
        new_node_dicts = nodes_to_dicts(all_nodes)
        
        def validate_node(config: dict[str, object]) -> None:
            if not isinstance(config.get("protocol"), str) or not str(config.get("protocol", "")).strip():
                raise ValueError(f"Invalid node: missing or empty 'protocol'")
            if not isinstance(config.get("host"), str) or not str(config.get("host", "")).strip():
                raise ValueError(f"Invalid node: missing or empty 'host'")
            if not isinstance(config.get("port"), int) or config.get("port", 0) <= 0:
                raise ValueError(f"Invalid node: missing or invalid 'port'")
        
        merged_node_dicts, invalid_nodes = config_merger.validate_and_merge(
            provider_name="telegram_proxy_nodes",
            new_configs=new_node_dicts,
            preserve=True,
            validator=validate_node,
        )
        
        if invalid_nodes:
            print(f"WARNING: {len(invalid_nodes)} proxy node(s) failed validation")
        
        all_nodes = dicts_to_nodes(merged_node_dicts)
        print(f"✓ Merged {len(all_nodes)} proxy nodes (new + preserved, deduplicated)")
    
    if not all_nodes:
        print("No valid proxy nodes available")
        return 1

    # Process each subscription
    pipeline = SubscriptionPipeline(
        output_dir=output_dir,
        tester=ConnectivityTester(timeout_seconds=config.settings.default_timeout_seconds),
    )
    
    success_count = 0
    for subscription in final_subscriptions:
        # Filter nodes for this subscription based on channels
        # Get raw text that includes channel source info if available
        collected_text = "\n".join(
            node.metadata.get("raw", "") for node in all_nodes if isinstance(node.metadata.get("raw"), str)
        )
        
        output_filename = f"subscriptions/{subscription.output_path}"
        
        try:
            # Determine source display
            if subscription.channels:
                source_display = subscription.channels[0]
                channels_display = ', '.join(subscription.channels[:3]) + ('...' if len(subscription.channels) > 3 else '')
            else:
                # For merged subscription with empty channels
                source_display = "merged"
                channels_display = f"{len(unique_channels_set)} unique channels"
            
            result = pipeline.run(collected_text, output_filename, source=source_display)
            
            # Write decoded file
            pub_path = Path(result.published.output_path)
            decoded_path = pub_path.with_name(pub_path.stem + ".decoded.txt")
            decoded_bytes = base64.b64decode(result.content.encode("utf-8"), validate=False)
            decoded_path.write_bytes(decoded_bytes)
            
            print(f"✓ Published {subscription.subscription_name}.txt with {len(result.nodes)} nodes to {result.published.output_path}")
            print(f"  Channels: {channels_display}")
            success_count += 1
            
        except Exception as exc:  # noqa: BLE001
            print(f"✗ Failed to publish {subscription.subscription_name}: {exc}")
    
    if success_count == 0:
        print("Failed to process any subscriptions")
        return 1
    
    print(f"\n✓ Successfully processed {success_count}/{len(final_subscriptions)} subscription(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
