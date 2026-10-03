import uvicorn


def main() -> None:
    uvicorn.run("qanunai_backend.presentation.app:app", host="0.0.0.0", port=8000)
