# QanunAI

Q&A assistant for Arabic legal documents (Egyptian Civil Code of 1948) providing exact article citations.

Monorepo for QanunAI with:

- **Backend**: Python + FastAPI using `uv`, organized with DDD-style layers.
- **Frontend**: React app with feature-based architecture, TanStack Query, shadcn/ui conventions, ai-elements tooling, and Zod validation.
- **Deployment**: Docker + Docker Compose.
- **Automation**: pre-commit + GitHub Actions CI.

## Structure

- `/apps/qanunai_backend`
- `/apps/qanunai_frontend`
- `/docker-compose.yml`

## Run locally

```bash
cp apps/qanunai_backend/.env.example apps/qanunai_backend/.env
# edit apps/qanunai_backend/.env with your API keys
docker compose up --build
```
