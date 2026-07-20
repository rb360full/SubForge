#!/usr/bin/env python3
from pathlib import Path
import base64
import sys

repo = Path(__file__).resolve().parent

# Support command line arguments
input_name = sys.argv[1] if len(sys.argv) > 1 else "Telegram-List1.txt"
output_name = sys.argv[2] if len(sys.argv) > 2 else f"{Path(input_name).stem}.decoded.txt"

inp = repo / input_name
out = repo / output_name

if not inp.exists():
    raise SystemExit(f"Input not found: {inp}")

data = inp.read_bytes()
try:
    decoded = base64.b64decode(data, validate=False)
except Exception as exc:
    raise SystemExit(f"Failed to decode: {exc}")

out.write_bytes(decoded)
print(f"Wrote decoded file: {out}")
