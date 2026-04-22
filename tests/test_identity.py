"""Offline tests for :mod:`mimeo.identity`."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from mimeo.config import Settings, ensure_dirs
from mimeo.identity import AmbiguousNameError, resolve_identity
from mimeo.schemas import ExpertCandidate, IdentityResolution

from .conftest import FakeLLMClient, FakeParallelClient, make_search_result


def _settings(tmp_path: Path, **overrides: object) -> Settings:
    base: dict[str, object] = {
        "expert_name": "John Smith",
        "output_dir": tmp_path,
    }
    base.update(overrides)
    s = Settings(**base)  # type: ignore[arg-type]
    ensure_dirs(s)
    return s


@pytest.mark.asyncio
async def test_preset_disambiguator_short_circuits(tmp_path: Path) -> None:
    """When the user supplies a disambiguator, no APIs are touched."""
    s = _settings(tmp_path, expert_description="economist at MIT")
    parallel = FakeParallelClient()
    llm = FakeLLMClient()

    out = await resolve_identity(settings=s, parallel=parallel, llm=llm)

    assert out.expert_description == "economist at MIT"
    assert parallel.search_calls == []
    assert llm.structured_calls == []


@pytest.mark.asyncio
async def test_assume_unambiguous_short_circuits(tmp_path: Path) -> None:
    s = _settings(tmp_path, assume_unambiguous=True)
    parallel = FakeParallelClient()
    llm = FakeLLMClient()

    out = await resolve_identity(settings=s, parallel=parallel, llm=llm)

    assert out.expert_description is None
    assert parallel.search_calls == []
    assert llm.structured_calls == []


@pytest.mark.asyncio
async def test_unambiguous_resolution_attaches_description(tmp_path: Path) -> None:
    s = _settings(tmp_path, expert_name="Naval Ravikant")
    parallel = FakeParallelClient(
        default_search=make_search_result(
            [
                {
                    "url": "https://en.wikipedia.org/wiki/Naval_Ravikant",
                    "title": "Naval Ravikant - Wikipedia",
                    "excerpts": ["Co-founder and former CEO of AngelList."],
                }
            ]
        )
    )
    llm = FakeLLMClient()
    llm.queue_structured(
        IdentityResolution,
        IdentityResolution(
            is_ambiguous=False,
            resolved_description="co-founder of AngelList, investor and essayist",
        ),
    )

    out = await resolve_identity(settings=s, parallel=parallel, llm=llm)

    assert out.expert_description == "co-founder of AngelList, investor and essayist"
    assert out.expert_context == " (co-founder of AngelList, investor and essayist)"
    assert len(parallel.search_calls) == 1
    assert len(llm.structured_calls) == 1
    # Cache file was written for next run.
    cache = s.workspace_dir / f"identity.{s.model_cache_id}.json"
    assert cache.exists()


@pytest.mark.asyncio
async def test_ambiguous_without_tty_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Non-interactive runs without a disambiguator fail loudly."""
    s = _settings(tmp_path)
    parallel = FakeParallelClient(
        default_search=make_search_result(
            [{"url": "https://example.com/a", "title": "John Smith the economist"}]
        )
    )
    llm = FakeLLMClient()
    llm.queue_structured(
        IdentityResolution,
        IdentityResolution(
            is_ambiguous=True,
            candidates=[
                ExpertCandidate(
                    name="John Smith",
                    description="Scottish economist, author of The Wealth of Nations",
                ),
                ExpertCandidate(
                    name="John Smith",
                    description="basketball coach, Michigan State",
                ),
            ],
        ),
    )

    # Force non-interactive regardless of how the tests are actually run.
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)

    with pytest.raises(AmbiguousNameError) as exc_info:
        await resolve_identity(settings=s, parallel=parallel, llm=llm)

    msg = str(exc_info.value)
    assert "John Smith" in msg
    assert "Scottish economist" in msg
    assert "--disambiguator" in msg


@pytest.mark.asyncio
async def test_empty_search_evidence_is_unambiguous(tmp_path: Path) -> None:
    """If the search returns nothing, we fall back to unambiguous without description."""
    s = _settings(tmp_path)
    parallel = FakeParallelClient()  # default_search is None -> empty results
    llm = FakeLLMClient()  # no queued structured response -> would blow up if called

    out = await resolve_identity(settings=s, parallel=parallel, llm=llm)

    assert out.expert_description is None
    assert llm.structured_calls == []


@pytest.mark.asyncio
async def test_cache_short_circuits_second_call(tmp_path: Path) -> None:
    s = _settings(tmp_path, expert_name="Naval Ravikant")
    cache = s.workspace_dir / f"identity.{s.model_cache_id}.json"
    cache.write_text(
        IdentityResolution(
            is_ambiguous=False,
            resolved_description="co-founder of AngelList",
        ).model_dump_json(),
        encoding="utf-8",
    )
    parallel = FakeParallelClient()
    llm = FakeLLMClient()

    out = await resolve_identity(settings=s, parallel=parallel, llm=llm)

    assert out.expert_description == "co-founder of AngelList"
    assert parallel.search_calls == []
    assert llm.structured_calls == []


