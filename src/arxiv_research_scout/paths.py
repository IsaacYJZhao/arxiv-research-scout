from __future__ import annotations

from pathlib import Path


# --------------------------------------------------
# Project root
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]


# --------------------------------------------------
# Project directories
# --------------------------------------------------

CONFIG_DIR = PROJECT_ROOT / "config"
REPORTS_DIR = PROJECT_ROOT / "reports"
STATE_DIR = PROJECT_ROOT / ".state"


# --------------------------------------------------
# Project files
# --------------------------------------------------

CONFIG_FILE = CONFIG_DIR / "scout.yaml"
STATE_FILE = STATE_DIR / "state.json"


def ensure_runtime_directories() -> None:
    """
    Create directories that may not exist yet.

    This function never relies on machine-specific
    absolute paths.
    """

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    STATE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

def resolve_project_path(
    relative_path: str,
) -> Path:
    """
    Resolve a repository-relative path.

    Absolute paths are intentionally rejected
    to keep the project portable.
    """

    path = Path(relative_path)

    if path.is_absolute():
        raise ValueError(
            "Project paths must be relative."
        )

    resolved = (
        PROJECT_ROOT / path
    ).resolve()

    root = PROJECT_ROOT.resolve()

    if (
        resolved != root
        and root not in resolved.parents
    ):
        raise ValueError(
            "Project path must remain "
            "inside the repository."
        )

    return resolved