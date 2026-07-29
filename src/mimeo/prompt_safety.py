"""Helpers for clearly delimiting untrusted text in LLM prompts."""

from __future__ import annotations

import re
from collections.abc import Mapping

_NEWLINES_RE = re.compile(r"[\r\n]+")


def sanitize_prompt_metadata(value: str) -> str:
    """Keep untrusted metadata on one inert line."""
    return _NEWLINES_RE.sub(" ", value).replace("```", "` ` `").strip()


def _escape_tag_boundaries(tag: str, text: str) -> str:
    opening = re.compile(rf"<\s*{re.escape(tag)}\b", re.IGNORECASE)
    closing = re.compile(rf"<\s*/\s*{re.escape(tag)}\b", re.IGNORECASE)
    text = opening.sub(f"< {tag}", text)
    return closing.sub(f"< /{tag}", text)


def wrap_untrusted_block(
    tag: str,
    text: str,
    *,
    attributes: Mapping[str, str] | None = None,
) -> str:
    """Wrap source data in a tag it cannot close from inside."""
    if not tag.replace("_", "").isalnum():
        raise ValueError(
            "Prompt tag must contain only letters, numbers, or underscores"
        )
    attrs = ""
    if attributes:
        attrs = "".join(
            f' {key}="{sanitize_prompt_metadata(value).replace(chr(34), "&quot;")}"'
            for key, value in sorted(attributes.items())
        )
    escaped = _escape_tag_boundaries(tag, text)
    return f"<{tag}{attrs}>\n{escaped}\n</{tag}>"
