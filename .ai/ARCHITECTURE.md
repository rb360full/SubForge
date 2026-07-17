# Architecture Guide

## Pipeline

SubForge uses a strict pipeline architecture:

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

## Design Rules

- Each stage has exactly one responsibility
- Dependencies should point inward toward the core
- Transport adapters belong at the edges
- Provider-specific concerns must not leak into validation or publishing
- New providers should integrate through interfaces, not core rewrites

## Suggested Package Roles

- `src/core/`: orchestration, interfaces, shared contracts
- `src/models/`: data structures used across the pipeline
- `src/providers/`: provider adapters and source-specific logic
- `src/parser/`: raw input parsing
- `src/validator/`: schema and rule validation
- `src/tester/`: connectivity verification
- `src/filter/`: post-validation filtering
- `src/generator/`: output assembly
- `src/publisher/`: file and distribution publishing
- `src/utils/`: shared utilities with minimal coupling

