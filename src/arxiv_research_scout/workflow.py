from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from arxiv_research_scout.batch_processor import (
    process_paper_batch,
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


ScanFunction = Callable[..., ScanResult]
BatchFunction = Callable[..., BatchProcessingResult]
ApiKeyLoader = Callable[..., str]
ClientFactory = Callable[..., Any]


@dataclass(frozen=True, slots=True)
class WorkflowRunResult:
    """
    Result of one complete scheduled research run.
    """

    scan: ScanResult
    batch: BatchProcessingResult | None
    settings: LLMProviderSettings | None


def run_research_workflow(
    *,
    config: dict,
    state: dict,
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
) -> WorkflowRunResult:
    """
    Execute one complete research-scout workflow.

    The workflow first performs the arXiv scan.

    If the configured schedule is not due, no LLM
    provider or API key is needed.

    If the run is due but no papers are selected,
    the batch is committed as an empty successful
    run without creating an LLM client.

    If papers are selected, one provider client is
    created and reused for the complete batch.
    """

    scan = scan_function(
        config=config,
        state=state,
        force=force,
        now=now,
    )

    if not scan.due:
        return WorkflowRunResult(
            scan=scan,
            batch=None,
            settings=None,
        )

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

    client = None

    if papers:
        api_key = api_key_loader(
            settings
        )

        client = client_factory(
            settings,
            api_key=api_key,
        )

    batch = batch_function(
        papers,
        config=config,
        state=state,
        state_file=state_file,
        reports_dir=reports_dir,
        client=client,
        settings=settings,
        now=now,
    )

    return WorkflowRunResult(
        scan=scan,
        batch=batch,
        settings=settings,
    )


def workflow_exit_code(
    result: WorkflowRunResult,
) -> int:
    """
    Return a process exit code suitable for local
    execution and GitHub Actions.

    Partial paper failures produce a non-zero exit
    code so automated runs visibly fail.
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

    if result.settings is not None:
        print(
            f"Provider              : "
            f"{result.settings.provider}"
        )

        print(
            f"Model                 : "
            f"{result.settings.model}"
        )

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
        f"{'yes' if batch.run_marked_successful else 'no'}"
    )

    if batch.committed:
        print()
        print("Reports:")

        for committed in batch.committed:
            print(
                f"- {committed.report_path}"
            )

    if batch.failures:
        print()
        print("Failures:")

        for failure in batch.failures:
            print(
                f"- {failure.arxiv_id} | "
                f"{failure.title}"
            )

            print(
                f"  {failure.error}"
            )