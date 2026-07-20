# Multiple Subscriptions Configuration

SubForge now supports generating multiple subscription files from a single configuration. Each subscription is defined in `config/subscriptions.json` with a unique `subscription_name`.

## Configuration Structure

The `config/subscriptions.json` file contains an array of subscription definitions:

```json
{
  "subscriptions": [
    {
      "name": "default",
      "enabled": true,
      "subscription_name": "Telegram-List1",
      "format": "plain"
    },
    {
      "name": "list2",
      "enabled": true,
      "subscription_name": "Telegram-List2",
      "format": "plain"
    }
  ]
}
```

## Configuration Fields

- **name**: Internal identifier for the subscription (must be unique)
- **enabled**: Boolean flag to enable/disable the subscription processing
- **subscription_name**: Base name for output files (will generate `{subscription_name}.txt` and `{subscription_name}.decoded.txt`)
- **format**: Output format (currently "plain")

## Dynamic File Generation

When the pipeline runs, each enabled subscription automatically generates:

1. `subscriptions/{subscription_name}.txt` - Base64-encoded payload
2. `subscriptions/{subscription_name}.decoded.txt` - Decoded, human-readable format

## Adding New Subscriptions

To add a new subscription (e.g., from a different Telegram channel):

1. Open `config/subscriptions.json`
2. Add a new object to the `subscriptions` array:

```json
{
  "name": "secondary",
  "enabled": true,
  "subscription_name": "Telegram-List3",
  "format": "plain"
}
```

3. Commit your changes
4. The workflow will generate `Telegram-List3.txt` and `Telegram-List3.decoded.txt` automatically

## GitHub Actions Integration

The `.github/workflows/update.yml` workflow automatically:

- Commits all generated subscription files in the `subscriptions/` directory
- Uploads all files as artifacts
- Runs on a schedule (every 8 hours) or manually

## Decoding Subscriptions

To decode a subscription file manually:

### Python
```bash
python subscriptions/decode_default.py "Telegram-List2.txt"
python subscriptions/decode_default.py "Telegram-List2.txt" "custom-output.txt"
```

### PowerShell
```powershell
& .\subscriptions\decode_default.ps1 -Input "Telegram-List2.txt"
& .\subscriptions\decode_default.ps1 -Input "Telegram-List2.txt" -Output "custom-output.txt"
```

Default output name is `{input_name}.decoded.txt` if not specified.
