"""Versioned, fingerprinted cache helpers.

Every cache entry is wrapped in a small envelope. A stage only accepts an
entry when its fingerprint still matches all inputs that can affect the
output. Legacy bare JSON and corrupt entries are safe cache misses.
"""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from .config import PROMPTS_DIR

logger = logging.getLogger(__name__)

CACHE_LAYOUT_VERSION = 1


def canonical_data(value: Any) -> Any:
    """Convert supported values to deterministic JSON-compatible data."""
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json", exclude_none=False)
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {
            str(key): canonical_data(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (list, tuple)):
        return [canonical_data(item) for item in value]
    if isinstance(value, (set, frozenset)):
        normalized = [canonical_data(item) for item in value]
        return sorted(normalized, key=_canonical_json)
    return value


def _canonical_json(value: Any) -> str:
    return json.dumps(
        canonical_data(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def digest(value: Any) -> str:
    """Return a stable SHA-256 digest for JSON-compatible data."""
    return hashlib.sha256(_canonical_json(value).encode("utf-8")).hexdigest()


def fingerprint(stage: str, **inputs: Any) -> str:
    """Fingerprint a stage name, cache layout, and all relevant inputs."""
    return digest(
        {
            "layout": CACHE_LAYOUT_VERSION,
            "stage": stage,
            "inputs": inputs,
        }
    )[:16]


def prompt_digest(*names: str) -> str:
    """Digest prompt files by logical name."""
    prompts: dict[str, str] = {}
    for name in names:
        filename = name if name.endswith(".md") else f"{name}.md"
        prompts[filename] = (PROMPTS_DIR / filename).read_text(encoding="utf-8")
    return digest(prompts)


def schema_digest(*models: type[BaseModel]) -> str:
    """Digest Pydantic JSON schemas used at an LLM/cache boundary."""
    return digest({model.__name__: model.model_json_schema() for model in models})


def load_cache(path: Path, expected_fingerprint: str) -> Any | None:
    """Load an envelope payload or return ``None`` for any safe miss."""
    if not path.exists():
        return None
    try:
        envelope = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        logger.warning("Corrupt cache at %s; recomputing", path)
        return None
    if not isinstance(envelope, dict):
        logger.info("Ignoring legacy cache at %s", path)
        return None
    if envelope.get("version") != CACHE_LAYOUT_VERSION:
        logger.info("Ignoring cache layout mismatch at %s", path)
        return None
    if envelope.get("fingerprint") != expected_fingerprint:
        logger.info("Cache fingerprint changed for %s; recomputing", path)
        return None
    if "data" not in envelope:
        logger.warning("Cache envelope at %s has no data; recomputing", path)
        return None
    return envelope["data"]


def store_cache(path: Path, cache_fingerprint: str, data: Any) -> None:
    """Write a cache envelope."""
    path.parent.mkdir(parents=True, exist_ok=True)
    envelope = {
        "version": CACHE_LAYOUT_VERSION,
        "fingerprint": cache_fingerprint,
        "data": canonical_data(data),
    }
    path.write_text(
        json.dumps(envelope, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
