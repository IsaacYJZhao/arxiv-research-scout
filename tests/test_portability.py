from __future__ import annotations

import re

from arxiv_research_scout.paths import PROJECT_ROOT


WINDOWS_ABSOLUTE_PATH = re.compile(
    r"(?<![A-Za-z0-9])[A-Za-z]:[\\/]"
)

USER_HOME_PATH = re.compile(
    r"(?<![A-Za-z0-9:/])/(?:Users|home)/[^/\s]+/"
)


def test_runtime_files_do_not_contain_hardcoded_paths() -> None:
    """
    Runtime source/config files must not contain
    machine-specific absolute paths.
    """

    files_to_check = list(
        (PROJECT_ROOT / "src").rglob("*.py")
    )

    files_to_check += list(
        (PROJECT_ROOT / "config").rglob("*.yaml")
    )

    files_to_check += list(
        (PROJECT_ROOT / "config").rglob("*.yml")
    )

    for file_path in files_to_check:
        text = file_path.read_text(
            encoding="utf-8"
        )

        assert not WINDOWS_ABSOLUTE_PATH.search(text), (
            f"Hard-coded Windows path found in "
            f"{file_path}"
        )

        assert not USER_HOME_PATH.search(text), (
            f"Hard-coded user-home path found in "
            f"{file_path}"
        )