from arxiv_research_scout.paths import (
    CONFIG_FILE,
    PROJECT_ROOT,
    REPORTS_DIR,
    STATE_FILE,
    resolve_project_path,
)


def test_project_paths_are_derived_from_root() -> None:
    assert CONFIG_FILE == (
        PROJECT_ROOT / "config" / "scout.yaml"
    )

    assert REPORTS_DIR == (
        PROJECT_ROOT / "reports"
    )

    assert STATE_FILE == (
        PROJECT_ROOT / ".state" / "state.json"
    )


def test_project_files_stay_inside_repository() -> None:
    root = PROJECT_ROOT.resolve()

    for path in (
        CONFIG_FILE,
        REPORTS_DIR,
        STATE_FILE,
    ):
        resolved = path.resolve()

        assert (
            resolved == root
            or root in resolved.parents
        )

def test_resolve_project_path() -> None:
    resolved = resolve_project_path(
        ".state/state.json"
    )

    assert resolved == (
        PROJECT_ROOT
        / ".state"
        / "state.json"
    ).resolve()


def test_resolve_project_path_rejects_escape() -> None:
    try:
        resolve_project_path(
            "../../outside.txt"
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError."
        )