"""Tests for direct Settings validation."""

from __future__ import annotations

from pathlib import Path

import pytest

from mimeo.config import Settings, openrouter_default_headers


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("expert_name", "   "),
        ("mode", "unsafe"),
        ("format", "pdf"),
        ("max_sources", 0),
        ("max_sources", 201),
        ("concurrency", 0),
        ("concurrency", 21),
        ("max_revisions", -1),
        ("max_revisions", 6),
        ("quality_bar", -1),
        ("quality_bar", 11),
        ("model", ""),
    ],
)
def test_settings_reject_invalid_direct_callers(field: str, value: object) -> None:
    kwargs: dict[str, object] = {
        "expert_name": "Expert",
        "output_dir": Path("output"),
        field: value,
    }
    with pytest.raises(ValueError):
        Settings(**kwargs)  # type: ignore[arg-type]


def test_settings_rejects_empty_enabled_avatar_model() -> None:
    with pytest.raises(ValueError, match="avatar_model"):
        Settings(
            expert_name="Expert",
            output_dir=Path("output"),
            generate_avatar=True,
            avatar_model="",
        )


def test_openrouter_default_headers_are_optional(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("OPENROUTER_SITE_URL", raising=False)
    monkeypatch.delenv("OPENROUTER_APP_NAME", raising=False)
    assert openrouter_default_headers() == {}

    monkeypatch.setenv("OPENROUTER_SITE_URL", "https://example.com")
    monkeypatch.setenv("OPENROUTER_APP_NAME", "mimeo")
    assert openrouter_default_headers() == {
        "HTTP-Referer": "https://example.com",
        "X-Title": "mimeo",
    }
