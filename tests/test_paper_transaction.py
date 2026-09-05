from pathlib import Path

import pytest

from arxiv_research_scout.models import (
    PaperRecord,
    LLMProviderSettings,
    PaperAnalysisContext,
    PaperAnalysisResult,
    PaperProcessingResult,
)
from arxiv_research_scout.paper_transaction import (
    process_and_commit_paper,
)


def make_paper() -> PaperRecord:
    return PaperRecord(
        record_id="2608.10000v1",
        title="Example Paper",
        authors=("Alice Example",),
        abstract="Official abstract.",
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


def make_context() -> PaperAnalysisContext:
    return PaperAnalysisContext(
        record_id="2608.10000v1",
        title="Example Paper",
        authors=("Alice Example",),
        abstract="Official abstract.",
        introduction="Introduction.",
        methodology="Method.",
        experiments="Experiments.",
        results="Results.",
        discussion="Discussion.",
        conclusion="Conclusion.",
        pdf_text_available=True,
    )


def make_analysis() -> PaperAnalysisResult:
    return PaperAnalysisResult(
        methodology="Method summary.",
        evaluation="Evaluation summary.",
        innovation="Innovation summary.",
        datasets=("LUNA16",),
        metrics=("FROC",),
        key_results=("Result.",),
        limitations="Limitations.",
        evidence_level="full_text",
        confidence="high",
    )


def make_processing() -> PaperProcessingResult:
    return PaperProcessingResult(
        paper=make_paper(),
        context=make_context(),
        analysis=make_analysis(),
        pdf_error=None,
    )


def make_settings() -> LLMProviderSettings:
    return LLMProviderSettings(
        provider="openai",
        model="test-model",
        api_key_env="OPENAI_API_KEY",
        base_url=None,
        max_output_tokens=2500,
    )


def make_state() -> dict:
    return {
        "schema_version": 1,
        "last_successful_run_utc": None,
        "processed_ids": [],
    }


def test_successful_transaction_updates_state(
    tmp_path: Path,
) -> None:
    state = make_state()

    saved = {}

    report_path = (
        tmp_path / "2608.10000v1.md"
    )

    def fake_processor(
        paper,
        **kwargs,
    ):
        return make_processing()

    def fake_report_writer(
        result,
        **kwargs,
    ):
        return report_path

    def fake_state_saver(
        state_file,
        staged_state,
    ):
        saved["state_file"] = (
            state_file
        )

        saved["state"] = dict(
            staged_state
        )

    result = process_and_commit_paper(
        make_paper(),
        config={},
        state=state,
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        client=object(),
        settings=make_settings(),
        processor=fake_processor,
        report_writer=(
            fake_report_writer
        ),
        state_saver=fake_state_saver,
    )

    assert result.report_path == (
        report_path
    )

    assert (
        "arxiv:2608.10000"
        in state["processed_ids"]
    )

    assert (
        saved["state"][
            "processed_ids"
        ]
        == state["processed_ids"]
    )


def test_processing_failure_does_not_change_state(
    tmp_path: Path,
) -> None:
    state = make_state()
    original = dict(state)

    def failing_processor(
        paper,
        **kwargs,
    ):
        raise RuntimeError(
            "processing failed"
        )

    with pytest.raises(
        RuntimeError,
        match="processing failed",
    ):
        process_and_commit_paper(
            make_paper(),
            config={},
            state=state,
            state_file=(
                tmp_path / "state.json"
            ),
            reports_dir=tmp_path,
            client=object(),
            settings=make_settings(),
            processor=(
                failing_processor
            ),
        )

    assert state == original


def test_report_failure_does_not_change_state(
    tmp_path: Path,
) -> None:
    state = make_state()
    original = dict(state)

    save_called = False

    def fake_processor(
        paper,
        **kwargs,
    ):
        return make_processing()

    def failing_report_writer(
        result,
        **kwargs,
    ):
        raise OSError(
            "report failed"
        )

    def fake_state_saver(
        state_file,
        staged_state,
    ):
        nonlocal save_called
        save_called = True

    with pytest.raises(
        OSError,
        match="report failed",
    ):
        process_and_commit_paper(
            make_paper(),
            config={},
            state=state,
            state_file=(
                tmp_path / "state.json"
            ),
            reports_dir=tmp_path,
            client=object(),
            settings=make_settings(),
            processor=fake_processor,
            report_writer=(
                failing_report_writer
            ),
            state_saver=(
                fake_state_saver
            ),
        )

    assert state == original
    assert not save_called


def test_state_save_failure_does_not_change_state(
    tmp_path: Path,
) -> None:
    state = make_state()
    original = dict(state)

    def fake_processor(
        paper,
        **kwargs,
    ):
        return make_processing()

    def fake_report_writer(
        result,
        **kwargs,
    ):
        return (
            tmp_path
            / "2608.10000v1.md"
        )

    def failing_state_saver(
        state_file,
        staged_state,
    ):
        raise OSError(
            "state save failed"
        )

    with pytest.raises(
        OSError,
        match="state save failed",
    ):
        process_and_commit_paper(
            make_paper(),
            config={},
            state=state,
            state_file=(
                tmp_path / "state.json"
            ),
            reports_dir=tmp_path,
            client=object(),
            settings=make_settings(),
            processor=fake_processor,
            report_writer=(
                fake_report_writer
            ),
            state_saver=(
                failing_state_saver
            ),
        )

    assert state == original


def test_existing_processed_ids_are_preserved(
    tmp_path: Path,
) -> None:
    state = make_state()

    state["processed_ids"] = [
        "arxiv:2501.00001",
    ]

    def fake_processor(
        paper,
        **kwargs,
    ):
        return make_processing()

    def fake_report_writer(
        result,
        **kwargs,
    ):
        return (
            tmp_path
            / "2608.10000v1.md"
        )

    def fake_state_saver(
        state_file,
        staged_state,
    ):
        return None

    process_and_commit_paper(
        make_paper(),
        config={},
        state=state,
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        client=object(),
        settings=make_settings(),
        processor=fake_processor,
        report_writer=(
            fake_report_writer
        ),
        state_saver=(
            fake_state_saver
        ),
    )

    assert "arxiv:2501.00001" in (
        state["processed_ids"]
    )

    assert "arxiv:2608.10000" in (
        state["processed_ids"]
    )


def test_transaction_does_not_mark_run_successful(
    tmp_path: Path,
) -> None:
    state = make_state()

    def fake_processor(
        paper,
        **kwargs,
    ):
        return make_processing()

    def fake_report_writer(
        result,
        **kwargs,
    ):
        return (
            tmp_path
            / "2608.10000v1.md"
        )

    def fake_state_saver(
        state_file,
        staged_state,
    ):
        return None

    process_and_commit_paper(
        make_paper(),
        config={},
        state=state,
        state_file=(
            tmp_path / "state.json"
        ),
        reports_dir=tmp_path,
        client=object(),
        settings=make_settings(),
        processor=fake_processor,
        report_writer=(
            fake_report_writer
        ),
        state_saver=(
            fake_state_saver
        ),
    )

    assert (
        state[
            "last_successful_run_utc"
        ]
        is None
    )