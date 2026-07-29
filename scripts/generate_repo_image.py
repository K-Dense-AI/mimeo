"""Generate an image that explains this repo via OpenRouter.

Uses openai/gpt-5.4-image-2 through OpenRouter's chat-completions API.
Requires OPENROUTER_API_KEY in the environment (or .env at repo root).

Usage:
    uv run python scripts/generate_repo_image.py
    uv run python scripts/generate_repo_image.py --out output/mimeo-explainer.png
"""

from __future__ import annotations

import argparse
import base64
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parent.parent
MODEL = "openai/gpt-5.4-image-2"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

PROMPT = """Create a clean, modern, WIDE LANDSCAPE (16:9) infographic that explains the "mimeo" repo.
Use the full width of the canvas — a horizontal left-to-right pipeline, not a square grid.

Concept: mimeo clones an expert's way of thinking into a coding agent. Point it at a
name (e.g. Feynman, Naval, Turing) and it reads the internet on your behalf, then emits
a production-ready SKILL.md or AGENTS.md file — plus a painterly avatar portrait of
the expert.

Visually show a left-to-right pipeline with labeled stages:
  1. NAME INPUT  →  2. DISAMBIGUATE  →  3. DISCOVER (web search, 8 intent buckets)
  →  4. FETCH (web + YouTube + audio)  →  5. DISTILL (LLM per source)
  →  6. CLUSTER (merge + rank)  →  7. VERIFY QUOTES  →  8. AUTHOR (SKILL.md / AGENTS.md)
  →  9. CRITIQUE  →  10. AVATAR (OpenRouter image model → painterly portrait)

Aesthetic: minimal, flat-vector, soft pastel palette on off-white background, thin
line icons, clear sans-serif labels, subtle grid. Title at top: "mimeo — clone an
expert's way of thinking into your coding agent". Small subtitle: "Parallel Search +
OpenRouter → SKILL.md / AGENTS.md + avatar.png". No photorealism. Portrait of the
archetypal "expert" as a simple silhouette on the left, flowing into the pipeline,
emerging on the right as two stacked output artifacts: a neatly formatted markdown
file icon (labeled "SKILL.md / AGENTS.md") AND a small framed painterly portrait
thumbnail (labeled "avatar.png") to represent the generated avatar output."""


def main() -> int:
    load_dotenv(REPO_ROOT / ".env")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--out",
        type=Path,
        default=REPO_ROOT / "docs" / "mimeo-explainer.png",
        help="Where to write the generated PNG.",
    )
    parser.add_argument("--model", default=MODEL)
    parser.add_argument(
        "--aspect-ratio",
        default="16:9",
        help="Image aspect ratio (e.g. 16:9, 21:9, 3:2, 1:1). Default: 16:9.",
    )
    parser.add_argument(
        "--image-size",
        default="2K",
        help="Image resolution tier (0.5K, 1K, 2K, 4K). Default: 2K.",
    )
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("error: OPENROUTER_API_KEY not set", file=sys.stderr)
        return 1

    payload = {
        "model": args.model,
        "modalities": ["image", "text"],
        "messages": [{"role": "user", "content": PROMPT}],
        "image_config": {
            "aspect_ratio": args.aspect_ratio,
            "image_size": args.image_size,
        },
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/K-Dense-AI/mimeo",
        "X-Title": "mimeo repo explainer",
    }

    print(f"→ requesting image from {args.model} …")
    with httpx.Client(timeout=300.0) as client:
        resp = client.post(ENDPOINT, json=payload, headers=headers)
        resp.raise_for_status()
        data = resp.json()

    try:
        message = data["choices"][0]["message"]
        images = message.get("images") or []
        if not images:
            print("error: no images returned. full response:", file=sys.stderr)
            print(data, file=sys.stderr)
            return 2
        url = images[0]["image_url"]["url"]
    except (KeyError, IndexError, TypeError) as exc:
        print(f"error: unexpected response shape: {exc}", file=sys.stderr)
        print(data, file=sys.stderr)
        return 2

    # OpenRouter returns either a data: URL with base64 or a hosted URL.
    args.out.parent.mkdir(parents=True, exist_ok=True)
    if url.startswith("data:"):
        b64 = url.split(",", 1)[1]
        args.out.write_bytes(base64.b64decode(b64))
    else:
        with httpx.Client(timeout=120.0) as client:
            img = client.get(url)
            img.raise_for_status()
            args.out.write_bytes(img.content)

    print(f"✓ wrote {args.out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
