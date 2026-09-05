from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from arxiv_research_scout.batch_processor import (
    process_paper_batch,
)
from arxiv_research_scout.digest_writer import (
    write_digest,
)
from arxiv_research_scout.llm_provider import (
    create_provider_client,
    load_provider_api_key,
    resolve_provider_settings,
)
from arxiv_research_scout.models import (
    BatchProcessingResult,
    LLMProviderSettings,
)
from arxiv_research_scout.runner import (
    ScanResult,
    print_scan_result,
    run_scan,
)
from arxiv_research_scout.state_manager import (
    mark_run_successful,
    save_state,
)


ScanFunction = Callable[
    ...,
    ScanResult,
]

BatchFunction = Callable[
    ...,
    BatchProcessingResult,
]

ApiKeyLoader = Callable[
    ...,
    str,
]

ClientFactory = Callable[
    ...,
    Any,
]

DigestWriterFunction = Callable[
    ...,
    Path,
]

RunMarkerFunction = Callable[
    ...,
    None,
]

StateSaverFunction = Callable[
    [Path, dict[str, Any]],
    None,
]


@dataclass(
    frozen=True,
    slots=True,
)
class WorkflowRunResult:
    """
    Result of one complete research-scout workflow.

    run_marked_successful represents run-level
    success and is independent from the legacy
    BatchProcessingResult.run_marked_successful
    field.
    """

    scan: ScanResult

    batch: (
        BatchProcessingResult
        | None
    )

    settings: (
        LLMProviderSettings
        | None
    )

    digest_path: (
        Path
        | None
    )

    run_marked_successful: bool


def get_digests_dir(
    reports_dir: Path,
) -> Path:
    """
    Derive the digest directory from the configured
    reports directory.

    Example:

        reports/
            ->
        reports/digests/
    """

    return (
        reports_dir
        / "digests"
    )


def run_research_workflow(
    *,
    config: dict,
    state: dict[str, Any],
    state_file: Path,
    reports_dir: Path,
    force: bool = False,
    provider_override: str | None = None,
    model_override: str | None = None,
    now: datetime | None = None,
    scan_function: ScanFunction = run_scan,
    batch_function: BatchFunction = (
        process_paper_batch
    ),
    api_key_loader: ApiKeyLoader = (
        load_provider_api_key
    ),
    client_factory: ClientFactory = (
        create_provider_client
    ),
    digest_writer: DigestWriterFunction = (
        write_digest
    ),
    run_marker: RunMarkerFunction = (
        mark_run_successful
    ),
    state_saver: StateSaverFunction = (
        save_state
    ),
) -> WorkflowRunResult:
    """
    Execute one complete research-scout workflow.

    Transaction order:

        scan
            ->
        process selected papers
            ->
        write individual reports
            ->
        commit processed IDs per successful paper
            ->
        write run digest
            ->
        mark run successful
            ->
        persist final run timestamp

    Important rules:

    1. If the configured schedule is not due, no
       provider, API key, client, digest, or state
       update is required.

    2. If no papers are selected, no API key or LLM
       client is required. An empty digest is still
       written, and the run may be marked successful.

    3. Individual paper failures do not prevent the
       digest from being generated. The digest records
       those failures.

    4. If any paper fails, the run is NOT marked
       successful.

    5. If digest writing fails, run-level state is
       NOT updated.

    6. Run-level state is staged with deepcopy() and
       exposed to the caller only after save_state()
       succeeds.

    7. Successful per-paper processed IDs may already
       have been persisted by paper_transaction.py.
       They remain valid even if a later digest or
       paper fails.
    """

    scan = scan_function(
        config=config,
        state=state,
        force=force,
        now=now,
    )

    # --------------------------------------------------
    # Schedule not due
    # --------------------------------------------------

    if not scan.due:
        return WorkflowRunResult(
            scan=scan,
            batch=None,
            settings=None,
            digest_path=None,
            run_marked_successful=False,
        )

    # --------------------------------------------------
    # Resolve provider
    # --------------------------------------------------

    settings = resolve_provider_settings(
        config,
        provider_override=provider_override,
        model_override=model_override,
    )

    papers = [
        selected[0]
        for selected
        in scan.selected_papers
    ]

    # --------------------------------------------------
    # Create LLM client only when papers exist
    # --------------------------------------------------

    client = None

    if papers:
        api_key = api_key_loader(
            settings
        )

        client = client_factory(
            settings,
            api_key=api_key,
        )

    # --------------------------------------------------
    # Process selected papers
    #
    # Individual successful transactions may update
    # processed_ids, but batch_processor.py does not
    # mark the whole run successful.
    # --------------------------------------------------

    batch = batch_function(
        papers,
        config=config,
        state=state,
        state_file=state_file,
        reports_dir=reports_dir,
        client=client,
        settings=settings,
    )

    # --------------------------------------------------
    # Digest must be written before run success.
    #
    # If this raises, the exception deliberately
    # propagates and last_successful_run_utc remains
    # unchanged.
    # --------------------------------------------------

    digests_dir = get_digests_dir(
        reports_dir
    )

    digest_path = digest_writer(
        scan,
        batch,
        settings=settings,
        digests_dir=digests_dir,
        generated_at=now,
    )

    # --------------------------------------------------
    # Partial batch
    #
    # A digest is still useful and has already been
    # written, but the scheduled run must remain due
    # so failed papers can be retried later.
    # --------------------------------------------------

    if batch.failures:
        return WorkflowRunResult(
            scan=scan,
            batch=batch,
            settings=settings,
            digest_path=digest_path,
            run_marked_successful=False,
        )

    # --------------------------------------------------
    # Complete run success
    #
    # Stage the run timestamp transactionally.
    # --------------------------------------------------

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

    # Only update caller-visible in-memory state after
    # persistent storage succeeds.
    state.clear()

    state.update(
        staged_state
    )

    return WorkflowRunResult(
        scan=scan,
        batch=batch,
        settings=settings,
        digest_path=digest_path,
        run_marked_successful=True,
    )


