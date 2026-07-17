# Configuration Guide

All runtime behavior should be driven by configuration.

## Rules

- Never hardcode provider URLs
- Never hardcode channels or destinations
- Never hardcode timeouts
- Never hardcode file paths when they can be configured
- Never hardcode subscription names

## Config Files

- `config/settings.json` for global settings
- `config/providers.json` for provider definitions
- `config/subscriptions.json` for subscription output definitions

## Expectations

- Config should be validated before use
- Missing or malformed config should fail clearly
- Defaults should be explicit and documented
- Environment overrides may be added later, but config files are the baseline

