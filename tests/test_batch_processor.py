from pathlib import Path

import pytest

from arxiv_research_scout.batch_processor import (
    process_paper_batch,
)
from arxiv_research_scout.models import (
    ArxivPaper,
    LLMProviderSettings,
    PaperAnalysisContext,
    PaperAnalysisResult,
    PaperCommitResult,
    PaperProcessingResult,
)


def make_paper(
    arxiv_id: str,
) -> ArxivPaper:
    return ArxivPaper(
        arxiv_id=arxiv_id,
        title=f"Paper {arxiv_id}",
        authors=("Alice Example",),
        abstract="Abstract.",
        published="2026-08-28T10:00:00Z",
        updated="2026-08-28T10:00:00Z",
        categories=("cs.CV",),
        abs_url=(
            f"https://arxiv.org/abs/"
            f"{arxiv_id}"
        ),
        pdf_url=(
            f"https://arxiv.org/pdf/"
            f"{arxiv_id}"
        ),
    )


def make_settings() -> LLMProviderSettings:
    return LLMProviderSettings(
        provider="openai",
        model="test-model",
        api_key_env="OPENAI_API_KEY",
        base_url=None,
        max_output_tokens=2500,
    )


def make_commit(
    paper: ArxivPaper,
    tmp_path: Path,
) -> PaperCommitResult:
    context = PaperAnalysisContext(
        arxiv_id=paper.arxiv_id,
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
            / f"{paper.arxiv_id}.md"
        ),
    )


def make_state() -> dict:
    return {
        "schema_version": 1,
        "last_successful_run_utc": None,
        "processed_ids": [],
    }


def test_all_success_marks_run_successful(
    tmp_path: Path,
) -> None:
    papers = [
        make_paper("2608.10001v1"),
        make_paper("2608.10002v1"),
    ]

    state = make_state()

    marker_called = False
    saver_called = False

    def fake_transaction(
        paper,
        **kwargs,
    ):
        return make_commit(
            paper,
            tmp_path,
        )

    def fake_run_marker(
        staged_state,
        now=None,
    ):
        nonlocal marker_called

        marker_called = True

        staged_state[
            "last_successful_run_utc"
        ] = "success"

    def fake_state_saver(
        state_file,
        staged_state,
    ):
        nonlocal saver_called
        saver_called = True

    result = process_paper_batch(
        papers,
        config={},
        state=state,
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        client=object(),
        settings=make_settings(),
        transaction=fake_transaction,
        run_marker=fake_run_marker,
        state_saver=fake_state_saver,
    )

    assert len(
        result.committed
    ) == 2

    assert not result.failures

    assert (
        result.run_marked_successful
    )

    assert marker_called
    assert saver_called

    assert (
        state[
            "last_successful_run_utc"
        ]
        == "success"
    )


def test_failure_does_not_stop_later_papers(
    tmp_path: Path,
) -> None:
    papers = [
        make_paper("2608.10001v1"),
        make_paper("2608.10002v1"),
        make_paper("2608.10003v1"),
    ]

    processed = []

    def fake_transaction(
        paper,
        **kwargs,
    ):
        processed.append(
            paper.arxiv_id
        )

        if (
            paper.arxiv_id
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

    assert processed == [
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


def test_partial_failure_does_not_mark_run_successful(
    tmp_path: Path,
) -> None:
    paper = make_paper(
        "2608.10001v1"
    )

    marker_called = False

    def failing_transaction(
        paper,
        **kwargs,
    ):
        raise RuntimeError(
            "analysis failed"
        )

    def fake_run_marker(
        staged_state,
        now=None,
    ):
        nonlocal marker_called
        marker_called = True

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
        run_marker=fake_run_marker,
    )

    assert not marker_called

    assert not (
        result.run_marked_successful
    )


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

    failure = result.failures[0]

    assert failure.arxiv_id == (
        "2608.10001v1"
    )

    assert failure.title == (
        "Paper 2608.10001v1"
    )

    assert failure.error == (
        "ValueError: bad paper"
    )


def test_empty_batch_is_successful(
    tmp_path: Path,
) -> None:
    state = make_state()

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

    result = process_paper_batch(
        [],
        config={},
        state=state,
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        client=object(),
        settings=make_settings(),
        run_marker=fake_run_marker,
        state_saver=fake_state_saver,
    )

    assert not result.committed
    assert not result.failures

    assert (
        result.run_marked_successful
    )

    assert (
        state[
            "last_successful_run_utc"
        ]
        == "empty-success"
    )


def test_final_state_save_failure_keeps_old_run_timestamp(
    tmp_path: Path,
) -> None:
    state = make_state()

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
        process_paper_batch(
            [],
            config={},
            state=state,
            state_file=(
                tmp_path / "state.json"
            ),
            reports_dir=tmp_path,
            client=object(),
            settings=make_settings(),
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