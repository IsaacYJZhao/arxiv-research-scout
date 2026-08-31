from __future__ import annotations

from collections.abc import (
    Callable,
    Sequence,
)
from copy import deepcopy
from datetime import datetime
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
from arxiv_research_scout.state_manager import (
    mark_run_successful,
    save_state,
)


TransactionFunction = Callable[
    ...,
    PaperCommitResult,
]

RunMarkerFunction = Callable[
    ...,
    None,
]

StateSaverFunction = Callable[
    [Path, dict[str, Any]],
    None,
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
    now: datetime | None = None,
    transaction: TransactionFunction = (
        process_and_commit_paper
    ),
    run_marker: RunMarkerFunction = (
        mark_run_successful
    ),
    state_saver: StateSaverFunction = (
        save_state
    ),
) -> BatchProcessingResult:
    """
    Process a batch of selected papers.

    Individual paper failures do not stop later
    papers from being processed.

    Run-level success is committed only when every
    selected paper succeeds.

    An empty batch is considered a successful run
    because retrieval completed successfully and
    there was simply no new work to process.
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

    # A partial batch must not be marked as
    # successfully completed.
    if failures:
        return BatchProcessingResult(
            committed=tuple(
                committed
            ),
            failures=tuple(
                failures
            ),
            run_marked_successful=False,
        )

    # Run-level state is also staged transactionally.
    staged_state = deepcopy(
        state
    )

    run_marker(
        staged_state,
        now=now,
    )

    state_saver(
        state_file,
        staged_state,
    )

    # Only expose the new run timestamp in memory
    # after it has been persisted successfully.
    state.clear()
    state.update(
        staged_state
    )

    return BatchProcessingResult(
        committed=tuple(
            committed
        ),
        failures=(),
        run_marked_successful=True,
    )