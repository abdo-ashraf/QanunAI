# AGENTS.md (Backend)

## Stack
- Python + FastAPI
- Dependency/runtime management: `uv`
- Architecture: DDD-inspired layers (`domain`, `application`, `infrastructure`, `presentation`)

## Layer boundaries
- `domain`: core entities and business rules, framework-agnostic.
- `application`: use-cases/services orchestrating domain behavior.
- `infrastructure`: adapters, data access, integrations.
- `presentation`: FastAPI routers, request/response DTOs.

## Local commands
- Install/sync: `python -m uv sync`
- Run API: `python -m uv run --env-file .env uvicorn presentation.app:app --reload`
