from pathlib import Path

import yaml
from haystack.dataclasses import ChatMessage


def load_prompt(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"Prompt file does not exist: {path}")

    with path.open(encoding="utf-8") as prompt_file:
        payload = yaml.safe_load(prompt_file)

    if not isinstance(payload, dict) or not isinstance(payload.get("text"), str):
        raise ValueError(f"Prompt file must contain a string 'text' field: {path}")

    text = payload["text"].strip()
    if not text:
        raise ValueError(f"Prompt file contains an empty 'text' field: {path}")
    return text


def load_rag_prompt_messages(prompts_path: str | Path) -> list[ChatMessage]:
    prompt_dir = Path(prompts_path)
    return [
        ChatMessage.from_system(load_prompt(prompt_dir / "system.yml")),
        ChatMessage.from_user(load_prompt(prompt_dir / "user.yml")),
    ]
