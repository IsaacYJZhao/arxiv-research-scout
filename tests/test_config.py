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


def test_relevance_values_are_valid() -> None:
    config = load_config()

    relevance = config["relevance"]

    assert relevance["min_score"] >= 0

    assert (
        relevance["high_score"]
        >= relevance["min_score"]
    )

    assert relevance["core_terms"]
    assert relevance["target_terms"]

def test_pdf_values_are_valid() -> None:
    config = load_config()

    pdf = config["pdf"]

    assert pdf["max_download_mb"] >= 1
    assert pdf["max_text_chars"] >= 1000
    assert pdf["timeout_seconds"] >= 1
    assert pdf["max_attempts"] >= 1

def test_llm_values_are_valid() -> None:
    config = load_config()

    llm = config["llm"]

    assert llm["max_context_chars"] >= 1000

    assert llm["default_provider"] in {
        "openai",
        "deepseek",
    }

    assert llm["max_output_tokens"] >= 1

    assert llm["openai"]["model"]

    assert llm["deepseek"]["model"]

    assert (
        llm["deepseek"]["base_url"]
        ==
        "https://api.deepseek.com"
    )