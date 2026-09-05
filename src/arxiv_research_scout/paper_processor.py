from __future__ import annotations

from collections.abc import Callable
from typing import Any

from arxiv_research_scout.analysis_context import (
    build_analysis_context,
)
from arxiv_research_scout.analyzer import (
    analyze_with_client,
)
from arxiv_research_scout.models import (
    PaperRecord,
    LLMProviderSettings,
    PaperAnalysisResult,
    PaperProcessingResult,
    PaperSections,
)
from arxiv_research_scout.pdf_reader import (
    fetch_pdf_text,
)
from arxiv_research_scout.section_parser import (
    parse_sections,
)


PdfFetcher = Callable[..., str]

SectionParser = Callable[
    [str],
    PaperSections,
]

AnalyzerFunction = Callable[
    ...,
    PaperAnalysisResult,
]


def build_abstract_only_result(
    paper: PaperRecord,
    *,
    config: dict,
    client: Any,
    settings: LLMProviderSettings,
    analyzer: AnalyzerFunction,
    reason: str,
) -> PaperProcessingResult:
    """
    Analyze a paper for which no full text exists.

    The analyzer still runs, so the paper appears in the
    digest with structured fields, but evidence_level
    will report abstract_only and the report records why.
    """

    context = build_analysis_context(
        paper,
        PaperSections(),
    )

    if not context.abstract.strip():
        raise ValueError(
            "No analyzable paper evidence "
            "is available."
        )

    analysis = analyzer(
        context,
        client=client,
        settings=settings,
        output_language=(
            config["output"]["language"]
        ),
        max_context_chars=(
            config["llm"][
                "max_context_chars"
            ]
        ),
    )

    return PaperProcessingResult(
        paper=paper,
        context=context,
        analysis=analysis,
        pdf_error=reason,
    )


def process_paper(
    paper: PaperRecord,
    *,
    config: dict,
    client: Any,
    settings: LLMProviderSettings,
    pdf_fetcher: PdfFetcher = fetch_pdf_text,
    section_parser: SectionParser = parse_sections,
    analyzer: AnalyzerFunction = analyze_with_client,
) -> PaperProcessingResult:
    """
    Process one arXiv paper.

    Pipeline:
        PDF download
            ->
        section parsing
            ->
        analysis context
            ->
        LLM analysis

    If PDF download or parsing fails, the pipeline
    falls back to the arXiv metadata abstract.

    LLM failures are deliberately NOT swallowed.
    The caller must know that analysis failed so that
    the paper is not marked as processed.
    """

    pdf_config = config["pdf"]
    llm_config = config["llm"]

    pdf_error: str | None = None

    if not paper.pdf_url:
        # Closed-access journal articles are indexed
        # without a downloadable PDF. Their record is
        # still worth analyzing from the abstract, but
        # attempting a download would only produce a
        # misleading network error.
        return build_abstract_only_result(
            paper,
            config=config,
            client=client,
            settings=settings,
            analyzer=analyzer,
            reason=(
                "No downloadable full text is "
                "available for this record."
            ),
        )

    try:
        pdf_text = pdf_fetcher(
            paper.pdf_url,
            timeout_seconds=(
                pdf_config[
                    "timeout_seconds"
                ]
            ),
            max_attempts=(
                pdf_config[
                    "max_attempts"
                ]
            ),
            max_download_mb=(
                pdf_config[
                    "max_download_mb"
                ]
            ),
            max_text_chars=(
                pdf_config[
                    "max_text_chars"
                ]
            ),
        )

        sections = section_parser(
            pdf_text
        )

    except Exception as error:
        pdf_error = (
            f"{type(error).__name__}: "
            f"{error}"
        )

        sections = PaperSections()

    context = build_analysis_context(
        paper,
        sections,
    )

    if (
        not context.abstract.strip()
        and not context.pdf_text_available
    ):
        raise ValueError(
            "No analyzable paper evidence "
            "is available."
        )

    analysis = analyzer(
        context,
        client=client,
        settings=settings,
        output_language=(
            config["output"]["language"]
        ),
        max_context_chars=(
            llm_config[
                "max_context_chars"
            ]
        ),
    )

    return PaperProcessingResult(
        paper=paper,
        context=context,
        analysis=analysis,
        pdf_error=pdf_error,
    )