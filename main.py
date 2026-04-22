"""Thin shim so ``python main.py`` and ``uv run main.py`` both work."""

from mimeo.cli import app


if __name__ == "__main__":
    app()