@pytest.mark.asyncio
async def test_refresh_bypasses_identity_cache(tmp_path: Path) -> None:
    s = _settings(tmp_path, expert_name="Naval Ravikant", refresh=True)
    cache = s.workspace_dir / f"identity.{s.model_cache_id}.json"
    # Stale cache that should be ignored.
    cache.write_text(
        IdentityResolution(
            is_ambiguous=False, resolved_description="stale"
        ).model_dump_json(),
        encoding="utf-8",
    )
    parallel = FakeParallelClient(
        default_search=make_search_result(
            [{"url": "https://x.com/1", "title": "Fresh"}]
        )
    )
    llm = FakeLLMClient()
    llm.queue_structured(
        IdentityResolution,
        IdentityResolution(is_ambiguous=False, resolved_description="fresh"),
    )

    out = await resolve_identity(settings=s, parallel=parallel, llm=llm)

    assert out.expert_description == "fresh"
    assert len(llm.structured_calls) == 1


def test_ambiguous_name_error_lists_candidates() -> None:
    candidates = [
        ExpertCandidate(name="John Smith", description="economist"),
        ExpertCandidate(name="John Smith", description="basketball coach"),
    ]
    err = AmbiguousNameError(expert_name="John Smith", candidates=candidates)
    msg = str(err)
    assert "economist" in msg
    assert "basketball coach" in msg
    assert '--disambiguator "<short qualifier>"' in msg


# ---------------------------------------------------------------------------
# Internal helpers + uncommon branches
# ---------------------------------------------------------------------------


import sys  # noqa: E402

from rich.console import Console  # noqa: E402

from mimeo.identity import _apply_resolution, _prompt_choice  # noqa: E402


@pytest.mark.asyncio
async def test_resolve_identity_recovers_from_corrupt_cache(tmp_path: Path) -> None:
    s = _settings(tmp_path, expert_name="Naval")
    cache = s.workspace_dir / f"identity.{s.model_cache_id}.json"
    cache.write_text("not valid json", encoding="utf-8")

    parallel = FakeParallelClient(
        default_search=make_search_result(
            [{"url": "https://x.com", "title": "t", "excerpts": ["e"]}]
        )
    )
    llm = FakeLLMClient()
    llm.queue_structured(
        IdentityResolution,
        IdentityResolution(is_ambiguous=False, resolved_description="recovered"),
    )
    out = await resolve_identity(settings=s, parallel=parallel, llm=llm)
    assert out.expert_description == "recovered"


@pytest.mark.asyncio
async def test_resolve_identity_prints_progress_with_console(tmp_path: Path) -> None:
    s = _settings(tmp_path, expert_name="Naval")
    parallel = FakeParallelClient(
        default_search=make_search_result(
            [{"url": "https://x.com", "title": "t", "excerpts": ["e"]}]
        )
    )
    llm = FakeLLMClient()
    llm.queue_structured(
        IdentityResolution,
        IdentityResolution(is_ambiguous=False, resolved_description="q"),
    )
    console = Console(record=True, width=120)
    out = await resolve_identity(settings=s, parallel=parallel, llm=llm, console=console)
    assert out.expert_description == "q"
    rendered = console.export_text()
    assert "Resolving identity" in rendered
    assert "Resolved" in rendered


def test_apply_resolution_unambiguous_without_description(tmp_path: Path) -> None:
    s = _settings(tmp_path, expert_name="X")
    console = Console(record=True, width=120)
    out = _apply_resolution(
        s,
        IdentityResolution(is_ambiguous=False, resolved_description=None),
        console=console,
    )
    assert out.expert_description is None
    assert "No biographical evidence" in console.export_text()


def test_apply_resolution_ambiguous_with_tty_picks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    s = _settings(tmp_path, expert_name="John Smith")
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    # Force a specific pick (index 2 → second candidate).
    monkeypatch.setattr("rich.prompt.IntPrompt.ask", lambda *_a, **_kw: 2)
    candidates = [
        ExpertCandidate(name="A", description="first"),
        ExpertCandidate(name="B", description="second", evidence="ev"),
    ]
    out = _apply_resolution(
        s,
        IdentityResolution(is_ambiguous=True, candidates=candidates),
        console=Console(record=True, width=120),
    )
    assert out.expert_description == "second"


def test_apply_resolution_ambiguous_no_console_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    s = _settings(tmp_path, expert_name="John Smith")
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    with pytest.raises(AmbiguousNameError):
        _apply_resolution(
            s,
            IdentityResolution(
                is_ambiguous=True,
                candidates=[ExpertCandidate(name="A", description="d")],
            ),
            console=None,
        )


def test_prompt_choice_empty_candidates_returns_none() -> None:
    assert _prompt_choice(Console(), "X", []) == None  # noqa: E711


@pytest.mark.asyncio
async def test_classify_skips_search_results_without_urls(tmp_path: Path) -> None:
    s = _settings(tmp_path, expert_name="Naval")
    parallel = FakeParallelClient(
        default_search=make_search_result(
            [
                {"url": None, "title": "skip me"},
                {"url": "https://x.com/a", "title": "keep", "excerpts": ["e"]},
            ]
        )
    )
    llm = FakeLLMClient()
    llm.queue_structured(
        IdentityResolution,
        IdentityResolution(is_ambiguous=False, resolved_description="q"),
    )
    out = await resolve_identity(settings=s, parallel=parallel, llm=llm)
    assert out.expert_description == "q"
    _, user, _ = llm.structured_calls[0]
    assert "https://x.com/a" in user
    assert "skip me" not in user


def test_prompt_choice_returns_selected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("rich.prompt.IntPrompt.ask", lambda *_a, **_kw: 1)
    picked = _prompt_choice(
        Console(record=True, width=120),
        "X",
        [
            ExpertCandidate(name="One", description="first"),
            ExpertCandidate(name="Two", description="second", evidence="ev"),
        ],
    )
    assert picked is not None and picked.name == "One"
