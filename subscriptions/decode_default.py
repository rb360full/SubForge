#!/usr/bin/env python3
from pathlib import Path
import base64

repo = Path(__file__).resolve().parent
inp = repo / "default.txt"
out = repo / "default.decoded.txt"

if not inp.exists():
    raise SystemExit(f"Input not found: {inp}")

data = inp.read_bytes()
try:
    decoded = base64.b64decode(data, validate=False)
except Exception as exc:
    raise SystemExit(f"Failed to decode: {exc}")

out.write_bytes(decoded)
print(f"Wrote decoded file: {out}")
