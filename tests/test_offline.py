"""Offline tests that don't touch the network.

These verify the plumbing: schemas, URL parsing, writers, and prompt loading.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from mimeo.config import (
    MissingCredentialError,
    PROMPTS_DIR,
    Settings,
    ensure_dirs,
    require_openrouter_key,
    require_parallel_key,
)
from mimeo.discovery import _merge_and_dedupe, _normalize_url
from mimeo.fetchers.youtube import extract_video_id
from mimeo.llm import _strip_code_fence, load_prompt
from mimeo.schemas import (
    AgentsOutput,
    ClusteredCorpus,
    ClusteredItem,
    SkillOutput,
    Source,
)
from mimeo.writers import write_agents, write_skill


def test_extract_video_id() -> None:
    assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"
    assert (
        extract_video_id("https://www.youtube.com/watch?v=abc123&t=10s") == "abc123"
    )
    assert extract_video_id("https://youtube.com/shorts/xyz789") == "xyz789"
    assert extract_video_id("https://example.com/not-youtube") is None


def test_prompt_files_exist() -> None:
    for name in ("extract", "cluster", "synthesize_skill", "synthesize_agents"):
        content = load_prompt(name)
        assert content
        assert PROMPTS_DIR / f"{name}.md"


def test_schema_roundtrip() -> None:
    corpus = ClusteredCorpus(
        expert_name="Test Expert",
        themes=["leverage", "compounding"],
        principles=[
            ClusteredItem(
                label="Seek leverage",
                summary="Use tools, capital, and content to multiply effort.",
                source_ids=["src_001", "src_003"],
            )
        ],
    )
    assert corpus.principles[0].frequency == 2
    raw = corpus.model_dump_json()
    assert ClusteredCorpus.model_validate_json(raw) == corpus


def test_write_skill(tmp_path: Path) -> None:
    settings = Settings(
        expert_name="Test Expert",
        output_dir=tmp_path,
    )
    ensure_dirs(settings)

    output = SkillOutput(
        skill_name="test-expert",
        description=(
            "Think like Test Expert. Use this skill whenever the user is deciding "
            "about leverage, compounding, or long-term strategy."
        ),
        skill_body="# Thinking like Test Expert\n\nBody here.\n",
        principles_md="# Principles\n\n## Seek leverage\n\nUse tools.\n",
        frameworks_md="# Frameworks\n\nNone yet.\n",
        mental_models_md="# Mental models\n\nNone yet.\n",
        quotes_md="# Quotes\n\n> Quote.\n",
    )
    sources = [
        Source(id="src_000", url="https://example.com/a", title="A", bucket="essays"),
        Source(id="src_001", url="https://example.com/b", title="B", bucket="talks"),
    ]
    skill_dir = write_skill(output=output, sources=sources, settings=settings)

    skill_md = (skill_dir / "SKILL.md").read_text()
    assert skill_md.startswith("---\n")
    # Validate YAML frontmatter parses.
    _, fm_text, body = skill_md.split("---", 2)
    fm = yaml.safe_load(fm_text)
    assert fm["name"] == "test-expert"
    assert "leverage" in fm["description"]
    assert "Thinking like Test Expert" in body

    for ref in ("principles.md", "frameworks.md", "mental-models.md", "quotes.md", "sources.md"):
        assert (skill_dir / "references" / ref).exists(), ref

    sources_md = (skill_dir / "references" / "sources.md").read_text()
    assert "src_000" in sources_md and "example.com/a" in sources_md


def test_write_agents_appends_sources(tmp_path: Path) -> None:
    settings = Settings(
        expert_name="Test Expert",
        output_dir=tmp_path,
        format="agents",
    )
    ensure_dirs(settings)

    output = AgentsOutput(
        content=(
            "# Think like Test Expert\n\n"
            "We favor leverage and long time horizons.\n\n"
            "## Default stance\n\n- Ask about durability before velocity.\n"
        ),
    )
    sources = [
        Source(id="src_000", url="https://example.com/a", title="A", bucket="essays"),
        Source(id="src_001", url="https://example.com/b", title="B", bucket="talks"),
    ]
    agents_path = write_agents(output=output, sources=sources, settings=settings)

    text = agents_path.read_text()
    assert agents_path.name == "AGENTS.md"
    assert text.startswith("# Think like Test Expert")
    assert "---" not in text.splitlines()[0], "AGENTS.md must not have frontmatter"
    assert "## Sources" in text, "sources section should be auto-appended"
    assert "src_000" in text and "example.com/a" in text
    # When the model already includes a ## Sources section we must not double-append.
    output2 = AgentsOutput(
        content="# Think like Test Expert\n\n## Sources\n\n- already here\n",
    )
    agents_path2 = write_agents(output=output2, sources=sources, settings=settings)
    text2 = agents_path2.read_text()
    assert text2.count("## Sources") == 1


def test_settings_slug_and_paths(tmp_path: Path) -> None:
    s = Settings(expert_name="Naval Ravikant", output_dir=tmp_path)
    assert s.slug == "naval-ravikant"
    assert s.skill_dir == tmp_path / "naval-ravikant"
    assert s.references_dir == s.skill_dir / "references"
    assert s.workspace_dir == s.skill_dir / "_workspace"


def test_model_cache_id_is_stable_and_model_scoped(tmp_path: Path) -> None:
    a = Settings(expert_name="N", output_dir=tmp_path, model="anthropic/claude-opus-4.7")
    b = Settings(expert_name="N", output_dir=tmp_path, model="anthropic/claude-opus-4.7")
    c = Settings(expert_name="N", output_dir=tmp_path, model="openai/gpt-5")
    assert a.model_cache_id == b.model_cache_id
    assert a.model_cache_id != c.model_cache_id
    assert len(a.model_cache_id) == 8


def test_normalize_url() -> None:
    assert _normalize_url("HTTPS://Example.com/a/") == "https://example.com/a"
    assert (
        _normalize_url("https://example.com/a?utm_source=x&utm_medium=y")
        == "https://example.com/a"
    )
    assert (
        _normalize_url("https://example.com/a?foo=bar&utm_source=x")
        == "https://example.com/a?foo=bar"
    )
    assert _normalize_url("https://example.com/a#frag") == "https://example.com/a"


def test_merge_and_dedupe_collapses_duplicates() -> None:
    sources = [
        Source(id="a_000", url="https://example.com/x/", title="X long", bucket="essays"),
        Source(
            id="b_000",
            url="https://example.com/x?utm_source=y",
            title="X",
            kind="talk",
            bucket="talks",
            excerpts=["an excerpt"],
        ),
        Source(id="c_000", url="https://other.com/y", title="Y", bucket="interviews"),
    ]
    merged = _merge_and_dedupe(sources)
    assert len(merged) == 2
    # Renumbered to src_XXX.
    assert all(m.id.startswith("src_") for m in merged)
    # The merged entry should have the non-"other" kind and the excerpt.
    x = next(m for m in merged if "example.com/x" in m.url)
    assert x.kind == "talk"
    assert "an excerpt" in x.excerpts


def test_strip_code_fence() -> None:
    assert _strip_code_fence("```json\n{\"a\": 1}\n```") == '{"a": 1}'
    assert _strip_code_fence("```\n{\"a\": 1}\n```") == '{"a": 1}'
    assert _strip_code_fence('{"a": 1}') == '{"a": 1}'
    # Single-line fenced block (no newline) falls through untouched.
    assert _strip_code_fence("  hello  ") == "hello"


def test_prompts_dir_exists_in_repo() -> None:
    assert PROMPTS_DIR.exists(), PROMPTS_DIR
    assert (PROMPTS_DIR / "extract.md").exists()


def test_require_openrouter_key_raises_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with pytest.raises(MissingCredentialError, match="OPENROUTER_API_KEY"):
        require_openrouter_key()


def test_require_parallel_key_raises_when_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("PARALLEL_API_KEY", raising=False)
    with pytest.raises(MissingCredentialError, match="PARALLEL_API_KEY"):
        require_parallel_key()


def test_require_keys_return_value_when_set(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENROUTER_API_KEY", "abc")
    monkeypatch.setenv("PARALLEL_API_KEY", "def")
    assert require_openrouter_key() == "abc"
    assert require_parallel_key() == "def"


def test_expert_context_property(tmp_path: Path) -> None:
    s = Settings(expert_name="N", output_dir=tmp_path)
    assert s.expert_context == ""
    s2 = Settings(
        expert_name="N", output_dir=tmp_path, expert_description="investor, essayist"
    )
    assert s2.expert_context == " (investor, essayist)"
