"""Best-effort SSRF and resource controls for local HTTP fetches."""

from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urljoin, urlsplit

import httpx

_BLOCKED_HOSTS = frozenset(
    {
        "localhost",
        "metadata",
        "metadata.google.internal",
    }
)
_REDIRECT_CODES = frozenset({301, 302, 303, 307, 308})
_MAX_REDIRECTS = 5
_MAX_RESPONSE_BYTES = 5 * 1024 * 1024


class UrlSafetyError(ValueError):
    """Raised when a URL is unsafe for local or delegated fetching."""


def _normalize_hostname(hostname: str) -> str:
    return hostname.rstrip(".").lower()


def _is_blocked_hostname(hostname: str) -> bool:
    normalized = _normalize_hostname(hostname)
    return (
        normalized in _BLOCKED_HOSTS
        or normalized.endswith(".localhost")
        or normalized.endswith(".local")
    )


def _validate_ip(address: str) -> None:
    try:
        parsed = ipaddress.ip_address(address)
    except ValueError as exc:
        raise UrlSafetyError(f"Invalid IP address: {address}") from exc
    if isinstance(parsed, ipaddress.IPv6Address) and parsed.ipv4_mapped is not None:
        parsed = parsed.ipv4_mapped
    if not parsed.is_global:
        raise UrlSafetyError(f"URL resolves to a non-public address: {parsed}")


def resolve_public_host(hostname: str, port: int) -> tuple[str, ...]:
    """Resolve a host and reject it if any returned address is non-public."""
    try:
        rows = socket.getaddrinfo(
            hostname,
            port,
            type=socket.SOCK_STREAM,
        )
    except socket.gaierror as exc:
        raise UrlSafetyError(f"Could not resolve URL host: {hostname}") from exc
    addresses = tuple(sorted({str(row[4][0]) for row in rows}))
    if not addresses:
        raise UrlSafetyError(f"URL host resolved to no addresses: {hostname}")
    for address in addresses:
        _validate_ip(address)
    return addresses


def validate_public_http_url(url: str, *, resolve_dns: bool = False) -> str:
    """Validate and return a public HTTP(S) URL.

    Literal private addresses are always rejected. DNS resolution is optional
    so discovery can filter syntax without performing network lookups; local
    fetches enable it immediately before connecting.
    """
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as exc:
        raise UrlSafetyError("Malformed URL") from exc
    if parsed.scheme.lower() not in {"http", "https"}:
        raise UrlSafetyError("Only http and https URLs are allowed")
    if parsed.username is not None or parsed.password is not None:
        raise UrlSafetyError("URLs containing credentials are not allowed")
    if not parsed.hostname:
        raise UrlSafetyError("URL must include a hostname")

    hostname = _normalize_hostname(parsed.hostname)
    if _is_blocked_hostname(hostname):
        raise UrlSafetyError(f"Blocked URL hostname: {hostname}")
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        if resolve_dns:
            resolve_public_host(
                hostname,
                port or (443 if parsed.scheme.lower() == "https" else 80),
            )
    else:
        _validate_ip(hostname)

    return url


def safe_http_get(
    url: str,
    *,
    timeout_s: float = 30.0,
    max_redirects: int = _MAX_REDIRECTS,
    max_bytes: int = _MAX_RESPONSE_BYTES,
    client: httpx.Client | None = None,
) -> bytes:
    """GET a public URL with redirect validation and a response-size cap."""
    owns_client = client is None
    http = client or httpx.Client(
        follow_redirects=False,
        timeout=httpx.Timeout(timeout_s),
    )
    current = url
    try:
        for redirect_count in range(max_redirects + 1):
            validate_public_http_url(current, resolve_dns=True)
            with http.stream(
                "GET",
                current,
                headers={
                    "User-Agent": "mimeo/0.1 (+https://github.com/K-Dense-AI/mimeo)"
                },
            ) as response:
                if response.status_code in _REDIRECT_CODES:
                    location = response.headers.get("location")
                    if not location:
                        raise UrlSafetyError("Redirect response had no Location header")
                    if redirect_count >= max_redirects:
                        raise UrlSafetyError("Too many redirects")
                    current = urljoin(current, location)
                    continue
                response.raise_for_status()
                chunks: list[bytes] = []
                total = 0
                for chunk in response.iter_bytes():
                    total += len(chunk)
                    if total > max_bytes:
                        raise UrlSafetyError(
                            f"HTTP response exceeded {max_bytes} bytes"
                        )
                    chunks.append(chunk)
                return b"".join(chunks)
    finally:
        if owns_client:
            http.close()
    raise UrlSafetyError("Too many redirects")  # pragma: no cover - loop exits above
