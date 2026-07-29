"""mimeo: turn an expert's body of work into an Agent Skill."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("mimeo")
except PackageNotFoundError:  # pragma: no cover - direct source import
    __version__ = "0+unknown"
