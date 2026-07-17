# Decisions Log

## 2026-07-17

- Chose a pipeline-based architecture to keep provider, parsing, validation, testing, filtering, generation, and publishing concerns separated
- Reserved configuration files for all runtime values to avoid hardcoded environment-specific details
- Kept the first commit intentionally limited to scaffolding only
- Added a dependency-light MVP pipeline that preserves raw proxy links while introducing a normalized internal node model
