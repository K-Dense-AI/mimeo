"""Offline tests for :mod:`mimeo.avatar`."""

from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

import httpx
import pytest

from mimeo.avatar import (
    _build_prompt,
    _extract_image,
    generate_avatar,
)
from mimeo.config import Settings

# A tiny 1x1 PNG, base64-encoded. Small enough to paste inline, large
# enough to round-trip through base64 + write_bytes without ceremony.
_TINY_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII="
_TINY_PNG = base64.b64decode(_TINY_PNG_B64)


def _response(
    *,
    images: list[dict[str, Any]] | None = None,
    status: int = 200,
) -> httpx.Response:
    body: dict[str, Any] = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "",
                    "images": images or [],
                }
            }
        ]
    }
    return httpx.Response(
        status,
        json=body,
        request=httpx.Request("POST", "https://openrouter.ai/api/v1/chat/completions"),
    )


def _image_response(
    *,
    data: list[dict[str, Any]] | None = None,
    status: int = 200,
) -> httpx.Response:
    return httpx.Response(
        status,
        json={"data": data or []},
        request=httpx.Request("POST", "https://openrouter.ai/api/v1/images"),
    )


def _client_returning(response: httpx.Response) -> httpx.AsyncClient:
    """Build an ``httpx.AsyncClient`` whose transport always returns ``response``."""

    def handler(_request: httpx.Request) -> httpx.Response:
        return response

    transport = httpx.MockTransport(handler)
    return httpx.AsyncClient(transport=transport)


def _settings(tmp_path: Path, **kwargs: Any) -> Settings:
    defaults: dict[str, Any] = {
        "expert_name": "Ada Lovelace",
        "output_dir": tmp_path,
        "generate_avatar": True,
    }
    defaults.update(kwargs)
    return Settings(**defaults)


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------


def test_build_prompt_includes_description_when_set(tmp_path: Path) -> None:
    s = _settings(tmp_path, expert_description="mathematician, programmer")
    prompt = _build_prompt(s)
    assert "Ada Lovelace" in prompt
    assert "(mathematician, programmer)" in prompt


def test_build_prompt_omits_parenthetical_when_no_description(tmp_path: Path) -> None:
    s = _settings(tmp_path)
    prompt = _build_prompt(s)
    assert "Ada Lovelace" in prompt
    assert "()" not in prompt


# ---------------------------------------------------------------------------
# _extract_image
# ---------------------------------------------------------------------------


def test_extract_image_happy_path_png() -> None:
    body = {
        "choices": [
            {
                "message": {
                    "images": [
                        {"image_url": {"url": f"data:image/png;base64,{_TINY_PNG_B64}"}}
                    ]
                }
            }
        ]
    }
    out = _extract_image(body)
    assert out is not None
    image_bytes, ext = out
    assert image_bytes == _TINY_PNG
    assert ext == "png"


def test_extract_image_reads_images_api_response() -> None:
    body = {
        "data": [
            {
                "b64_json": _TINY_PNG_B64,
                "media_type": "image/png",
            }
        ]
    }
    assert _extract_image(body) == (_TINY_PNG, "png")


def test_extract_image_defaults_missing_media_type_to_png() -> None:
    body = {"data": [{"b64_json": _TINY_PNG_B64}]}
    assert _extract_image(body) == (_TINY_PNG, "png")


def test_extract_image_skips_invalid_images_api_entries() -> None:
    body = {
        "data": [
            "not-an-object",
            {"b64_json": 42},
            {"b64_json": _TINY_PNG_B64, "media_type": "image/svg+xml"},
        ]
    }
    assert _extract_image(body) is None


def test_extract_image_normalizes_jpeg_extension() -> None:
    body = {
        "choices": [
            {
                "message": {
                    "images": [
                        {
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{_TINY_PNG_B64}"
                            }
                        }
                    ]
                }
            }
        ]
    }
    out = _extract_image(body)
    assert out is not None
    _, ext = out
    assert ext == "jpg"


def test_extract_image_returns_none_for_empty_choices() -> None:
    assert _extract_image({}) is None
    assert _extract_image({"choices": []}) is None
    assert _extract_image({"choices": [{}]}) is None


def test_extract_image_returns_none_for_non_dict_message() -> None:
    assert _extract_image({"choices": [{"message": "not-a-dict"}]}) is None


def test_extract_image_returns_none_when_no_images() -> None:
    assert _extract_image({"choices": [{"message": {"content": "hi"}}]}) is None
    assert _extract_image({"choices": [{"message": {"images": []}}]}) is None


def test_extract_image_skips_invalid_entries_and_urls() -> None:
    body = {
        "choices": [
            {
                "message": {
                    "images": [
                        "not-a-dict",
                        {"image_url": {}},
                        {"image_url": {"url": 42}},
                        {"image_url": {"url": "https://example.com/no-data-url.png"}},
                        {
                            "image_url": {
                                "url": f"data:image/png;base64,{_TINY_PNG_B64}"
                            }
                        },
                    ]
                }
            }
        ]
    }
    out = _extract_image(body)
    assert out is not None
    image_bytes, ext = out
    assert image_bytes == _TINY_PNG
    assert ext == "png"


