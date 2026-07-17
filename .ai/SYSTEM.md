# System Rules

This file is mandatory reading for every future coding session in SubForge.

## Project Philosophy

- Build for production from the start
- Prefer clarity over cleverness
- Keep modules small and narrowly scoped
- Make behavior configurable
- Treat providers, parsing, validation, and publishing as separate concerns
- Optimize for safe extension without core rewrites

## Coding Rules

- Use Python 3.12+
- Prefer type hints for all public code
- Use dataclasses where they reduce boilerplate and improve clarity
- Favor dependency injection over global state
- Keep functions small and single-purpose
- Use logging instead of prints
- Avoid hardcoded URLs, channels, timeouts, names, and paths
- Do not add networking or scraping logic unless the task explicitly requires it

## Architecture Rules

- Follow the pipeline strictly:
  Providers -> Collectors -> Parser -> Normalizer -> Validator -> Deduplicator -> Connectivity Tester -> Filters -> Generator -> Publisher
- Each stage must do exactly one job
- Data should flow through explicit models
- Providers must be swappable without changing core stages
- Future provider additions should require no core architecture rewrite
- Keep domain logic independent from transport and publishing details

## Documentation Rules

- Update docs when behavior, structure, or configuration changes
- Keep `README.md` user-oriented and complete
- Maintain `.ai/` files as operational guidance for future sessions
- Prefer concise, accurate docs over speculative prose
- Record decisions in `.ai/DECISIONS.md`

## Commit Rules

- Make one logical change per commit when possible
- Use clear, action-oriented commit messages
- Do not rewrite history unless explicitly requested
- The initial scaffold commit for this repository is: `Initial project scaffold`

## Testing Rules

- Add tests alongside new behavior
- Prefer deterministic tests
- Test each pipeline stage independently
- Keep tests fast and hermetic
- Do not rely on live external services for unit tests

## AI Behavior

- Read this file before making changes
- Inspect the repository before editing
- Preserve user changes unless explicitly asked to modify them
- Ask only when a decision cannot be safely inferred
- Prefer implementing the smallest correct foundation first
- Leave the repository in a coherent, buildable state

