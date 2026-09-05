from arxiv_research_scout.analysis_context import (
    build_analysis_context,
    choose_abstract,
)

from arxiv_research_scout.models import (
    PaperRecord,
    PaperSections,
)


def make_paper(
    abstract: str = "Metadata abstract.",
) -> PaperRecord:
    return PaperRecord(
        record_id="2608.10000v1",
        title="Example Paper",
        authors=("Alice Example",),
        abstract=abstract,
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


def make_sections(
    abstract: str = "",
) -> PaperSections:
    return PaperSections(
        abstract=abstract,
        introduction="Introduction text.",
        methodology="Method text.",
        experiments="Experiment text.",
        results="Result text.",
        discussion="Discussion text.",
        conclusion="Conclusion text.",
    )


def test_metadata_abstract_is_preferred() -> None:
    paper = make_paper(
        abstract="Official arXiv abstract."
    )

    sections = make_sections(
        abstract="PDF extracted abstract."
    )

    result = choose_abstract(
        paper,
        sections,
    )

    assert result == (
        "Official arXiv abstract."
    )


def test_pdf_abstract_is_fallback() -> None:
    paper = make_paper(
        abstract=""
    )

    sections = make_sections(
        abstract="PDF extracted abstract."
    )

    result = choose_abstract(
        paper,
        sections,
    )

    assert result == (
        "PDF extracted abstract."
    )


def test_build_analysis_context() -> None:
    paper = make_paper(
        abstract="Official abstract."
    )

    sections = make_sections()

    context = build_analysis_context(
        paper,
        sections,
    )

    assert context.record_id == (
        "2608.10000v1"
    )

    assert context.abstract == (
        "Official abstract."
    )

    assert context.methodology == (
        "Method text."
    )

    assert context.experiments == (
        "Experiment text."
    )

    assert context.results == (
        "Result text."
    )

    assert context.pdf_text_available