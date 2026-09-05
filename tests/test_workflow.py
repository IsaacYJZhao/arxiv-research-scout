from pathlib import Path

import pytest

from arxiv_research_scout.models import (
    PaperRecord,
    BatchProcessingResult,
    PaperProcessingFailure,
)
from arxiv_research_scout.runner import (
    ScanResult,
)
from arxiv_research_scout.workflow import (
    get_digests_dir,
    run_research_workflow,
    workflow_exit_code,
)


def make_config() -> dict:
    return {
        "llm": {
            "default_provider": "deepseek",
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


def make_state() -> dict:
    return {
        "schema_version": 1,
        "last_successful_run_utc": None,
        "processed_ids": [],
    }


def make_paper() -> PaperRecord:
    return PaperRecord(
        record_id="2608.10000v1",
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


def empty_success_batch() -> BatchProcessingResult:
    return BatchProcessingResult(
        committed=(),
        failures=(),
        run_marked_successful=False,
    )


def test_get_digests_dir() -> None:
    assert get_digests_dir(
        Path("reports")
    ) == (
        Path("reports")
        / "digests"
    )


def test_not_due_skips_batch_and_api_key(
    tmp_path: Path,
) -> None:
    batch_called = False
    key_called = False
    digest_called = False

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

        raise AssertionError(
            "Batch must not run."
        )

    def fake_key_loader(
        settings,
    ):
        nonlocal key_called

        key_called = True

        raise AssertionError(
            "API key must not be loaded."
        )

    def fake_digest_writer(
        *args,
        **kwargs,
    ):
        nonlocal digest_called

        digest_called = True

        raise AssertionError(
            "Digest must not be written."
        )

    result = run_research_workflow(
        config=make_config(),
        state=make_state(),
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        scan_function=fake_scan,
        batch_function=fake_batch,
        api_key_loader=fake_key_loader,
        digest_writer=(
            fake_digest_writer
        ),
    )

    assert result.batch is None
    assert result.settings is None
    assert result.digest_path is None

    assert not (
        result.run_marked_successful
    )

    assert not batch_called
    assert not key_called
    assert not digest_called


def test_empty_batch_does_not_need_api_key(
    tmp_path: Path,
) -> None:
    state = make_state()

    digest_path = (
        tmp_path
        / "digests"
        / "digest.md"
    )

    captured = {}

    def fake_scan(**kwargs):
        return make_scan(
            due=True
        )

    def fake_key_loader(
        settings,
    ):
        raise AssertionError(
            "API key should not be loaded."
        )

    def fake_batch(
        papers,
        **kwargs,
    ):
        captured["papers"] = papers
        captured["client"] = (
            kwargs["client"]
        )

        return empty_success_batch()

    def fake_digest_writer(
        scan,
        batch,
        **kwargs,
    ):
        captured["digests_dir"] = (
            kwargs["digests_dir"]
        )

        return digest_path

    def fake_run_marker(
        staged_state,
        now=None,
    ):
        staged_state[
            "last_successful_run_utc"
        ] = "empty-success"

    def fake_state_saver(
        state_file,
        staged_state,
    ):
        return None

    result = run_research_workflow(
        config=make_config(),
        state=state,
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        scan_function=fake_scan,
        batch_function=fake_batch,
        api_key_loader=fake_key_loader,
        digest_writer=(
            fake_digest_writer
        ),
        run_marker=fake_run_marker,
        state_saver=fake_state_saver,
    )

    assert captured["papers"] == []

    assert (
        captured["client"]
        is None
    )

    assert captured[
        "digests_dir"
    ] == (
        tmp_path / "digests"
    )

    assert (
        result.digest_path
        == digest_path
    )

    assert (
        result.run_marked_successful
    )

    assert (
        state[
            "last_successful_run_utc"
        ]
        == "empty-success"
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
        captured["api_key"] = (
            api_key
        )

        return fake_client

    def fake_batch(
        papers,
        **kwargs,
    ):
        captured["papers"] = papers
        captured["client"] = (
            kwargs["client"]
        )

        return empty_success_batch()

    def fake_digest_writer(
        *args,
        **kwargs,
    ):
        return (
            tmp_path
            / "digest.md"
        )

    def fake_run_marker(
        staged_state,
        now=None,
    ):
        staged_state[
            "last_successful_run_utc"
        ] = "success"

    def fake_state_saver(
        state_file,
        staged_state,
    ):
        return None

    run_research_workflow(
        config=make_config(),
        state=make_state(),
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
        digest_writer=(
            fake_digest_writer
        ),
        run_marker=fake_run_marker,
        state_saver=fake_state_saver,
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

    assert (
        captured["key_provider"]
        == "deepseek"
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
        return empty_success_batch()

    def fake_digest_writer(
        *args,
        **kwargs,
    ):
        return (
            tmp_path
            / "digest.md"
        )

    def fake_run_marker(
        staged_state,
        now=None,
    ):
        staged_state[
            "last_successful_run_utc"
        ] = "success"

    def fake_state_saver(
        state_file,
        staged_state,
    ):
        return None

    run_research_workflow(
        config=make_config(),
        state=make_state(),
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        provider_override="openai",
        model_override=(
            "temporary-model"
        ),
        scan_function=fake_scan,
        batch_function=fake_batch,
        api_key_loader=fake_key_loader,
        client_factory=(
            fake_client_factory
        ),
        digest_writer=(
            fake_digest_writer
        ),
        run_marker=fake_run_marker,
        state_saver=fake_state_saver,
    )

    settings = captured[
        "settings"
    ]

    assert (
        settings.provider
        == "openai"
    )

    assert (
        settings.model
        == "temporary-model"
    )


def test_partial_failure_writes_digest_but_does_not_mark_run(
    tmp_path: Path,
) -> None:
    paper = make_paper()

    state = make_state()

    failure = (
        PaperProcessingFailure(
            record_id=(
                paper.record_id
            ),
            title=paper.title,
            error=(
                "RuntimeError: failed"
            ),
        )
    )

    digest_called = False
    marker_called = False
    saver_called = False

    digest_path = (
        tmp_path / "partial.md"
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

    def fake_digest_writer(
        *args,
        **kwargs,
    ):
        nonlocal digest_called

        digest_called = True

        return digest_path

    def fake_run_marker(
        staged_state,
        now=None,
    ):
        nonlocal marker_called

        marker_called = True

    def fake_state_saver(
        state_file,
        staged_state,
    ):
        nonlocal saver_called

        saver_called = True

    result = run_research_workflow(
        config=make_config(),
        state=state,
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        scan_function=fake_scan,
        batch_function=fake_batch,
        digest_writer=(
            fake_digest_writer
        ),
        run_marker=fake_run_marker,
        state_saver=fake_state_saver,
    )

    assert digest_called

    assert (
        result.digest_path
        == digest_path
    )

    assert not (
        result.run_marked_successful
    )

    assert not marker_called
    assert not saver_called

    assert (
        state[
            "last_successful_run_utc"
        ]
        is None
    )

    assert (
        workflow_exit_code(
            result
        )
        == 1
    )


def test_digest_failure_does_not_mark_run_successful(
    tmp_path: Path,
) -> None:
    state = make_state()

    marker_called = False
    saver_called = False

    def fake_scan(**kwargs):
        return make_scan(
            due=True
        )

    def fake_batch(
        papers,
        **kwargs,
    ):
        return empty_success_batch()

    def failing_digest_writer(
        *args,
        **kwargs,
    ):
        raise RuntimeError(
            "digest failed"
        )

    def fake_run_marker(
        staged_state,
        now=None,
    ):
        nonlocal marker_called

        marker_called = True

    def fake_state_saver(
        state_file,
        staged_state,
    ):
        nonlocal saver_called

        saver_called = True

    with pytest.raises(
        RuntimeError,
        match="digest failed",
    ):
        run_research_workflow(
            config=make_config(),
            state=state,
            state_file=(
                tmp_path / "state.json"
            ),
            reports_dir=tmp_path,
            scan_function=fake_scan,
            batch_function=fake_batch,
            digest_writer=(
                failing_digest_writer
            ),
            run_marker=fake_run_marker,
            state_saver=(
                fake_state_saver
            ),
        )

    assert not marker_called
    assert not saver_called

    assert (
        state[
            "last_successful_run_utc"
        ]
        is None
    )


def test_successful_run_order_is_batch_digest_marker_save(
    tmp_path: Path,
) -> None:
    paper = make_paper()

    state = make_state()

    call_order = []

    def fake_scan(**kwargs):
        return make_scan(
            due=True,
            papers=(paper,),
        )

    def fake_key_loader(
        settings,
    ):
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
        call_order.append(
            "batch"
        )

        return empty_success_batch()

    def fake_digest_writer(
        *args,
        **kwargs,
    ):
        call_order.append(
            "digest"
        )

        return (
            tmp_path
            / "digest.md"
        )

    def fake_run_marker(
        staged_state,
        now=None,
    ):
        call_order.append(
            "run_marker"
        )

        staged_state[
            "last_successful_run_utc"
        ] = "success"

    def fake_state_saver(
        state_file,
        staged_state,
    ):
        call_order.append(
            "state_saver"
        )

    result = run_research_workflow(
        config=make_config(),
        state=state,
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
        digest_writer=(
            fake_digest_writer
        ),
        run_marker=fake_run_marker,
        state_saver=fake_state_saver,
    )

    assert call_order == [
        "batch",
        "digest",
        "run_marker",
        "state_saver",
    ]

    assert (
        result.run_marked_successful
    )


def test_final_state_save_failure_keeps_old_run_timestamp(
    tmp_path: Path,
) -> None:
    state = make_state()

    def fake_scan(**kwargs):
        return make_scan(
            due=True
        )

    def fake_batch(
        papers,
        **kwargs,
    ):
        return empty_success_batch()

    def fake_digest_writer(
        *args,
        **kwargs,
    ):
        return (
            tmp_path
            / "digest.md"
        )

    def fake_run_marker(
        staged_state,
        now=None,
    ):
        staged_state[
            "last_successful_run_utc"
        ] = "new-value"

    def failing_state_saver(
        state_file,
        staged_state,
    ):
        raise OSError(
            "final state save failed"
        )

    with pytest.raises(
        OSError,
        match=(
            "final state save failed"
        ),
    ):
        run_research_workflow(
            config=make_config(),
            state=state,
            state_file=(
                tmp_path / "state.json"
            ),
            reports_dir=tmp_path,
            scan_function=fake_scan,
            batch_function=fake_batch,
            digest_writer=(
                fake_digest_writer
            ),
            run_marker=fake_run_marker,
            state_saver=(
                failing_state_saver
            ),
        )

    assert (
        state[
            "last_successful_run_utc"
        ]
        is None
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
        return empty_success_batch()

    def fake_digest_writer(
        *args,
        **kwargs,
    ):
        return (
            tmp_path
            / "digest.md"
        )

    def fake_run_marker(
        staged_state,
        now=None,
    ):
        staged_state[
            "last_successful_run_utc"
        ] = "success"

    def fake_state_saver(
        state_file,
        staged_state,
    ):
        return None

    result = run_research_workflow(
        config=make_config(),
        state=make_state(),
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        scan_function=fake_scan,
        batch_function=fake_batch,
        digest_writer=(
            fake_digest_writer
        ),
        run_marker=fake_run_marker,
        state_saver=fake_state_saver,
    )

    assert (
        workflow_exit_code(
            result
        )
        == 0
    )