def workflow_exit_code(
    result: WorkflowRunResult,
) -> int:
    """
    Return a process exit code suitable for local
    execution and GitHub Actions.

    A partial batch is considered a failed automated
    run even though a partial digest may have been
    produced.
    """

    if (
        result.batch is not None
        and result.batch.failures
    ):
        return 1

    return 0


def print_workflow_result(
    config: dict,
    result: WorkflowRunResult,
) -> None:
    """
    Print a human-readable complete-run summary.
    """

    print_scan_result(
        config,
        result.scan,
    )

    # --------------------------------------------------
    # Schedule not due
    # --------------------------------------------------

    if not result.scan.due:
        print()

        print(
            "Run skipped: configured schedule "
            "interval has not elapsed."
        )

        return

    batch = result.batch

    if batch is None:
        return

    print()
    print(
        "===== Processing Summary ====="
    )
    print()

    # --------------------------------------------------
    # Provider information
    # --------------------------------------------------

    if result.settings is not None:
        print(
            f"Provider              : "
            f"{result.settings.provider}"
        )

        print(
            f"Model                 : "
            f"{result.settings.model}"
        )

    # --------------------------------------------------
    # Batch information
    # --------------------------------------------------

    print(
        f"Committed papers      : "
        f"{len(batch.committed)}"
    )

    print(
        f"Failed papers         : "
        f"{len(batch.failures)}"
    )

    print(
        f"Run marked successful : "
        f"{'yes' if result.run_marked_successful else 'no'}"
    )

    # --------------------------------------------------
    # Digest
    # --------------------------------------------------

    if result.digest_path is not None:
        print(
            f"Digest                : "
            f"{result.digest_path}"
        )

    # --------------------------------------------------
    # Individual reports
    # --------------------------------------------------

    if batch.committed:
        print()
        print(
            "Reports:"
        )

        for committed in (
            batch.committed
        ):
            print(
                f"- "
                f"{committed.report_path}"
            )

    # --------------------------------------------------
    # Failures
    # --------------------------------------------------

    if batch.failures:
        print()
        print(
            "Failures:"
        )

        for failure in (
            batch.failures
        ):
            print(
                f"- "
                f"{failure.record_id} "
                f"| "
                f"{failure.title}"
            )

            print(
                f"  "
                f"{failure.error}"
            )