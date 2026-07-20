# Subscriptions folder

This folder contains generated subscription payloads used by the project.

- `Telegram-List1.txt` — Base64-encoded subscription payload (client import format).
- `Telegram-List1.decoded.txt` — (optional) decoded, human-readable lines (one URI per line).
- `decode_default.ps1` — PowerShell helper to decode subscription files.
- `decode_default.py` — Python helper to decode subscription files.

Multiple subscription files can be configured in `config/subscriptions.json` by adding new entries with different `subscription_name` values. Each will generate corresponding `.txt` and `.decoded.txt` files.

Use the helpers below to inspect the generated subscription payload without modifying the repository files.

Use the helpers below to inspect the generated subscription payload without modifying the repository files.

PowerShell decode example:

```powershell
.\	ransactions\decode_default.ps1
```

Python decode example:

```powershell
python .\subscriptions\decode_default.py
```
