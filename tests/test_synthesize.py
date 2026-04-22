"""Offline tests for :mod:`mimeo.synthesize`."""

from __future__ import annotations

import pytest

from mimeo.config import Settings, ensure_dirs
from mimeo.schemas import AgentsOutput, ClusteredCorpus, Extraction, SkillOutput
from mimeo.synthesize import (
    _maybe_truncate,
    author_agents,
    author_skill,
    cluster_corpus,
)

from .conftest import (
    FakeLLMClient,
    sample_agents_output,
    sample_clustered_corpus,
    sample_extraction,
    sample_skill_output,
)


def test_maybe_truncate_noop_and_truncation() -> None:
    assert _maybe_truncate("hi", 10) == "hi"
    big = "A" * 50
    out = _maybe_truncate(big, 10)
    assert out.startswith("A" * 10)
    assert "[truncated for length]" in out


# ---------------------------------------------------------------------------
# cluster_corpus
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_cluster_corpus_with_extractions(settings: Settings) -> None:
    ensure_dirs(settings)
    llm = FakeLLMClient()
    # Model drops the expert_name; cluster_corpus should re-stamp it.
    returned = sample_clustered_corpus("Someone Else")
    llm.queue_structured(ClusteredCorpus, returned)

    corpus = await cluster_corpus(
        extractions=[sample_extraction("src_000")], settings=settings, llm=llm
    )
    assert corpus.expert_name == settings.expert_name
    cache = settings.workspace_dir / f"clustered_corpus.{settings.model_cache_id}.json"
    assert cache.exists()


@pytest.mark.asyncio
async def test_cluster_corpus_empty_shortcircuits(settings: Settings) -> None:
    ensure_dirs(settings)
    llm = FakeLLMClient()
    corpus = await cluster_corpus(extractions=[], settings=settings, llm=llm)
    assert corpus.expert_name == settings.expert_name
    assert corpus.principles == []
    assert llm.structured_calls == []


@pytest.mark.asyncio
async def test_cluster_corpus_reads_cache(settings: Settings) -> None:
    ensure_dirs(settings)
    cache = settings.workspace_dir / f"clustered_corpus.{settings.model_cache_id}.json"
    cached = sample_clustered_corpus(settings.expert_name)
    cache.write_text(cached.model_dump_json(), encoding="utf-8")

    llm = FakeLLMClient()
    corpus = await cluster_corpus(
        extractions=[sample_extraction()], settings=settings, llm=llm
    )
    assert corpus == cached
    assert llm.structured_calls == []


@pytest.mark.asyncio
async def test_cluster_corpus_recovers_from_corrupt_cache(settings: Settings) -> None:
    ensure_dirs(settings)
    cache = settings.workspace_dir / f"clustered_corpus.{settings.model_cache_id}.json"
    cache.write_text("not json", encoding="utf-8")

    llm = FakeLLMClient()
    llm.queue_structured(ClusteredCorpus, sample_clustered_corpus(settings.expert_name))
    corpus = await cluster_corpus(
        extractions=[sample_extraction()], settings=settings, llm=llm
    )
    assert corpus.expert_name == settings.expert_name


# ---------------------------------------------------------------------------
# author_skill / author_agents
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_author_skill_happy_and_caches(settings: Settings) -> None:
    ensure_dirs(settings)
    llm = FakeLLMClient()
    llm.queue_structured(SkillOutput, sample_skill_output())
    out = await author_skill(
        corpus=sample_clustered_corpus(settings.expert_name),
        settings=settings,
        llm=llm,
    )
    assert out.skill_name == "test-expert"
    cache = settings.workspace_dir / f"skill_output.{settings.model_cache_id}.json"
    assert cache.exists()


@pytest.mark.asyncio
async def test_author_skill_reads_cache(settings: Settings) -> None:
    ensure_dirs(settings)
    cache = settings.workspace_dir / f"skill_output.{settings.model_cache_id}.json"
    cache.write_text(sample_skill_output().model_dump_json(), encoding="utf-8")
    llm = FakeLLMClient()
    out = await author_skill(
        corpus=sample_clustered_corpus(), settings=settings, llm=llm
    )
    assert out.skill_name == "test-expert"
    assert llm.structured_calls == []


@pytest.mark.asyncio
async def test_author_skill_recovers_from_corrupt_cache(settings: Settings) -> None:
    ensure_dirs(settings)
    cache = settings.workspace_dir / f"skill_output.{settings.model_cache_id}.json"
    cache.write_text("{bad", encoding="utf-8")
    llm = FakeLLMClient()
    llm.queue_structured(SkillOutput, sample_skill_output())
    out = await author_skill(
        corpus=sample_clustered_corpus(), settings=settings, llm=llm
    )
    assert out.skill_name == "test-expert"


@pytest.mark.asyncio
async def test_author_agents_happy_and_caches(settings: Settings) -> None:
    ensure_dirs(settings)
    llm = FakeLLMClient()
    llm.queue_structured(AgentsOutput, sample_agents_output())
    out = await author_agents(
        corpus=sample_clustered_corpus(settings.expert_name),
        settings=settings,
        llm=llm,
    )
    assert "Think like Test Expert" in out.content
    cache = settings.workspace_dir / f"agents_output.{settings.model_cache_id}.json"
    assert cache.exists()


@pytest.mark.asyncio
async def test_author_agents_reads_cache(settings: Settings) -> None:
    ensure_dirs(settings)
    cache = settings.workspace_dir / f"agents_output.{settings.model_cache_id}.json"
    cache.write_text(sample_agents_output().model_dump_json(), encoding="utf-8")
    llm = FakeLLMClient()
    out = await author_agents(
        corpus=sample_clustered_corpus(), settings=settings, llm=llm
    )
    assert "Think like Test Expert" in out.content
    assert llm.structured_calls == []


@pytest.mark.asyncio
async def test_author_agents_recovers_from_corrupt_cache(settings: Settings) -> None:
    ensure_dirs(settings)
    cache = settings.workspace_dir / f"agents_output.{settings.model_cache_id}.json"
    cache.write_text("oops", encoding="utf-8")
    llm = FakeLLMClient()
    llm.queue_structured(AgentsOutput, sample_agents_output())
    out = await author_agents(corpus=sample_clustered_corpus(), settings=settings, llm=llm)
    assert "Think like Test Expert" in out.content
