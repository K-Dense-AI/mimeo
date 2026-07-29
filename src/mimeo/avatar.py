"""Generate an illustrative avatar portrait for an expert via OpenRouter.

OpenRouter exposes image-capable models through ``POST /api/v1/images``.
Generated images are returned as base64 data in ``data[].b64_json`` and are
decoded straight to ``avatar.<ext>`` in the skill directory.

The feature is strictly optional: any failure here is logged and swallowed
so a flaky image endpoint never breaks the main pipeline.
"""

from __future__ import annotations

import base64
import binascii
import logging
import re
from pathlib import Path
from typing import Any

import httpx

from .config import (
    OPENROUTER_BASE_URL,
    Settings,
    openrouter_default_headers,
    require_openrouter_key,
)

logger = logging.getLogger(__name__)

# Short, neutral brief tuned for "profile-icon-ish" results rather than
# photorealistic likenesses (which image models can get wrong in ways that
# feel disrespectful for real public figures).
_AVATAR_PROMPT_TEMPLATE = (
    "A dignified, painterly head-and-shoulders portrait of {expert}{context}. "
    "Centered composition, looking toward the viewer, warm natural lighting, "
    "clean neutral background, soft editorial illustration style, tasteful "
    "and respectful — suitable as a profile avatar. "
    "Do not render any text, captions, watermarks, logos, or UI chrome."
)


def _build_prompt(settings: Settings) -> str:
    context = f" ({settings.expert_description})" if settings.expert_description else ""
    return _AVATAR_PROMPT_TEMPLATE.format(expert=settings.expert_name, context=context)


# Matches ``data:image/png;base64,AAAA...`` (or jpeg/webp/gif). We keep the
# extension to write the file with the right suffix rather than always
# forcing ``.png`` on a jpeg payload.
_DATA_URL_RE = re.compile(
    r"^data:image/(?P<ext>[\w+-]+);base64,(?P<b64>.+)$", re.DOTALL
)
_ALLOWED_IMAGE_TYPES = {
    "gif": "gif",
    "jpeg": "jpg",
    "jpg": "jpg",
    "png": "png",
    "webp": "webp",
}
_MAX_AVATAR_BYTES = 5 * 1024 * 1024
_MAX_AVATAR_B64_CHARS = ((_MAX_AVATAR_BYTES + 2) // 3) * 4


def _extract_image(body: dict[str, Any]) -> tuple[bytes, str] | None:
    """Pull the first usable image out of an OpenRouter response body.

    Returns ``(bytes, extension)`` on success, or ``None`` if the response
    carried no image payload.
    """
    images = body.get("data") or []
    for entry in images:
        if not isinstance(entry, dict):
            continue
        encoded = entry.get("b64_json")
        if isinstance(encoded, str):
            media_type = entry.get("media_type")
            ext = (
                media_type.removeprefix("image/")
                if isinstance(media_type, str)
                else "png"
            )
            decoded = _decode_image(encoded, ext)
            if decoded is not None:
                return decoded

    # Compatibility with the older chat-completions image response shape.
    try:
        message = body["choices"][0]["message"]
    except (KeyError, IndexError, TypeError):
        return None
    if not isinstance(message, dict):
        return None
    for entry in message.get("images") or []:
        if not isinstance(entry, dict):
            continue
        url = (entry.get("image_url") or {}).get("url")
        if not isinstance(url, str):
            continue
        match = _DATA_URL_RE.match(url)
        if match:
            decoded = _decode_image(match.group("b64"), match.group("ext"))
            if decoded is not None:
                return decoded
    return None


def _decode_image(encoded: str, image_type: str) -> tuple[bytes, str] | None:
    ext = _ALLOWED_IMAGE_TYPES.get(image_type.lower())
    if ext is None or len(encoded) > _MAX_AVATAR_B64_CHARS:
        return None
    try:
        image_bytes = base64.b64decode(encoded, validate=True)
    except (ValueError, TypeError, binascii.Error):
        return None
    if len(image_bytes) > _MAX_AVATAR_BYTES:
        return None
    return image_bytes, ext


async def generate_avatar(
    *,
    settings: Settings,
    client: httpx.AsyncClient | None = None,
    destination_dir: Path | None = None,
) -> Path | None:
    """Generate the expert avatar and write it to ``<skill>/avatar.<ext>``.

    Returns the path on success, or ``None`` if the model declined to
    produce an image. Raises :class:`httpx.HTTPError` on transport errors
    so callers can log and continue; the pipeline wrapper catches these.
    """
    prompt = _build_prompt(settings)
    headers = {
        "Authorization": f"Bearer {require_openrouter_key()}",
        "Content-Type": "application/json",
        **openrouter_default_headers(),
    }
    payload: dict[str, Any] = {
        "model": settings.avatar_model,
        "prompt": prompt,
        "n": 1,
        "resolution": "1K",
        "aspect_ratio": "1:1",
        "output_format": "png",
    }

    owns_client = client is None
    c = client or httpx.AsyncClient(timeout=httpx.Timeout(300.0, connect=30.0))
    try:
        resp = await c.post(
            f"{OPENROUTER_BASE_URL}/images",
            headers=headers,
            json=payload,
        )
        resp.raise_for_status()
        body = resp.json()
    finally:
        if owns_client:
            await c.aclose()

    extracted = _extract_image(body)
    if extracted is None:
        logger.warning(
            "Avatar model %s returned no image payload; skipping.",
            settings.avatar_model,
        )
        return None

    image_bytes, ext = extracted
    target_dir = destination_dir or settings.skill_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    avatar_path = target_dir / f"avatar.{ext}"
    avatar_path.write_bytes(image_bytes)
    logger.info("Avatar written to %s (%d bytes).", avatar_path, len(image_bytes))
    return avatar_path
