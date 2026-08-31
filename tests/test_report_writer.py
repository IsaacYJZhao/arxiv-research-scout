from pathlib import Path

import pytest

from arxiv_research_scout.models import (
    ArxivPaper,
    LLMProviderSettings,
    PaperAnalysisContext,
    PaperAnalysisResult,
    PaperProcessingResult,
)
from arxiv_research_scout.report_writer import (
    UNAVAILABLE_TEXT,
    build_report_markdown,
    markdown_list,
    safe_report_filename,
    write_report,
)


def make_paper() -> ArxivPaper:
    return ArxivPaper(
        arxiv_id="2608.10000v1",
        title="Example Lung Nodule Paper",
        authors=(
            "Alice Example",
            "Bob Example",
        ),
        abstract=(
            "Official arXiv abstract."
        ),
        published=(
            "2026-08-28T10:00:00Z"
        ),
        updated=(
            "2026-08-28T10:00:00Z"
        ),
        categories=(
            "cs.CV",
            "eess.IV",
        ),
        abs_url=(
            "https://arxiv.org/abs/"
            "2608.10000v1"
        ),
        pdf_url=(
            "https://arxiv.org/pdf/"
            "2608.10000v1"
        ),
    )


def make_context() -> PaperAnalysisContext:
    return PaperAnalysisContext(
        arxiv_id="2608.10000v1",
        title="Example Lung Nodule Paper",
        authors=(
            "Alice Example",
            "Bob Example",
        ),
        abstract=(
            "Official arXiv abstract."
        ),
        introduction="Introduction.",
        methodology="Method evidence.",
        experiments="Experiments.",
        results="Results.",
        discussion="Discussion.",
        conclusion="Conclusion.",
        pdf_text_available=True,
    )


def make_analysis() -> PaperAnalysisResult:
    return PaperAnalysisResult(
        methodology="Method summary.",
        evaluation="Evaluation summary.",
        innovation="Innovation summary.",
        datasets=("LUNA16",),
        metrics=(
            "FROC",
            "Sensitivity",
        ),
        key_results=(
            "Reported improvement.",
        ),
        limitations=(
            "External validation "
            "was not reported."
        ),
        evidence_level="full_text",
        confidence="high",
    )


def make_settings() -> LLMProviderSettings:
    return LLMProviderSettings(
        provider="openai",
        model="test-model",
        api_key_env="OPENAI_API_KEY",
        base_url=None,
        max_output_tokens=2500,
    )


def make_result(
    *,
    pdf_error: str | None = None,
) -> PaperProcessingResult:
    return PaperProcessingResult(
        paper=make_paper(),
        context=make_context(),
        analysis=make_analysis(),
        pdf_error=pdf_error,
    )


def test_safe_report_filename() -> None:
    assert safe_report_filename(
        "cs/0601001v2"
    ) == "cs_0601001v2.md"


def test_empty_report_filename_is_rejected() -> None:
    with pytest.raises(ValueError):
        safe_report_filename(
            "///"
        )


def test_markdown_list_handles_empty_values() -> None:
    assert markdown_list(
        ()
    ) == (
        f"- {UNAVAILABLE_TEXT}"
    )


def test_build_report_contains_core_sections() -> None:
    markdown = build_report_markdown(
        make_result(),
        settings=make_settings(),
    )

    assert (
        "# Example Lung Nodule Paper"
        in markdown
    )

    assert "## Methodology" in markdown
    assert "Method summary." in markdown

    assert "## Evaluation" in markdown
    assert "Evaluation summary." in markdown

    assert "## Innovation" in markdown
    assert "Innovation summary." in markdown

    assert "- LUNA16" in markdown
    assert "- FROC" in markdown

    assert (
        "**Evidence level:** full_text"
        in markdown
    )


def test_pdf_error_is_included_in_report() -> None:
    markdown = build_report_markdown(
        make_result(
            pdf_error=(
                "RuntimeError: download failed"
            )
        ),
        settings=make_settings(),
    )

    assert (
        "## Processing Notes"
        in markdown
    )

    assert (
        "RuntimeError: download failed"
        in markdown
    )

    assert (
        "Unavailable / fallback used"
        in markdown
    )


def test_write_report_creates_markdown_file(
    tmp_path: Path,
) -> None:
    report_path = write_report(
        make_result(),
        settings=make_settings(),
        reports_dir=tmp_path,
    )

    assert report_path.exists()

    assert report_path.name == (
        "2608.10000v1.md"
    )

    content = report_path.read_text(
        encoding="utf-8"
    )

    assert (
        "# Example Lung Nodule Paper"
        in content
    )

    assert not (
        tmp_path
        / "2608.10000v1.md.tmp"
    ).exists()