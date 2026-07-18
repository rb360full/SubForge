# Subscriptions folder

This folder contains generated subscription payloads used by the project.

- `default.txt` — Base64-encoded subscription payload (client import format).
- `default.decoded.txt` — (optional) decoded, human-readable lines (one URI per line).
- `decode_default.ps1` — PowerShell helper to decode `default.txt` to `default.decoded.txt`.
- `decode_default.py` — Python helper to decode `default.txt` to `default.decoded.txt`.

Use the helpers below to inspect the generated subscription payload without modifying the repository files.

PowerShell decode example:

```powershell
.\	ransactions\decode_default.ps1
```

Python decode example:

```powershell
python .\subscriptions\decode_default.py
```
