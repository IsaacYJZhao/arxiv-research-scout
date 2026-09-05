from pathlib import Path

from arxiv_research_scout.batch_processor import (
    process_paper_batch,
)
from arxiv_research_scout.models import (
    PaperRecord,
    LLMProviderSettings,
    PaperAnalysisContext,
    PaperAnalysisResult,
    PaperCommitResult,
    PaperProcessingResult,
)


def make_paper(
    record_id: str,
) -> PaperRecord:
    return PaperRecord(
        record_id=record_id,
        title=f"Paper {record_id}",
        authors=("Alice Example",),
        abstract="Abstract.",
        published="2026-08-28T10:00:00Z",
        updated="2026-08-28T10:00:00Z",
        categories=("cs.CV",),
        abs_url=(
            f"https://arxiv.org/abs/"
            f"{record_id}"
        ),
        pdf_url=(
            f"https://arxiv.org/pdf/"
            f"{record_id}"
        ),
    )


def make_settings() -> LLMProviderSettings:
    return LLMProviderSettings(
        provider="deepseek",
        model="deepseek-v4-pro",
        api_key_env="DEEPSEEK_API_KEY",
        base_url=(
            "https://api.deepseek.com"
        ),
        max_output_tokens=2500,
    )


def make_commit(
    paper: PaperRecord,
    tmp_path: Path,
) -> PaperCommitResult:
    context = PaperAnalysisContext(
        record_id=paper.record_id,
        title=paper.title,
        authors=paper.authors,
        abstract=paper.abstract,
        introduction="Introduction.",
        methodology="Method.",
        experiments="Experiments.",
        results="Results.",
        discussion="Discussion.",
        conclusion="Conclusion.",
        pdf_text_available=True,
    )

    analysis = PaperAnalysisResult(
        methodology="Method.",
        evaluation="Evaluation.",
        innovation="Innovation.",
        datasets=(),
        metrics=(),
        key_results=(),
        limitations="Limitations.",
        evidence_level="full_text",
        confidence="high",
    )

    processing = PaperProcessingResult(
        paper=paper,
        context=context,
        analysis=analysis,
        pdf_error=None,
    )

    return PaperCommitResult(
        processing=processing,
        report_path=(
            tmp_path
            / f"{paper.record_id}.md"
        ),
    )


def make_state() -> dict:
    return {
        "schema_version": 1,
        "last_successful_run_utc": None,
        "processed_ids": [],
    }


def test_all_success_returns_committed_papers(
    tmp_path: Path,
) -> None:
    papers = [
        make_paper("2608.10001v1"),
        make_paper("2608.10002v1"),
    ]

    def fake_transaction(
        paper,
        **kwargs,
    ):
        return make_commit(
            paper,
            tmp_path,
        )

    result = process_paper_batch(
        papers,
        config={},
        state=make_state(),
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        client=object(),
        settings=make_settings(),
        transaction=fake_transaction,
    )

    assert len(
        result.committed
    ) == 2

    assert not result.failures

    assert not (
        result.run_marked_successful
    )


def test_failure_does_not_stop_later_papers(
    tmp_path: Path,
) -> None:
    papers = [
        make_paper("2608.10001v1"),
        make_paper("2608.10002v1"),
        make_paper("2608.10003v1"),
    ]

    attempted = []

    def fake_transaction(
        paper,
        **kwargs,
    ):
        attempted.append(
            paper.record_id
        )

        if (
            paper.record_id
            == "2608.10002v1"
        ):
            raise RuntimeError(
                "LLM failed"
            )

        return make_commit(
            paper,
            tmp_path,
        )

    result = process_paper_batch(
        papers,
        config={},
        state=make_state(),
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        client=object(),
        settings=make_settings(),
        transaction=fake_transaction,
    )

    assert attempted == [
        "2608.10001v1",
        "2608.10002v1",
        "2608.10003v1",
    ]

    assert len(
        result.committed
    ) == 2

    assert len(
        result.failures
    ) == 1


def test_failure_information_is_recorded(
    tmp_path: Path,
) -> None:
    paper = make_paper(
        "2608.10001v1"
    )

    def failing_transaction(
        paper,
        **kwargs,
    ):
        raise ValueError(
            "bad paper"
        )

    result = process_paper_batch(
        [paper],
        config={},
        state=make_state(),
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        client=object(),
        settings=make_settings(),
        transaction=(
            failing_transaction
        ),
    )

    assert len(
        result.failures
    ) == 1

    failure = result.failures[0]

    assert failure.record_id == (
        "2608.10001v1"
    )

    assert failure.title == (
        "Paper 2608.10001v1"
    )

    assert failure.error == (
        "ValueError: bad paper"
    )

    assert not (
        result.run_marked_successful
    )


def test_empty_batch_does_not_mark_run_successful(
    tmp_path: Path,
) -> None:
    state = make_state()

    result = process_paper_batch(
        [],
        config={},
        state=state,
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        client=None,
        settings=make_settings(),
    )

    assert not result.committed
    assert not result.failures

    assert not (
        result.run_marked_successful
    )

    assert (
        state[
            "last_successful_run_utc"
        ]
        is None
    )


def test_batch_does_not_modify_run_timestamp(
    tmp_path: Path,
) -> None:
    paper = make_paper(
        "2608.10001v1"
    )

    state = make_state()

    def fake_transaction(
        paper,
        **kwargs,
    ):
        return make_commit(
            paper,
            tmp_path,
        )

    process_paper_batch(
        [paper],
        config={},
        state=state,
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        client=object(),
        settings=make_settings(),
        transaction=fake_transaction,
    )

    assert (
        state[
            "last_successful_run_utc"
        ]
        is None
    )


def test_transaction_receives_shared_runtime_objects(
    tmp_path: Path,
) -> None:
    paper = make_paper(
        "2608.10001v1"
    )

    state = make_state()
    client = object()
    settings = make_settings()

    captured = {}

    def fake_transaction(
        received_paper,
        **kwargs,
    ):
        captured["paper"] = (
            received_paper
        )

        captured["state"] = (
            kwargs["state"]
        )

        captured["state_file"] = (
            kwargs["state_file"]
        )

        captured["reports_dir"] = (
            kwargs["reports_dir"]
        )

        captured["client"] = (
            kwargs["client"]
        )

        captured["settings"] = (
            kwargs["settings"]
        )

        return make_commit(
            received_paper,
            tmp_path,
        )

    state_file = (
        tmp_path / "state.json"
    )

    reports_dir = (
        tmp_path / "reports"
    )

    process_paper_batch(
        [paper],
        config={},
        state=state,
        state_file=state_file,
        reports_dir=reports_dir,
        client=client,
        settings=settings,
        transaction=fake_transaction,
    )

    assert (
        captured["paper"]
        is paper
    )

    assert (
        captured["state"]
        is state
    )

    assert (
        captured["state_file"]
        == state_file
    )

    assert (
        captured["reports_dir"]
        == reports_dir
    )

    assert (
        captured["client"]
        is client
    )

    assert (
        captured["settings"]
        is settings
    )