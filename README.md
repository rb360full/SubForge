# SubForge

SubForge is a modular subscription pipeline for V2Ray and Xray ecosystems.

The current MVP can extract supported proxy links from Telegram message text, normalize them into a shared model, remove duplicates, generate an importable subscription payload, and publish that payload to disk.

## Purpose

SubForge provides a production-ready foundation for subscription aggregation with a clean architecture and a workspace layout that is easy to extend.

## Features

- pnpm workspace layout
- TypeScript ESM packages
- Minimal executable CLI
- Parser and core package primitives
- Python MVP pipeline for parsing, deduplication, generation, and publishing
- Vitest-based testing
- Cross-platform scripts
- Clean architecture boundaries

## Architecture

SubForge follows a linear pipeline:

Providers
↓
Collectors
↓
Parser
↓
Normalizer
↓
Validator
↓
Deduplicator
↓
Connectivity Tester
↓
Filters
↓
Generator
↓
Publisher

Each module has one responsibility and communicates through explicit package boundaries.

## MVP Pipeline

The first usable Python milestone currently includes:

- `SubscriptionParser` for extracting `vmess://`, `vless://`, `trojan://`, `ss://`, and `socks://` links from text
- `SubscriptionNode` as the normalized internal model
- `SubscriptionDeduplicator` for stable order-preserving deduplication
- `SubscriptionGenerator` for producing base64 subscription payloads
- `FilePublisher` for writing generated subscriptions to the configured output folder
- `SubscriptionPipeline` for orchestrating the MVP flow end to end

## Workspace Packages

- `packages/core` contains shared command and workflow primitives
- `packages/common` contains reusable utility types
- `apps/cli` provides the executable command-line interface

## Installation

SubForge targets Node.js 22 LTS or newer and uses `pnpm` via Corepack.

```bash
corepack pnpm install
```

## Development

```bash
corepack pnpm dev
```

## Available Commands

- `corepack pnpm build` - build all workspace packages
- `corepack pnpm test` - run all workspace tests
- `corepack pnpm dev` - run the CLI
- `corepack pnpm dev --version` - print the CLI version
- `corepack pnpm dev hello` - print the hello message

## Configuration

Configuration files continue to live under `config/` and drive the MVP pipeline:

- `config/settings.json`
- `config/providers.json`
- `config/subscriptions.json`

## GitHub Actions

The repository includes a scheduled update workflow at `.github/workflows/update.yml`.

- Runs every 8 hours
- Installs the Python package
- Executes the Telegram subscription pipeline
- Uploads all generated subscription files from `config/subscriptions.json` as workflow artifacts

The workflow expects the `TELEGRAM_SESSION_STRING` secret for non-interactive Telegram access.

## Development Notes

- Keep changes small and reviewable
- Prefer dependency injection over global state
- Add tests alongside new behavior
- Avoid unnecessary dependencies

## Future Plans

- Add shared utilities in `packages/common`
- Introduce a Telegram provider adapter backed by a real Telegram client library
- Expand normalization and validation for richer proxy metadata
