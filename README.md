# SubForge

SubForge automatically builds clean subscription files for V2Ray and Xray clients.

It is designed to collect proxy configurations from multiple providers, normalize them into a common model, validate them, remove duplicates, test connectivity, filter dead nodes, and publish subscription outputs in a maintainable pipeline.

## Purpose

SubForge exists to provide a modular, production-ready foundation for subscription aggregation.

The project is intentionally structured so that provider integrations, validation, testing, filtering, and publishing can evolve independently without forcing changes across the entire codebase.

## Features

- Modular pipeline architecture
- Provider abstraction for Telegram, GitHub, and HTTP sources
- Normalization and validation stages
- Deduplication and connectivity testing stages
- Filter and publisher boundaries with single responsibility
- Centralized configuration
- CI-friendly project layout
- Strong typing and clean-architecture-oriented organization

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

Each module has one responsibility and communicates through explicit data models.

### Core principles

- Business rules stay out of transport-specific code
- Providers should be pluggable without core rewrites
- Configuration should drive behavior, not hardcoded values
- Each stage should be independently testable

## Roadmap

### Foundation

- [x] Project scaffold
- [x] Core foundation implementation
- [x] Architecture and policy documents
- [x] Configuration placeholders
- [x] GitHub Actions workflow skeletons

### Next implementation phases

- Provider interfaces and collector contracts
- Subscription data model and parser implementation
- Normalization and validation rules
- Deduplication strategy
- Connectivity tester integration
- Filter composition
- Generator output formats
- Publisher adapters

## Installation

SubForge targets Python 3.12+.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Configuration

Configuration is stored in `config/` and should remain the source of truth for runtime behavior.

- `config/settings.json` for global settings
- `config/providers.json` for provider definitions
- `config/subscriptions.json` for subscription output definitions

Do not hardcode:

- channels
- URLs
- timeouts
- paths
- subscription names

## GitHub Actions

The repository includes workflow placeholders for:

- `update.yml`
- `lint.yml`
- `tests.yml`

These workflows are intended to support scheduled updates, lint checks, and test execution as the implementation grows.

## Development

Recommended workflow:

1. Update or add configuration first
2. Implement one pipeline stage at a time
3. Add tests alongside each feature
4. Keep modules focused and small
5. Prefer dependency injection over global state

### Local quality checks

The project is scaffolded for:

- formatting
- linting
- static typing
- unit testing

## Future plans

- Provider adapters for more source types
- Richer subscription formats
- Health scoring and quality ranking
- Incremental publishing
- Observability and structured metrics
- Safe automation for scheduled refreshes
- Plugin-friendly expansion points

## Contributing

Please read:

- `.ai/SYSTEM.md`
- `.ai/PROJECT.md`
- `.ai/ARCHITECTURE.md`
- `docs/CONTRIBUTING.md`

These files define the operating rules for humans and future AI sessions.
