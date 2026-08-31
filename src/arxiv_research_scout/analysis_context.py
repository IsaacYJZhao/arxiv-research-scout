from __future__ import annotations

from arxiv_research_scout.models import (
    ArxivPaper,
    PaperAnalysisContext,
    PaperSections,
)


def choose_abstract(
    paper: ArxivPaper,
    sections: PaperSections,
) -> str:
    """
    Choose the best available abstract.

    arXiv metadata is preferred because it is
    usually cleaner and more reliable than text
    extracted from a PDF.
    """

    metadata_abstract = paper.abstract.strip()

    if metadata_abstract:
        return metadata_abstract

    return sections.abstract.strip()


def build_analysis_context(
    paper: ArxivPaper,
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
        arxiv_id=paper.arxiv_id,
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
    )