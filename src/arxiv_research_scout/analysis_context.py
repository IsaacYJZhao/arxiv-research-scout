from __future__ import annotations

from arxiv_research_scout.models import (
    PaperRecord,
    PaperAnalysisContext,
    PaperSections,
)


def choose_abstract(
    paper: PaperRecord,
    sections: PaperSections,
) -> str:
    """
    Choose the best available abstract.

    Source metadata is preferred because it is
    usually cleaner and more reliable than text
    extracted from a PDF.
    """

    metadata_abstract = paper.abstract.strip()

    if metadata_abstract:
        return metadata_abstract

    return sections.abstract.strip()


def build_analysis_context(
    paper: PaperRecord,
    sections: PaperSections,
) -> PaperAnalysisContext:
    """
    Combine arXiv metadata and parsed PDF sections
    into one normalized analysis context.
    """

    abstract = choose_abstract(
        paper,
        sections,
    )

    pdf_text_available = any(
        (
            sections.introduction,
            sections.methodology,
            sections.experiments,
            sections.results,
            sections.discussion,
            sections.conclusion,
        )
    )

    return PaperAnalysisContext(
        record_id=paper.record_id,
        title=paper.title,
        authors=paper.authors,
        abstract=abstract,
        introduction=sections.introduction,
        methodology=sections.methodology,
        experiments=sections.experiments,
        results=sections.results,
        discussion=sections.discussion,
        conclusion=sections.conclusion,
        pdf_text_available=pdf_text_available,
        source=paper.source,
        venue=paper.venue,
        doi=paper.doi,
    )