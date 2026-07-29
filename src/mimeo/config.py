"""Environment + runtime configuration.

Loads ``.env`` once at import time via python-dotenv, then exposes a typed
:class:`Settings` object. Validation happens lazily so tests and tooling that
don't need API keys can still import the package.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv

load_dotenv()

Mode = Literal["text", "captions", "full"]
Format = Literal["skill", "agents", "both"]

DEFAULT_MODEL = os.environ.get("MIMEO_MODEL", "google/gemini-3.6-flash")
DEFAULT_AVATAR_MODEL = os.environ.get("MIMEO_AVATAR_MODEL", "openai/gpt-image-2")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


@dataclass(frozen=True)
class Settings:
    """Resolved runtime settings for a single pipeline run."""

    expert_name: str
    output_dir: Path
    mode: Mode = "captions"
    format: Format = "skill"
    max_sources: int = 25
    deep_research: bool = False
    model: str = DEFAULT_MODEL
    concurrency: int = 5
    refresh: bool = False
    # Optional short qualifier that disambiguates which real person we mean.
    # Either supplied by the user (`--disambiguator`) or filled in by the
    # identity-resolution stage before discovery runs.
    expert_description: str | None = None
    # Skip the identity-resolution pre-flight entirely (non-interactive runs
    # where you're confident the name is unambiguous).
    assume_unambiguous: bool = False
    # Post-cluster: verify every representative_quote actually appears in
    # one of its listed source texts, stripping the ones that don't.
    verify_quotes: bool = True
    # Post-author: run an adversarial-editor LLM pass over the generated
    # artifact and write the critique to ``_workspace/critique_*.md``.
    critique: bool = True
    # Close the critique loop: re-author the artifact using the critique as
    # editorial feedback and keep iterating until it clears ``quality_bar`` or
    # ``max_revisions`` is exhausted, keeping the best-scoring draft. On by
    # default. ``critique`` is the master switch: ``--no-critique`` disables
    # scoring entirely (and therefore refining too), while ``--no-refine``
    # keeps a single critique pass without the rewrite loop.
    refine: bool = True
    max_revisions: int = 2
    quality_bar: int = 8
    # Painterly portrait of the expert saved as ``avatar.<ext>`` in the
    # skill directory. Generated via an OpenRouter image model; failures
    # are logged and swallowed so a flaky image endpoint never breaks the
    # main pipeline. On by default; disable with ``--no-avatar``.
    generate_avatar: bool = True
    avatar_model: str = DEFAULT_AVATAR_MODEL

    def __post_init__(self) -> None:
        if not self.expert_name.strip():
            raise ValueError("expert_name must not be empty")
        if self.mode not in ("text", "captions", "full"):
            raise ValueError(f"Unsupported mode: {self.mode}")
        if self.format not in ("skill", "agents", "both"):
            raise ValueError(f"Unsupported format: {self.format}")
        if not 1 <= self.max_sources <= 200:
            raise ValueError("max_sources must be between 1 and 200")
        if not 1 <= self.concurrency <= 20:
            raise ValueError("concurrency must be between 1 and 20")
        if not 0 <= self.max_revisions <= 5:
            raise ValueError("max_revisions must be between 0 and 5")
        if not 0 <= self.quality_bar <= 10:
            raise ValueError("quality_bar must be between 0 and 10")
        if not self.model.strip():
            raise ValueError("model must not be empty")
        if self.generate_avatar and not self.avatar_model.strip():
            raise ValueError(
                "avatar_model must not be empty when avatar generation is enabled"
            )

    @property
    def slug(self) -> str:
        from slugify import slugify

        return slugify(self.expert_name)

    @property
    def expert_context(self) -> str:
        """Parenthetical qualifier for prompt interpolation.

        Renders as ``` (co-founder of AngelList, investor)``` when a
        description is set, otherwise empty. Prompts include this directly
        after ``{expert}`` so unambiguous runs read naturally without a
        dangling empty parenthetical.
        """
        if self.expert_description:
            return f" ({self.expert_description})"
        return ""

    @property
    def skill_dir(self) -> Path:
        return self.output_dir / self.slug

    @property
    def workspace_dir(self) -> Path:
        return self.skill_dir / "_workspace"

    @property
    def references_dir(self) -> Path:
        return self.skill_dir / "references"

    @property
    def model_cache_id(self) -> str:
        """Short hash of the model slug, used to scope LLM caches.

        Changing the model should invalidate every LLM-produced artifact
        (distilled extractions, clustered corpus, authored outputs). We embed
        this hash in cache filenames so two runs with different models keep
        independent caches without stepping on each other.
        """
        return hashlib.sha1(self.model.encode("utf-8")).hexdigest()[:8]


class MissingCredentialError(RuntimeError):
    """Raised when a required API key is not in the environment."""


def require_openrouter_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise MissingCredentialError(
            "OPENROUTER_API_KEY is not set. Copy .env.example to .env and fill it in."
        )
    return key


def require_parallel_key() -> str:
    key = os.environ.get("PARALLEL_API_KEY")
    if not key:
        raise MissingCredentialError(
            "PARALLEL_API_KEY is not set. Copy .env.example to .env and fill it in."
        )
    return key


def openrouter_default_headers() -> dict[str, str]:
    """Optional attribution headers OpenRouter recommends."""
    headers: dict[str, str] = {}
    if url := os.environ.get("OPENROUTER_SITE_URL"):
        headers["HTTP-Referer"] = url
    if title := os.environ.get("OPENROUTER_APP_NAME"):
        headers["X-Title"] = title
    return headers


def ensure_dirs(settings: Settings) -> None:
    """Create the skill output scaffold. Idempotent."""
    settings.skill_dir.mkdir(parents=True, exist_ok=True)
    settings.references_dir.mkdir(parents=True, exist_ok=True)
    settings.workspace_dir.mkdir(parents=True, exist_ok=True)
    for sub in ("discovery", "raw", "distilled", "research"):
        (settings.workspace_dir / sub).mkdir(parents=True, exist_ok=True)


# Prompts live in ``<repo>/prompts`` for editable/dev installs, and are
# force-included at ``<site-packages>/mimeo/prompts`` for wheel installs. We
# check both so ``pip install mimeo`` and ``uv sync`` both work.
_HERE = Path(__file__).resolve().parent
_REPO_PROMPTS = _HERE.parents[1] / "prompts"
_PACKAGE_PROMPTS = _HERE / "prompts"
PROMPTS_DIR = _REPO_PROMPTS if _REPO_PROMPTS.exists() else _PACKAGE_PROMPTS
