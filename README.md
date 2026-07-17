# SubForge

SubForge is a modular subscription pipeline for V2Ray and Xray ecosystems.

It is designed to collect proxy configurations from multiple providers, normalize them into a common model, validate them, remove duplicates, test connectivity, filter dead nodes, and publish subscription outputs in a maintainable pipeline.

## Purpose

SubForge provides a production-ready foundation for subscription aggregation with a clean architecture and a workspace layout that is easy to extend.

## Features

- pnpm workspace layout
- TypeScript ESM packages
- Minimal executable CLI
- Parser and core package primitives
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

This sprint only introduces the workspace skeleton. Future configuration files will continue to live under `config/`.

## GitHub Actions

The repository still contains the workflow skeletons created in the earlier scaffold stage.

## Development Notes

- Keep changes small and reviewable
- Prefer dependency injection over global state
- Add tests alongside new behavior
- Avoid unnecessary dependencies

## Future Plans

- Add shared utilities in `packages/common`
- Introduce real provider adapters
- Implement parsing, validation, and publishing stages
