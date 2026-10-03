# Backend

FastAPI backend managed with `uv` and organized with DDD-inspired layers:

- `domain/`
- `application/`
- `infrastructure/`
- `presentation/`

Run locally:

```bash
python -m uv sync
python -m uv run uvicorn qanunai_backend.presentation.app:app --reload
```
