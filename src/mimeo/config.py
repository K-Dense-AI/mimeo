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
from typing import Literal, TypeAlias, cast

from dotenv import load_dotenv

load_dotenv()

Mode = Literal["text", "captions", "full"]
Format = Literal["skill", "agents", "both"]
LLMProvider: TypeAlias = Literal["openrouter", "openai", "anthropic", "xai", "google"]
SearchProviderName: TypeAlias = Literal["parallel"]
ImageProviderName: TypeAlias = Literal["openrouter", "none"]

OPENROUTER_DEFAULT_MODEL = "google/gemini-3.1-pro-preview"
DEFAULT_LLM_PROVIDER = cast(
    LLMProvider, os.environ.get("MIMEO_LLM_PROVIDER", "openrouter").lower()
)
DEFAULT_SEARCH_PROVIDER = cast(
    SearchProviderName, os.environ.get("MIMEO_SEARCH_PROVIDER", "parallel").lower()
)
DEFAULT_IMAGE_PROVIDER = cast(
    ImageProviderName, os.environ.get("MIMEO_IMAGE_PROVIDER", "openrouter").lower()
)
DEFAULT_MODEL = (
    os.environ.get("MIMEO_MODEL")
    or os.environ.get("MIMEO_OPENROUTER_MODEL")
    or OPENROUTER_DEFAULT_MODEL
)
DEFAULT_AVATAR_MODEL = os.environ.get("MIMEO_AVATAR_MODEL", "openai/gpt-5.4-image-2")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
XAI_BASE_URL = "https://api.x.ai/v1"

_LLM_PROVIDERS = frozenset({"openrouter", "openai", "anthropic", "xai", "google"})
_SEARCH_PROVIDERS = frozenset({"parallel"})
_IMAGE_PROVIDERS = frozenset({"openrouter", "none"})


@dataclass(frozen=True)
class Settings:
    """Resolved runtime settings for a single pipeline run."""

    expert_name: str
    output_dir: Path
    mode: Mode = "captions"
    format: Format = "skill"
    max_sources: int = 25
    deep_research: bool = False
    model: str | None = None
    llm_provider: LLMProvider = DEFAULT_LLM_PROVIDER
    search_provider: SearchProviderName = DEFAULT_SEARCH_PROVIDER
    image_provider: ImageProviderName = DEFAULT_IMAGE_PROVIDER
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
    # Painterly portrait of the expert saved as ``avatar.<ext>`` in the
    # skill directory. Generated via the configured image provider; failures
    # are logged and swallowed so a flaky image endpoint never breaks the
    # main pipeline. On by default; disable with ``--no-avatar``.
    generate_avatar: bool = True
    avatar_model: str = DEFAULT_AVATAR_MODEL

    def __post_init__(self) -> None:
        llm_provider = _validate_choice(
            "llm_provider", self.llm_provider, _LLM_PROVIDERS
        )
        search_provider = _validate_choice(
            "search_provider", self.search_provider, _SEARCH_PROVIDERS
        )
        image_provider = _validate_choice(
            "image_provider", self.image_provider, _IMAGE_PROVIDERS
        )
        object.__setattr__(self, "llm_provider", llm_provider)
        object.__setattr__(self, "search_provider", search_provider)
        object.__setattr__(self, "image_provider", image_provider)
        object.__setattr__(
            self, "model", resolve_llm_model(cast(LLMProvider, llm_provider), self.model)
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
        (distilled extractions, clustered corpus, authored outputs). OpenRouter
        keeps its historical model-only cache key for compatibility; direct
        providers include ``provider:model`` so same-named model aliases do not
        collide across providers.
        """
        material = (
            self.model
            if self.llm_provider == "openrouter"
            else f"{self.llm_provider}:{self.model}"
        )
        return hashlib.sha1(str(material).encode("utf-8")).hexdigest()[:8]


class MissingConfigurationError(RuntimeError):
    """Raised when required runtime configuration is absent or invalid."""


class MissingCredentialError(MissingConfigurationError):
    """Raised when a required API key is not in the environment."""


def resolve_llm_model(provider: LLMProvider, model: str | None = None) -> str:
    """Resolve the model for ``provider`` from explicit value or environment."""
    if model:
        return model
    provider_env = f"MIMEO_{provider.upper()}_MODEL"
    if provider_model := os.environ.get(provider_env):
        return provider_model
    if generic_model := os.environ.get("MIMEO_MODEL"):
        return generic_model
    if provider == "openrouter":
        return OPENROUTER_DEFAULT_MODEL
    raise MissingConfigurationError(
        f"No model configured for LLM provider '{provider}'. Set --model, "
        f"MIMEO_MODEL, or {provider_env}."
    )


def require_llm_key(provider: LLMProvider) -> str:
    if provider == "openrouter":
        return require_openrouter_key()
    if provider == "openai":
        return _require_env("OPENAI_API_KEY")
    if provider == "anthropic":
        return _require_env("ANTHROPIC_API_KEY")
    if provider == "xai":
        return _require_env("XAI_API_KEY")
    if provider == "google":
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not key:
            raise MissingCredentialError(
                "GEMINI_API_KEY or GOOGLE_API_KEY is not set. Copy .env.example "
                "to .env and fill in one of them."
            )
        return key
    raise MissingConfigurationError(f"Unsupported LLM provider: {provider}")


def require_openrouter_key() -> str:
    return _require_env("OPENROUTER_API_KEY")


def require_parallel_key() -> str:
    return _require_env("PARALLEL_API_KEY")


def openrouter_default_headers() -> dict[str, str]:
    """Optional attribution headers OpenRouter recommends."""
    headers: dict[str, str] = {}
    if url := os.environ.get("OPENROUTER_SITE_URL"):
        headers["HTTP-Referer"] = url
    if title := os.environ.get("OPENROUTER_APP_NAME"):
        headers["X-Title"] = title
    return headers


def _require_env(name: str) -> str:
    key = os.environ.get(name)
    if not key:
        raise MissingCredentialError(
            f"{name} is not set. Copy .env.example to .env and fill it in."
        )
    return key


def _validate_choice(name: str, value: str, allowed: frozenset[str]) -> str:
    lowered = value.lower()
    if lowered not in allowed:
        choices = ", ".join(sorted(allowed))
        raise MissingConfigurationError(
            f"Unsupported {name} '{value}'. Expected one of: {choices}."
        )
    return lowered


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
