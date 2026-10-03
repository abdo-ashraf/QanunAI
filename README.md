# QanunAI

Monorepo for QanunAI with:

- **Backend**: Python + FastAPI using `uv`, organized with DDD-style layers.
- **Frontend**: React app with feature-based architecture, TanStack Query, shadcn/ui conventions, ai-elements tooling, and Zod validation.
- **Deployment**: Docker + Docker Compose.
- **Automation**: pre-commit + GitHub Actions CI.

## Structure

- `/backend`
- `/frontend`
- `/docker-compose.yml`

## Run locally

```bash
docker compose up --build
```
