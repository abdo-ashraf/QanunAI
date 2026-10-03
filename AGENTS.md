# AGENTS.md (Root)

## Monorepo layout
- `apps/qanunai_backend/`: Python backend using FastAPI, managed with `uv`, organized with DDD layers.
- `apps/qanunai_frontend/`: React app with feature-based structure, using TanStack Query, shadcn/ui conventions, ai-elements tooling, and Zod validation.

## Working conventions
- Keep changes scoped to either `apps/qanunai_backend/` or `apps/qanunai_frontend/` unless cross-cutting infra is required.
- Prefer small feature slices in frontend (`src/features/<feature-name>`).
- Keep backend dependencies and commands managed via `uv`.

## Common commands
- Backend: `cd apps/qanunai_backend && python -m uv run --env-file .env uvicorn presentation.app:app --host 0.0.0.0 --port 8000`
- Frontend: `cd apps/qanunai_frontend && npm run dev -- --host 0.0.0.0 --port 5173`
- Docker Compose: `docker compose up --build`
