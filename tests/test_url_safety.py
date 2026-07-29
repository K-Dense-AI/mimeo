"""Tests for public-URL and bounded-fetch controls."""

from __future__ import annotations

import socket

import httpx
import pytest

from mimeo.url_safety import (
    UrlSafetyError,
    _validate_ip,
    resolve_public_host,
    safe_http_get,
    validate_public_http_url,
)


@pytest.mark.parametrize(
    "url",
    [
        "file:///etc/passwd",
        "ftp://example.com/file",
        "http://127.0.0.1/admin",
        "http://[::1]/admin",
        "http://10.0.0.1/",
        "http://169.254.169.254/latest/meta-data",
        "http://192.168.1.1/",
        "https://user:password@example.com/",
        "https://metadata.google.internal/",
        "https://service.local/",
    ],
)
def test_validate_public_http_url_rejects_unsafe_urls(url: str) -> None:
    with pytest.raises(UrlSafetyError):
        validate_public_http_url(url)


def test_validate_public_http_url_accepts_public_syntax() -> None:
    assert validate_public_http_url("https://example.com/article?q=1") == (
        "https://example.com/article?q=1"
    )


def test_validate_ip_handles_invalid_mapped_and_public_addresses() -> None:
    with pytest.raises(UrlSafetyError, match="Invalid IP"):
        _validate_ip("not-an-ip")
    with pytest.raises(UrlSafetyError, match="non-public"):
        _validate_ip("::ffff:127.0.0.1")
    _validate_ip("8.8.8.8")


@pytest.mark.parametrize("url", ["http://example.com:bad", "http:///missing-host"])
def test_validate_public_http_url_rejects_malformed_urls(url: str) -> None:
    with pytest.raises(UrlSafetyError):
        validate_public_http_url(url)


def test_validate_public_http_url_resolves_hostname(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, int]] = []
    monkeypatch.setattr(
        "mimeo.url_safety.resolve_public_host",
        lambda host, port: calls.append((host, port)) or ("93.184.216.34",),
    )
    assert validate_public_http_url(
        "http://example.com/path",
        resolve_dns=True,
    ).startswith("http://")
    assert calls == [("example.com", 80)]


def test_resolve_public_host_rejects_private_dns_answer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *_a, **_kw: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.8", 443))
        ],
    )
    with pytest.raises(UrlSafetyError, match="non-public"):
        resolve_public_host("example.com", 443)


def test_resolve_public_host_handles_dns_errors_empty_and_public(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def _dns_error(*_args: object, **_kwargs: object):
        raise socket.gaierror("no dns")

    monkeypatch.setattr(socket, "getaddrinfo", _dns_error)
    with pytest.raises(UrlSafetyError, match="Could not resolve"):
        resolve_public_host("example.com", 443)

    monkeypatch.setattr(socket, "getaddrinfo", lambda *_a, **_kw: [])
    with pytest.raises(UrlSafetyError, match="no addresses"):
        resolve_public_host("example.com", 443)

    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *_a, **_kw: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443))
        ],
    )
    assert resolve_public_host("example.com", 443) == ("8.8.8.8",)


def test_safe_http_get_rechecks_redirect_targets(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "mimeo.url_safety.resolve_public_host",
        lambda *_a, **_kw: ("93.184.216.34",),
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            302,
            headers={"location": "http://127.0.0.1/private"},
            request=request,
        )

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(UrlSafetyError, match="non-public"),
    ):
        safe_http_get("https://example.com/start", client=client)


def test_safe_http_get_caps_response_size(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "mimeo.url_safety.resolve_public_host",
        lambda *_a, **_kw: ("93.184.216.34",),
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"x" * 20, request=request)

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(UrlSafetyError, match="exceeded"),
    ):
        safe_http_get("https://example.com", max_bytes=10, client=client)


def test_safe_http_get_follows_public_redirect_and_returns_body(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "mimeo.url_safety.resolve_public_host",
        lambda *_a, **_kw: ("93.184.216.34",),
    )
    seen: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(str(request.url))
        if request.url.path == "/start":
            return httpx.Response(
                302,
                headers={"location": "/final"},
                request=request,
            )
        return httpx.Response(200, content=b"done", request=request)

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        assert safe_http_get("https://example.com/start", client=client) == b"done"
    assert seen == ["https://example.com/start", "https://example.com/final"]


@pytest.mark.parametrize(
    ("headers", "match"),
    [
        ({}, "no Location"),
        ({"location": "/again"}, "Too many redirects"),
    ],
)
def test_safe_http_get_rejects_bad_redirects(
    headers: dict[str, str],
    match: str,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "mimeo.url_safety.resolve_public_host",
        lambda *_a, **_kw: ("93.184.216.34",),
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers=headers, request=request)

    with (
        httpx.Client(transport=httpx.MockTransport(handler)) as client,
        pytest.raises(UrlSafetyError, match=match),
    ):
        safe_http_get("https://example.com/start", max_redirects=0, client=client)


def test_safe_http_get_closes_owned_client(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        "mimeo.url_safety.resolve_public_host",
        lambda *_a, **_kw: ("93.184.216.34",),
    )
    real_client = httpx.Client
    created: list[httpx.Client] = []

    def factory(*_args: object, **_kwargs: object) -> httpx.Client:
        client = real_client(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, content=b"ok", request=request)
            )
        )
        created.append(client)
        return client

    monkeypatch.setattr("mimeo.url_safety.httpx.Client", factory)
    assert safe_http_get("https://example.com") == b"ok"
    assert created[0].is_closed
