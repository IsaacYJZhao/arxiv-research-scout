from __future__ import annotations

from collections.abc import (
    Callable,
    Sequence,
)
from pathlib import Path
from typing import Any

from arxiv_research_scout.models import (
    ArxivPaper,
    BatchProcessingResult,
    LLMProviderSettings,
    PaperCommitResult,
    PaperProcessingFailure,
)
from arxiv_research_scout.paper_transaction import (
    process_and_commit_paper,
)


TransactionFunction = Callable[
    ...,
    PaperCommitResult,
]


def process_paper_batch(
    papers: Sequence[ArxivPaper],
    *,
    config: dict,
    state: dict[str, Any],
    state_file: Path,
    reports_dir: Path,
    client: Any,
    settings: LLMProviderSettings,
    transaction: TransactionFunction = (
        process_and_commit_paper
    ),
) -> BatchProcessingResult:
    """
    Process all selected papers in one batch.

    Responsibilities of this layer:

        Paper A
            ->
        single-paper transaction
            ->
        committed or failed

        Paper B
            ->
        single-paper transaction
            ->
        committed or failed

        ...

    Individual paper failures do not stop later
    papers from being attempted.

    Important transaction boundary:

    This function does NOT call:

        mark_run_successful()
        save_state() for run-level success

    Each successful single-paper transaction may
    persist its processed arXiv ID through
    process_and_commit_paper().

    Run-level success belongs to workflow.py and
    must happen only after the final digest has
    been written successfully.

    The BatchProcessingResult field
    run_marked_successful is retained for backward
    compatibility, but is always False at this
    stage.
    """

    committed: list[
        PaperCommitResult
    ] = []

    failures: list[
        PaperProcessingFailure
    ] = []

    for paper in papers:
        try:
            result = transaction(
                paper,
                config=config,
                state=state,
                state_file=state_file,
                reports_dir=reports_dir,
                client=client,
                settings=settings,
            )

        except Exception as error:
            failures.append(
                PaperProcessingFailure(
                    arxiv_id=paper.arxiv_id,
                    title=paper.title,
                    error=(
                        f"{type(error).__name__}: "
                        f"{error}"
                    ),
                )
            )

            continue

        committed.append(
            result
        )

    return BatchProcessingResult(
        committed=tuple(
            committed
        ),
        failures=tuple(
            failures
        ),
        run_marked_successful=False,
    )