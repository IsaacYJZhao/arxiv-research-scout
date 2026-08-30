from pathlib import PurePosixPath, PureWindowsPath

from arxiv_research_scout.config import load_config


def is_absolute_on_any_platform(value: str) -> bool:
    """
    Detect both Windows and POSIX absolute paths.

    This makes the test behave consistently on
    Windows and GitHub Actions/Linux.
    """

    return (
        PureWindowsPath(value).is_absolute()
        or PurePosixPath(value).is_absolute()
    )


def test_config_loads() -> None:
    config = load_config()

    assert config["topic"]["name"]
    assert config["topic"]["arxiv_query"]
    assert config["topic"]["categories"]


def test_schedule_values_are_valid() -> None:
    config = load_config()

    assert config["schedule"]["run_every_days"] >= 1
    assert config["schedule"]["lookback_days"] >= 1


def test_retrieval_values_are_valid() -> None:
    config = load_config()

    assert config["retrieval"]["max_candidates"] >= 1
    assert config["retrieval"]["max_papers"] >= 1

    assert (
        config["retrieval"]["max_candidates"]
        >= config["retrieval"]["max_papers"]
    )


def test_runtime_paths_in_config_are_relative() -> None:
    config = load_config()

    reports_dir = config["output"]["reports_dir"]
    state_file = config["state"]["file"]

    assert not is_absolute_on_any_platform(reports_dir)
    assert not is_absolute_on_any_platform(state_file)