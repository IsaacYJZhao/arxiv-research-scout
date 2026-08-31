from pathlib import Path

from arxiv_research_scout.models import (
    ArxivPaper,
    BatchProcessingResult,
    PaperProcessingFailure,
)
from arxiv_research_scout.runner import (
    ScanResult,
)
from arxiv_research_scout.workflow import (
    run_research_workflow,
    workflow_exit_code,
)


def make_config() -> dict:
    return {
        "llm": {
            "default_provider": "openai",
            "max_context_chars": 45000,
            "max_output_tokens": 2500,
            "openai": {
                "model": "gpt-5.6-terra",
            },
            "deepseek": {
                "model": "deepseek-v4-pro",
                "base_url": (
                    "https://api.deepseek.com"
                ),
            },
        }
    }


def make_paper() -> ArxivPaper:
    return ArxivPaper(
        arxiv_id="2608.10000v1",
        title="Example Paper",
        authors=("Alice Example",),
        abstract="Abstract.",
        published="2026-08-28T10:00:00Z",
        updated="2026-08-28T10:00:00Z",
        categories=("cs.CV",),
        abs_url=(
            "https://arxiv.org/abs/"
            "2608.10000v1"
        ),
        pdf_url=(
            "https://arxiv.org/pdf/"
            "2608.10000v1"
        ),
    )


def make_scan(
    *,
    due: bool,
    papers=(),
) -> ScanResult:
    selected = tuple(
        (
            paper,
            10,
            "high",
        )
        for paper in papers
    )

    count = len(selected)

    return ScanResult(
        due=due,
        candidate_count=count,
        recent_count=count,
        unique_count=count,
        unprocessed_count=count,
        relevant_count=count,
        selected_papers=selected,
    )


def test_not_due_skips_batch_and_api_key(
    tmp_path: Path,
) -> None:
    batch_called = False
    key_called = False

    def fake_scan(**kwargs):
        return make_scan(
            due=False
        )

    def fake_batch(
        papers,
        **kwargs,
    ):
        nonlocal batch_called
        batch_called = True
        raise AssertionError

    def fake_key_loader(
        settings,
    ):
        nonlocal key_called
        key_called = True
        raise AssertionError

    result = run_research_workflow(
        config=make_config(),
        state={},
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        scan_function=fake_scan,
        batch_function=fake_batch,
        api_key_loader=fake_key_loader,
    )

    assert result.batch is None
    assert result.settings is None
    assert not batch_called
    assert not key_called


def test_empty_batch_does_not_need_api_key(
    tmp_path: Path,
) -> None:
    captured = {}

    def fake_scan(**kwargs):
        return make_scan(
            due=True
        )

    def fake_key_loader(
        settings,
    ):
        raise AssertionError(
            "API key should not be loaded"
        )

    def fake_batch(
        papers,
        **kwargs,
    ):
        captured["papers"] = papers
        captured["client"] = (
            kwargs["client"]
        )

        return BatchProcessingResult(
            committed=(),
            failures=(),
            run_marked_successful=True,
        )

    result = run_research_workflow(
        config=make_config(),
        state={},
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        scan_function=fake_scan,
        batch_function=fake_batch,
        api_key_loader=fake_key_loader,
    )

    assert captured["papers"] == []
    assert captured["client"] is None

    assert (
        result.batch
        is not None
    )


def test_selected_papers_create_client(
    tmp_path: Path,
) -> None:
    paper = make_paper()

    captured = {}

    fake_client = object()

    def fake_scan(**kwargs):
        return make_scan(
            due=True,
            papers=(paper,),
        )

    def fake_key_loader(
        settings,
    ):
        captured["key_provider"] = (
            settings.provider
        )

        return "secret-key"

    def fake_client_factory(
        settings,
        *,
        api_key,
    ):
        captured["api_key"] = api_key
        return fake_client

    def fake_batch(
        papers,
        **kwargs,
    ):
        captured["papers"] = papers
        captured["client"] = (
            kwargs["client"]
        )

        return BatchProcessingResult(
            committed=(),
            failures=(),
            run_marked_successful=True,
        )

    run_research_workflow(
        config=make_config(),
        state={},
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        scan_function=fake_scan,
        batch_function=fake_batch,
        api_key_loader=fake_key_loader,
        client_factory=(
            fake_client_factory
        ),
    )

    assert captured["papers"] == [
        paper
    ]

    assert (
        captured["client"]
        is fake_client
    )

    assert (
        captured["api_key"]
        == "secret-key"
    )


def test_provider_and_model_override(
    tmp_path: Path,
) -> None:
    paper = make_paper()

    captured = {}

    def fake_scan(**kwargs):
        return make_scan(
            due=True,
            papers=(paper,),
        )

    def fake_key_loader(
        settings,
    ):
        captured["settings"] = (
            settings
        )

        return "secret-key"

    def fake_client_factory(
        settings,
        *,
        api_key,
    ):
        return object()

    def fake_batch(
        papers,
        **kwargs,
    ):
        return BatchProcessingResult(
            committed=(),
            failures=(),
            run_marked_successful=True,
        )

    run_research_workflow(
        config=make_config(),
        state={},
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        provider_override=(
            "deepseek"
        ),
        model_override=(
            "temporary-model"
        ),
        scan_function=fake_scan,
        batch_function=fake_batch,
        api_key_loader=fake_key_loader,
        client_factory=(
            fake_client_factory
        ),
    )

    settings = captured[
        "settings"
    ]

    assert (
        settings.provider
        == "deepseek"
    )

    assert (
        settings.model
        == "temporary-model"
    )


def test_failure_batch_returns_exit_code_one(
    tmp_path: Path,
) -> None:
    failure = PaperProcessingFailure(
        arxiv_id="2608.10000v1",
        title="Example Paper",
        error="RuntimeError: failed",
    )

    def fake_scan(**kwargs):
        return make_scan(
            due=True
        )

    def fake_batch(
        papers,
        **kwargs,
    ):
        return BatchProcessingResult(
            committed=(),
            failures=(failure,),
            run_marked_successful=False,
        )

    result = run_research_workflow(
        config=make_config(),
        state={},
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        scan_function=fake_scan,
        batch_function=fake_batch,
    )

    assert (
        workflow_exit_code(
            result
        )
        == 1
    )


def test_success_returns_exit_code_zero(
    tmp_path: Path,
) -> None:
    def fake_scan(**kwargs):
        return make_scan(
            due=True
        )

    def fake_batch(
        papers,
        **kwargs,
    ):
        return BatchProcessingResult(
            committed=(),
            failures=(),
            run_marked_successful=True,
        )

    result = run_research_workflow(
        config=make_config(),
        state={},
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        scan_function=fake_scan,
        batch_function=fake_batch,
    )

    assert (
        workflow_exit_code(
            result
        )
        == 0
    )