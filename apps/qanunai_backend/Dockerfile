FROM python:3.12-slim

WORKDIR /app

COPY apps/qanunai_backend/pyproject.toml apps/qanunai_backend/uv.lock ./
RUN pip install --no-cache-dir uv && python -m uv sync --frozen --no-install-project

COPY apps/qanunai_backend/src ./src
RUN python -m uv sync --frozen

EXPOSE 8000
CMD ["python", "-m", "uv", "run", "uvicorn", "presentation.app:app", "--host", "0.0.0.0", "--port", "8000"]
