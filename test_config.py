#!/usr/bin/env python3
"""Test script to verify configuration loads correctly."""

from src.core.config import ConfigurationLoader
from pathlib import Path

try:
    cfg = ConfigurationLoader(Path("config")).load()
    print("✓ Configuration loaded successfully")
    print("\nSubscriptions:")
    for s in cfg.subscriptions:
        print(f"  - name: {s.name}")
        print(f"    subscription_name: {s.subscription_name}")
        print(f"    output_path: {s.output_path}")
        print(f"    format: {s.format}")
        print(f"    enabled: {s.enabled}")
        print()
except Exception as e:
    print(f"✗ Error loading configuration: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
