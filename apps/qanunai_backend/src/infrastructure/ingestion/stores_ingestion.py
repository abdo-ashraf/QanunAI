"""Index all parsable files under the stores folder into the vector store."""

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from haystack.components.converters import (
    CSVToDocument,
    DOCXToDocument,
    HTMLToDocument,
    JSONConverter,
    MarkdownToDocument,
    PPTXToDocument,
    PyPDFToDocument,
    TextFileToDocument,
    XLSXToDocument,
)
from haystack.components.preprocessors import DocumentSplitter

from application.config import get_settings
from application.services.rag_service import RagEngine
from domain.entities.knowledge_document import KnowledgeDocument

logger = logging.getLogger(__name__)

MANIFEST_FILENAME = ".indexing-manifest.json"

_CONVERTER_FACTORIES: dict[str, Any] = {
    ".txt": TextFileToDocument,
    ".md": MarkdownToDocument,
    ".pdf": PyPDFToDocument,
    ".csv": CSVToDocument,
    ".json": JSONConverter,
    ".html": HTMLToDocument,
    ".htm": HTMLToDocument,
    ".docx": DOCXToDocument,
    ".pptx": PPTXToDocument,
    ".xlsx": XLSXToDocument,
}


def _content_hash(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()


def _manifest_path(stores_dir: Path) -> Path:
    settings = get_settings()
    if settings.stores_manifest_path:
        return Path(settings.stores_manifest_path)
    return stores_dir.parent / f".{stores_dir.name}-indexing-manifest.json"


def _load_manifest(stores_dir: Path) -> dict[str, str]:
    manifest_path = _manifest_path(stores_dir)
    if not manifest_path.exists():
        return {}
    try:
        return json.loads(manifest_path.read_text())
    except (json.JSONDecodeError, OSError):
        logger.warning("Ignoring unreadable manifest %s", manifest_path)
        return {}


def _save_manifest(stores_dir: Path, manifest: dict[str, str]) -> None:
    manifest_path = _manifest_path(stores_dir)
    try:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2))
    except OSError as exc:
        logger.warning("Could not write manifest %s: %s", manifest_path, exc)


def index_stores_files(engine: RagEngine, stores_path: Path) -> dict[str, int]:
    settings = get_settings()
    stores_dir = Path(stores_path)
    if not stores_dir.is_dir():
        logger.warning(
            "Stores folder %s does not exist; skipping ingestion", stores_dir
        )
        return {"indexed": 0, "skipped": 0, "unchanged": 0}

    splitter = DocumentSplitter(
        split_by="word",
        split_length=settings.stores_chunk_size,
        split_overlap=settings.stores_chunk_overlap,
    )
    manifest = _load_manifest(stores_dir)
    indexed = skipped = unchanged = 0

    for path in sorted(stores_dir.rglob("*")):
        if not path.is_file() or path.name == MANIFEST_FILENAME:
            continue
        if any(part.startswith(".") and part not in (".", "..") for part in path.parts):
            continue
        suffix = path.suffix.lower()
        converter_factory = _CONVERTER_FACTORIES.get(suffix)
        if converter_factory is None:
            logger.warning("Skipping non-parsable file: %s", path)
            skipped += 1
            continue

        try:
            content_hash = _content_hash(path)
        except OSError as exc:
            logger.warning("Skipping unreadable file %s: %s", path, exc)
            skipped += 1
            continue

        relative = str(path.relative_to(stores_dir))
        if manifest.get(relative) == content_hash:
            unchanged += 1
            continue

        try:
            result = converter_factory().run(sources=[path])
            documents = result.get("documents", [])
        except Exception as exc:
            logger.warning("Skipping file %s: failed to parse (%s)", path, exc)
            skipped += 1
            continue

        if not documents:
            logger.warning("Skipping file %s: no content extracted", path)
            skipped += 1
            continue

        for document in documents:
            document.meta["source"] = relative
            document.meta["content_hash"] = content_hash

        try:
            chunks = splitter.run(documents=documents)["documents"]
        except Exception as exc:
            logger.warning("Skipping file %s: failed to chunk (%s)", path, exc)
            skipped += 1
            continue

        written = engine.index(
            [
                KnowledgeDocument(content=chunk.content or "", meta=dict(chunk.meta))
                for chunk in chunks
                if chunk.content
            ]
        )
        if written > 0:
            manifest[relative] = content_hash
            indexed += 1
            logger.info("Indexed %s (%d chunks)", relative, written)
        else:
            logger.warning("Skipping file %s: nothing was written", path)
            skipped += 1

    _save_manifest(stores_dir, manifest)
    logger.info(
        "Stores ingestion complete: %d indexed, %d unchanged, %d skipped",
        indexed,
        unchanged,
        skipped,
    )
    return {"indexed": indexed, "skipped": skipped, "unchanged": unchanged}
