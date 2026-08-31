from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from arxiv_research_scout.llm_provider import (
    create_provider_client,
    load_provider_api_key,
    resolve_provider_settings,
)
from arxiv_research_scout.models import (
    ArxivPaper,
    LLMProviderSettings,
    ManualAnalysisResult,
    PaperProcessingResult,
)
from arxiv_research_scout.paper_lookup import (
    find_arxiv_paper,
)
from arxiv_research_scout.paper_processor import (
    process_paper,
)
from arxiv_research_scout.report_writer import (
    write_report,
)


PaperLookupFunction = Callable[
    ...,
    ArxivPaper,
]

ProcessorFunction = Callable[
    ...,
    PaperProcessingResult,
]

ApiKeyLoader = Callable[
    ...,
    str,
]

ClientFactory = Callable[
    ...,
    Any,
]

ReportWriterFunction = Callable[
    ...,
    Path,
]


def analyze_single_paper(
    arxiv_id: str,
    *,
    config: dict,
    reports_root: Path,
    provider_override: str | None = None,
    model_override: str | None = None,
    paper_lookup: PaperLookupFunction = (
        find_arxiv_paper
    ),
    processor: ProcessorFunction = (
        process_paper
    ),
    api_key_loader: ApiKeyLoader = (
        load_provider_api_key
    ),
    client_factory: ClientFactory = (
        create_provider_client
    ),
    report_writer: ReportWriterFunction = (
        write_report
    ),
) -> ManualAnalysisResult:
    """
    Analyze exactly one requested arXiv paper.

    This workflow deliberately does NOT modify
    .state/state.json.

    Reports are stored under:

        reports/manual/<provider>/
    """

    settings = resolve_provider_settings(
        config,
        provider_override=provider_override,
        model_override=model_override,
    )

    paper = paper_lookup(
        arxiv_id
    )

    api_key = api_key_loader(
        settings
    )

    client = client_factory(
        settings,
        api_key=api_key,
    )

    processing = processor(
        paper,
        config=config,
        client=client,
        settings=settings,
    )

    manual_reports_dir = (
        reports_root
        / "manual"
        / settings.provider
    )

    report_path = report_writer(
        processing,
        settings=settings,
        reports_dir=manual_reports_dir,
    )

    return ManualAnalysisResult(
        processing=processing,
        report_path=report_path,
        settings=settings,
    )