from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

from arxiv_research_scout.models import (
    PaperRecord,
    LLMProviderSettings,
    PaperCommitResult,
    PaperProcessingResult,
)
from arxiv_research_scout.paper_processor import (
    process_paper,
)
from arxiv_research_scout.report_writer import (
    write_report,
)
from arxiv_research_scout.state_manager import (
    mark_paper_processed,
    save_state,
)


ProcessorFunction = Callable[
    ...,
    PaperProcessingResult,
]

ReportWriterFunction = Callable[
    ...,
    Path,
]

StateMarkerFunction = Callable[
    [dict[str, Any], PaperRecord],
    None,
]

StateSaverFunction = Callable[
    [Path, dict[str, Any]],
    None,
]


def process_and_commit_paper(
    paper: PaperRecord,
    *,
    config: dict,
    state: dict[str, Any],
    state_file: Path,
    reports_dir: Path,
    client: Any,
    settings: LLMProviderSettings,
    processor: ProcessorFunction = process_paper,
    report_writer: ReportWriterFunction = write_report,
    state_marker: StateMarkerFunction = (
        mark_paper_processed
    ),
    state_saver: StateSaverFunction = save_state,
) -> PaperCommitResult:
    """
    Process and transactionally commit one paper.

    Commit order:

        process paper
            ->
        write report
            ->
        copy current state
            ->
        mark copied state as processed
            ->
        persist copied state
            ->
        update caller's in-memory state

    The original in-memory state is not modified
    unless state persistence succeeds.

    mark_run_successful() is deliberately NOT called
    here. Run-level success belongs to the batch
    orchestration layer.
    """

    processing = processor(
        paper,
        config=config,
        client=client,
        settings=settings,
    )

    report_path = report_writer(
        processing,
        settings=settings,
        reports_dir=reports_dir,
    )

    staged_state = deepcopy(
        state
    )

    state_marker(
        staged_state,
        paper,
    )

    state_saver(
        state_file,
        staged_state,
    )

    # Only update the caller's state after the
    # staged copy has been persisted successfully.
    state.clear()
    state.update(
        staged_state
    )

    return PaperCommitResult(
        processing=processing,
        report_path=report_path,
    )