def test_extract_image_skips_undecodable_base64() -> None:
    body = {
        "choices": [
            {
                "message": {
                    "images": [
                        {"image_url": {"url": "data:image/png;base64,!!not-base-64!!"}}
                    ]
                }
            }
        ]
    }
    # The one entry has bad base64; we skip it and return None.
    assert _extract_image(body) is None


def test_extract_image_rejects_untrusted_image_type() -> None:
    body = {
        "choices": [
            {
                "message": {
                    "images": [
                        {
                            "image_url": {
                                "url": f"data:image/svg+xml;base64,{_TINY_PNG_B64}"
                            }
                        }
                    ]
                }
            }
        ]
    }
    assert _extract_image(body) is None


def test_extract_image_rejects_oversized_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr("mimeo.avatar._MAX_AVATAR_BYTES", 4)
    monkeypatch.setattr("mimeo.avatar._MAX_AVATAR_B64_CHARS", 8)
    encoded = base64.b64encode(b"12345").decode()
    body = {
        "choices": [
            {
                "message": {
                    "images": [
                        {"image_url": {"url": f"data:image/png;base64,{encoded}"}}
                    ]
                }
            }
        ]
    }
    assert _extract_image(body) is None


# ---------------------------------------------------------------------------
# generate_avatar
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_generate_avatar_writes_file(tmp_path: Path) -> None:
    s = _settings(tmp_path)
    response = _image_response(
        data=[{"b64_json": _TINY_PNG_B64, "media_type": "image/png"}]
    )
    async with _client_returning(response) as client:
        path = await generate_avatar(settings=s, client=client)
    assert path is not None
    assert path == s.skill_dir / "avatar.png"
    assert path.read_bytes() == _TINY_PNG


@pytest.mark.asyncio
async def test_generate_avatar_honors_destination_override(tmp_path: Path) -> None:
    s = _settings(tmp_path / "generated")
    destination = tmp_path / "exact-skill-dir"
    response = _image_response(
        data=[{"b64_json": _TINY_PNG_B64, "media_type": "image/png"}]
    )
    async with _client_returning(response) as client:
        path = await generate_avatar(
            settings=s,
            client=client,
            destination_dir=destination,
        )
    assert path == destination / "avatar.png"


@pytest.mark.asyncio
async def test_generate_avatar_uses_webp_extension(tmp_path: Path) -> None:
    s = _settings(tmp_path)
    response = _response(
        images=[{"image_url": {"url": f"data:image/webp;base64,{_TINY_PNG_B64}"}}]
    )
    async with _client_returning(response) as client:
        path = await generate_avatar(settings=s, client=client)
    assert path is not None
    assert path.suffix == ".webp"


@pytest.mark.asyncio
async def test_generate_avatar_returns_none_when_no_image(tmp_path: Path) -> None:
    s = _settings(tmp_path)
    response = _image_response(data=[])
    async with _client_returning(response) as client:
        path = await generate_avatar(settings=s, client=client)
    assert path is None
    assert not (s.skill_dir / "avatar.png").exists()


@pytest.mark.asyncio
async def test_generate_avatar_raises_on_http_error(tmp_path: Path) -> None:
    s = _settings(tmp_path)
    response = httpx.Response(
        500,
        json={"error": "internal"},
        request=httpx.Request("POST", "https://openrouter.ai/api/v1/images"),
    )
    async with _client_returning(response) as client:
        with pytest.raises(httpx.HTTPStatusError):
            await generate_avatar(settings=s, client=client)


@pytest.mark.asyncio
async def test_generate_avatar_posts_expected_payload(tmp_path: Path) -> None:
    s = _settings(
        tmp_path,
        expert_description="mathematician",
        avatar_model="openai/gpt-image-1",
    )
    seen: dict[str, Any] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        import json as _json

        seen["url"] = str(request.url)
        seen["headers"] = dict(request.headers)
        seen["json"] = _json.loads(request.content.decode("utf-8"))
        return _image_response(
            data=[{"b64_json": _TINY_PNG_B64, "media_type": "image/png"}]
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        await generate_avatar(settings=s, client=client)

    assert seen["url"].endswith("/images")
    assert seen["headers"].get("authorization", "").startswith("Bearer ")
    body = seen["json"]
    assert body["model"] == "openai/gpt-image-1"
    assert body["n"] == 1
    assert body["resolution"] == "1K"
    assert body["aspect_ratio"] == "1:1"
    assert body["output_format"] == "png"
    assert "Ada Lovelace" in body["prompt"]
    assert "mathematician" in body["prompt"]


@pytest.mark.asyncio
async def test_generate_avatar_constructs_client_when_omitted(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """When ``client`` is ``None``, the function builds its own and closes it."""
    s = _settings(tmp_path)

    class _StubClient:
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            self.closed = False

        async def post(self, *args: Any, **kwargs: Any) -> httpx.Response:
            return _image_response(
                data=[{"b64_json": _TINY_PNG_B64, "media_type": "image/png"}]
            )

        async def aclose(self) -> None:
            self.closed = True

    instances: list[_StubClient] = []

    def _factory(*args: Any, **kwargs: Any) -> _StubClient:
        inst = _StubClient()
        instances.append(inst)
        return inst

    monkeypatch.setattr("mimeo.avatar.httpx.AsyncClient", _factory)

    path = await generate_avatar(settings=s)
    assert path is not None
    assert len(instances) == 1
    assert instances[0].closed is True
