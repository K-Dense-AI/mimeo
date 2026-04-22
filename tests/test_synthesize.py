"""Offline tests for :mod:`mimeo.synthesize`."""

from __future__ import annotations

import pytest

from mimeo.config import Settings, ensure_dirs
from mimeo.schemas import (
    AgentsOutput,
    ClusteredCorpus,
    ClusteredItem,
    Extraction,
    Principle,
    SkillOutput,
)
from mimeo.synthesize import (
    _CLUSTER_BATCH_CHARS,
    _MAX_CLUSTER_BATCHES,
    _maybe_truncate,
    _merge_corpora,
    _split_extractions_for_cluster,
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


# ---------------------------------------------------------------------------
# Batched clustering
# ---------------------------------------------------------------------------


def _big_extraction(source_id: str, pad_chars: int) -> Extraction:
    return Extraction(
        source_id=source_id,
        summary="x" * pad_chars,
        principles=[
            Principle(
                statement=f"Principle from {source_id}",
                rationale="r",
                source_id=source_id,
            )
        ],
    )


def test_split_extractions_single_batch_when_small() -> None:
    ext = [_big_extraction(f"src_{i:03d}", 200) for i in range(3)]
    batches = _split_extractions_for_cluster(ext)
    assert len(batches) == 1
    assert len(batches[0]) == 3


def test_split_extractions_batches_when_oversize() -> None:
    # Pad each extraction so ~3 fit per batch under _CLUSTER_BATCH_CHARS.
    per = _CLUSTER_BATCH_CHARS // 3
    ext = [_big_extraction(f"src_{i:03d}", per) for i in range(5)]
    batches = _split_extractions_for_cluster(ext)
    assert len(batches) >= 2
    # No batch should be empty and every extraction appears exactly once.
    seen: list[str] = []
    for batch in batches:
        assert batch
        seen.extend(e.source_id for e in batch)
    assert sorted(seen) == [e.source_id for e in ext]


def test_split_extractions_caps_batch_count() -> None:
    # Make each extraction so big that one fits per batch, and spawn more
    # than the cap so we trip the truncation path.
    per = _CLUSTER_BATCH_CHARS  # each alone already blows the budget
    ext = [_big_extraction(f"src_{i:03d}", per) for i in range(_MAX_CLUSTER_BATCHES + 3)]
    batches = _split_extractions_for_cluster(ext)
    assert len(batches) == _MAX_CLUSTER_BATCHES


def test_merge_corpora_dedupes_labels_and_unions_sources() -> None:
    a = ClusteredCorpus(
        expert_name="E",
        themes=["leverage", "time"],
        principles=[
            ClusteredItem(
                label="Seek Leverage",
                summary="Short.",
                source_ids=["src_000"],
            )
        ],
    )
    b = ClusteredCorpus(
        expert_name="E",
        themes=["Leverage"],  # dupe, case-insensitive
        principles=[
            ClusteredItem(
                label="seek leverage!",
                summary="A longer, more detailed summary of leveraging yourself.",
                representative_quote="Leverage is the key.",
                source_ids=["src_001", "src_002"],
            ),
            ClusteredItem(
                label="Own equity",
                summary="Equity compounds.",
                source_ids=["src_003"],
            ),
        ],
    )
    merged = _merge_corpora([a, b], expert_name="E")
    assert merged.themes == ["leverage", "time"]
    labels = [p.label for p in merged.principles]
    # "Own equity" appears in one corpus with 1 source; "Seek Leverage" has
    # 3 sources across both → should come first.
    assert labels[0].lower().startswith("seek")
    lev = merged.principles[0]
    assert set(lev.source_ids) == {"src_000", "src_001", "src_002"}
    # Longer summary wins.
    assert "longer" in lev.summary
    # Quote from the second corpus survives.
    assert lev.representative_quote == "Leverage is the key."


def test_merge_corpora_picks_longer_of_two_details() -> None:
    """Both ``details`` strings populated: _pick_longer keeps the longer one."""
    a = ClusteredCorpus(
        expert_name="E",
        principles=[
            ClusteredItem(
                label="Leverage",
                summary="s",
                details="a significantly longer details block",
                source_ids=["src_000"],
            )
        ],
    )
    b = ClusteredCorpus(
        expert_name="E",
        principles=[
            ClusteredItem(
                label="Leverage",
                summary="s",
                details="short",
                source_ids=["src_001"],
            )
        ],
    )
    # Order matters — first arg is longer so `_pick_longer` takes the `return a` branch.
    merged = _merge_corpora([a, b], expert_name="E")
    assert merged.principles[0].details == "a significantly longer details block"

    # Swap to exercise the `return b` branch.
    merged_swap = _merge_corpora([b, a], expert_name="E")
    assert merged_swap.principles[0].details == "a significantly longer details block"


def test_merge_corpora_skips_items_with_no_canonical_key() -> None:
    """Items whose label + summary are both pure punctuation are dropped."""
    corpus = ClusteredCorpus(
        expert_name="E",
        principles=[
            ClusteredItem(label="!!!", summary="???", source_ids=["src_000"]),
            ClusteredItem(label="Real", summary="x", source_ids=["src_001"]),
        ],
    )
    merged = _merge_corpora([corpus], expert_name="E")
    # Only "Real" survives; the punctuation-only item has no canonical key.
    assert [p.label for p in merged.principles] == ["Real"]


@pytest.mark.asyncio
async def test_cluster_corpus_batches_large_inputs(settings: Settings) -> None:
    ensure_dirs(settings)
    per = _CLUSTER_BATCH_CHARS // 2
    ext = [_big_extraction(f"src_{i:03d}", per) for i in range(5)]
    llm = FakeLLMClient()
    # Each batch gets its own ClusteredCorpus response.
    for i in range(6):  # overqueue
        llm.queue_structured(
            ClusteredCorpus,
            ClusteredCorpus(
                expert_name="placeholder",
                principles=[
                    ClusteredItem(
                        label=f"Idea {i}",
                        summary="s",
                        source_ids=[f"src_{i:03d}"],
                    )
                ],
            ),
        )
    corpus = await cluster_corpus(extractions=ext, settings=settings, llm=llm)
    assert corpus.expert_name == settings.expert_name
    assert len(llm.structured_calls) >= 2  # at least two batches ran
    # All items from the batches merged in; nothing silently dropped.
    assert len(corpus.principles) >= 2
