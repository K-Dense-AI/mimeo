"""Offline tests for :mod:`mimeo.cli` — drive the Typer app with CliRunner."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from typer.testing import CliRunner

from mimeo import cli as cli_module
from mimeo.cli import app, main
from mimeo.config import MissingCredentialError, Settings
from mimeo.identity import AmbiguousNameError
from mimeo.schemas import ExpertCandidate


runner = CliRunner()


def _patch_run_pipeline(
    monkeypatch: pytest.MonkeyPatch,
    *,
    captured: dict,
    raise_: BaseException | None = None,
) -> None:
    async def _fake_run(settings: Settings, **kwargs):
        captured["settings"] = settings
        captured["kwargs"] = kwargs
        if raise_ is not None:
            raise raise_
        return settings.skill_dir

    monkeypatch.setattr(cli_module, "run_pipeline", _fake_run)


def test_cli_help_lists_expert_arg() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    # Typer flattens single-command apps, so `EXPERT` is the positional on root.
    assert "EXPERT" in result.stdout


def test_cli_build_defaults(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict = {}
    _patch_run_pipeline(monkeypatch, captured=captured)
    result = runner.invoke(
        app,
        ["Naval Ravikant", "--output-dir", str(tmp_path)],
    )
    assert result.exit_code == 0, result.stdout
    settings: Settings = captured["settings"]
    assert settings.expert_name == "Naval Ravikant"
    # Defaults.
    assert settings.mode == "captions"
    assert settings.format == "skill"
    assert settings.max_sources == 25
    assert settings.deep_research is False
    assert settings.refresh is False
    assert settings.concurrency == 5
    assert "Done" in result.stdout


def test_cli_build_flags(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict = {}
    _patch_run_pipeline(monkeypatch, captured=captured)
    result = runner.invoke(
        app,
        [
            "Test Expert",
            "--mode",
            "full",
            "--format",
            "both",
            "--max-sources",
            "3",
            "--deep-research",
            "--model",
            "openai/gpt-5",
            "--output-dir",
            str(tmp_path),
            "--concurrency",
            "2",
            "--refresh",
            "--verbose",
        ],
    )
    assert result.exit_code == 0
    settings: Settings = captured["settings"]
    assert settings.mode == "full"
    assert settings.format == "both"
    assert settings.max_sources == 3
    assert settings.deep_research is True
    assert settings.model == "openai/gpt-5"
    assert settings.refresh is True
    assert settings.concurrency == 2


def test_cli_build_missing_credentials_exits_2(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: dict = {}
    _patch_run_pipeline(
        monkeypatch,
        captured=captured,
        raise_=MissingCredentialError("PARALLEL_API_KEY not set"),
    )
    result = runner.invoke(
        app, ["Someone", "--output-dir", str(tmp_path)]
    )
    assert result.exit_code == 2
    assert "Missing credential" in result.stdout


def test_cli_build_pipeline_failure_exits_1(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: dict = {}
    _patch_run_pipeline(
        monkeypatch, captured=captured, raise_=RuntimeError("boom")
    )
    result = runner.invoke(
        app, ["Someone", "--output-dir", str(tmp_path)]
    )
    assert result.exit_code == 1
    assert "Pipeline failed" in result.stdout


def test_cli_build_pipeline_failure_verbose_shows_traceback(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: dict = {}
    _patch_run_pipeline(monkeypatch, captured=captured, raise_=RuntimeError("boom"))
    result = runner.invoke(
        app,
        ["Someone", "--output-dir", str(tmp_path), "--verbose"],
    )
    assert result.exit_code == 1


def test_cli_build_ambiguous_name_exits_2(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: dict = {}
    _patch_run_pipeline(
        monkeypatch,
        captured=captured,
        raise_=AmbiguousNameError(
            expert_name="John Smith",
            candidates=[
                ExpertCandidate(name="John Smith A", description="poet"),
                ExpertCandidate(name="John Smith B", description="engineer"),
            ],
        ),
    )
    result = runner.invoke(app, ["John Smith", "--output-dir", str(tmp_path)])
    assert result.exit_code == 2
    assert "Ambiguous name" in result.stdout


def test_cli_build_passes_disambiguator_and_assume_flags(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: dict = {}
    _patch_run_pipeline(monkeypatch, captured=captured)
    result = runner.invoke(
        app,
        [
            "Naval Ravikant",
            "--disambiguator",
            "AngelList investor",
            "--assume-unambiguous",
            "--output-dir",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0, result.stdout
    settings: Settings = captured["settings"]
    assert settings.expert_description == "AngelList investor"
    assert settings.assume_unambiguous is True


def test_cli_build_keyboard_interrupt_exits_130(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    captured: dict = {}
    _patch_run_pipeline(monkeypatch, captured=captured, raise_=KeyboardInterrupt())
    result = runner.invoke(
        app, ["Someone", "--output-dir", str(tmp_path)]
    )
    assert result.exit_code == 130
    assert "Cancelled" in result.stdout


def test_main_wrapper_invokes_app(monkeypatch: pytest.MonkeyPatch) -> None:
    called = {"n": 0}

    def _fake_app() -> None:
        called["n"] += 1

    monkeypatch.setattr(cli_module, "app", _fake_app)
    main()
    assert called["n"] == 1
