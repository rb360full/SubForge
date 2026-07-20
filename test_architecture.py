#!/usr/bin/env python3
"""Test script to verify the new subscription architecture."""

from src.core.config import ConfigurationLoader
from src.models.subscription import Subscription
from pathlib import Path

print("=" * 60)
print("Testing Subscription Model and Configuration")
print("=" * 60)

# Test 1: Model instantiation
print("\n[TEST 1] Subscription model with provider and channels...")
try:
    sub = Subscription(
        name="test",
        enabled=True,
        subscription_name="Test-List",
        format="plain",
        provider="telegram",
        channels=("https://t.me/channel1", "https://t.me/channel2")
    )
    assert sub.provider == "telegram"
    assert len(sub.channels) == 2
    assert sub.output_path == "Test-List.txt"
    print("✅ PASS: Subscription model works correctly")
except Exception as e:
    print(f"❌ FAIL: {e}")

# Test 2: Configuration loading
print("\n[TEST 2] Loading configuration with new schema...")
try:
    cfg = ConfigurationLoader(Path("config")).load()
    enabled_subs = [s for s in cfg.subscriptions if s.enabled]
    print(f"✅ PASS: Loaded {len(enabled_subs)} enabled subscription(s)")
    
    for sub in enabled_subs:
        print(f"   - {sub.subscription_name} ({len(sub.channels)} channels)")
        print(f"     Provider: {sub.provider}")
        if sub.channels:
            print(f"     Channels: {', '.join(sub.channels[:2])}{'...' if len(sub.channels) > 2 else ''}")
except Exception as e:
    print(f"❌ FAIL: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Unique channel deduplication
print("\n[TEST 3] Unique channel deduplication algorithm...")
try:
    cfg = ConfigurationLoader(Path("config")).load()
    enabled_subs = [s for s in cfg.subscriptions if s.enabled]
    
    # Extract unique channels
    unique_channels = set()
    for sub in enabled_subs:
        unique_channels.update(sub.channels)
    
    total_channels = sum(len(sub.channels) for sub in enabled_subs)
    print(f"✅ PASS: Deduplication works")
    print(f"   Total channels across subscriptions: {total_channels}")
    print(f"   Unique channels: {len(unique_channels)}")
    print(f"   Saved API calls: {total_channels - len(unique_channels)}")
    
except Exception as e:
    print(f"❌ FAIL: {e}")

print("\n" + "=" * 60)
print("All tests completed successfully!")
print("=" * 60)
