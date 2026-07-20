#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import base64
import os
from pathlib import Path
import argparse
from concurrent.futures import ThreadPoolExecutor

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from parser.subscription_parser import SubscriptionParser
from filter.deduplicator import SubscriptionDeduplicator
from tester.connectivity_tester import ConnectivityTester
from generator.subscription_generator import SubscriptionGenerator


def fast_generate(
    input_text_path: Path | str,
    output_path: Path | str,
    *,
    skip_tests: bool = False,
    workers: int = 32,
    timeout: float = 3.0,
    decode: bool = False,
) -> None:
    input_path = Path(input_text_path)
    out_path = Path(output_path)
    text = input_path.read_text(encoding="utf-8")

    parser = SubscriptionParser()
    dedup = SubscriptionDeduplicator()
    tester = ConnectivityTester(timeout_seconds=timeout)
    generator = SubscriptionGenerator()

    parsed = parser.parse_text(text)
    deduped = dedup.deduplicate(parsed.nodes)

    if skip_tests:
        nodes = list(deduped)
    else:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futures = [ex.submit(tester.test, n) for n in deduped]
            nodes = [n for n, f in zip(deduped, futures) if f.result().is_reachable]

    tmp = tempfile.NamedTemporaryFile("w+", delete=False, encoding="utf-8")
    try:
        for node in nodes:
            line = generator._serialize_node(node)
            tmp.write(line + "\n")
        tmp.flush()
        tmp.close()

        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(tmp.name, "rb") as fin, open(out_path, "wb") as fout:
            base64.encode(fin, fout)

        print(f"Wrote encoded subscription to {out_path} ({len(nodes)} nodes)")

        if decode:
            # read the encoded file and write decoded lines
            try:
                encoded = out_path.read_bytes()
                decoded = base64.b64decode(encoded, validate=False)
                decoded_path = out_path.with_name(out_path.stem + ".decoded.txt")
                decoded_path.write_bytes(decoded)
                print(f"Wrote decoded subscription to {decoded_path}")
            except Exception as exc:
                print(f"Failed to write decoded file: {exc}")
    finally:
        try:
            os.unlink(tmp.name)
        except Exception:
            pass


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Path to raw input text")
    parser.add_argument("output", nargs="?", help="Output path (default: subscriptions/Telegram-List1.txt)")
    parser.add_argument("--skip-tests", action="store_true", help="Skip connectivity tests for faster generation")
    parser.add_argument("--workers", type=int, default=32, help="Number of worker threads for connectivity tests")
    parser.add_argument("--timeout", type=float, default=3.0, help="Socket timeout seconds for connectivity checks")
    parser.add_argument("--decode", action="store_true", help="Also write decoded output (Telegram-List1.decoded.txt)")
    args = parser.parse_args()

    input_file = Path(args.input)
    out_file = Path(args.output) if args.output else REPO_ROOT / "subscriptions" / "Telegram-List1.txt"
    # pass timeout to the tester via environment of the script
    # create tester inside fast_generate using provided timeout
    fast_generate(
        input_file,
        out_file,
        skip_tests=args.skip_tests,
        workers=args.workers,
        timeout=args.timeout,
        decode=args.decode,
    )


if __name__ == "__main__":
    main()
