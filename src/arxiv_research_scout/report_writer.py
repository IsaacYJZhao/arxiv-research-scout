from __future__ import annotations

import re
from pathlib import Path

from arxiv_research_scout.models import (
    LLMProviderSettings,
    PaperProcessingResult,
)
from arxiv_research_scout.paper_filters import (
    record_key,
)
from arxiv_research_scout.paths import (
    resolve_project_path,
)


UNAVAILABLE_TEXT = (
    "Not reported in the available evidence."
)


def safe_report_filename(
    record_id: str,
) -> str:
    """
    Convert a record key into a safe Markdown filename.

    The key carries the source, so reports from
    different databases cannot collide, and the colon
    that separates them is not a legal filename
    character on Windows.

    Examples:
        arxiv:2608.12345     -> arxiv_2608.12345.md
        europepmc:42675277   -> europepmc_42675277.md
        doi:10.1007/s10278-1 -> doi_10.1007_s10278-1.md
    """

    cleaned = re.sub(
        r"[^A-Za-z0-9._-]+",
        "_",
        record_id.strip(),
    )

    cleaned = cleaned.strip(
        "._-"
    )

    if not cleaned:
        raise ValueError(
            "Cannot create a report filename "
            "from an empty arXiv ID."
        )

    return f"{cleaned}.md"


def markdown_value(
    value: str,
) -> str:
    """
    Return a readable Markdown value for an
    optional text field.
    """

    cleaned = value.strip()

    if cleaned:
        return cleaned

    return UNAVAILABLE_TEXT


def markdown_list(
    values: tuple[str, ...],
) -> str:
    """
    Render a tuple of strings as a Markdown list.
    """

    cleaned = tuple(
        value.strip()
        for value in values
        if value.strip()
    )

    if not cleaned:
        return (
            f"- {UNAVAILABLE_TEXT}"
        )

    return "\n".join(
        f"- {value}"
        for value in cleaned
    )


def build_report_markdown(
    result: PaperProcessingResult,
    *,
    settings: LLMProviderSettings,
) -> str:
    """
    Build the final Markdown report for one paper.
    """

    paper = result.paper
    analysis = result.analysis

    authors = ", ".join(
        paper.authors
    )

    categories = ", ".join(
        paper.categories
    )

    if result.pdf_error is None:
        pdf_status = "Available"

    elif paper.full_text_available:
        pdf_status = (
            "Download or parsing failed; "
            "abstract used instead"
        )

    else:
        pdf_status = (
            "No full text available; "
            "abstract only"
        )

    lines = [
        f"# {paper.title}",
        "",
        "## Paper Information",
        "",
        f"- **Source:** {paper.source}",
        f"- **Paper ID:** {paper.record_id}",
        (
            f"- **DOI:** "
            f"{markdown_value(paper.doi)}"
        ),
        (
            f"- **Venue:** "
            f"{markdown_value(paper.venue)}"
        ),
        f"- **Authors:** {authors}",
        f"- **Published:** {paper.published}",
        f"- **Updated:** {paper.updated}",
        f"- **Categories:** {categories}",
        f"- **Landing URL:** {paper.abs_url}",
        (
            f"- **PDF URL:** "
            f"{markdown_value(paper.pdf_url)}"
        ),
        "",
        "## Analysis Information",
        "",
        (
            f"- **Provider:** "
            f"{settings.provider}"
        ),
        (
            f"- **Model:** "
            f"{settings.model}"
        ),
        (
            f"- **Evidence level:** "
            f"{analysis.evidence_level}"
        ),
        (
            f"- **Confidence:** "
            f"{analysis.confidence}"
        ),
        (
            f"- **PDF status:** "
            f"{pdf_status}"
        ),
        "",
        "## Methodology",
        "",
        markdown_value(
            analysis.methodology
        ),
        "",
        "## Evaluation",
        "",
        markdown_value(
            analysis.evaluation
        ),
        "",
        "## Innovation",
        "",
        markdown_value(
            analysis.innovation
        ),
        "",
        "## Datasets",
        "",
        markdown_list(
            analysis.datasets
        ),
        "",
        "## Metrics",
        "",
        markdown_list(
            analysis.metrics
        ),
        "",
        "## Key Results",
        "",
        markdown_list(
            analysis.key_results
        ),
        "",
        "## Limitations",
        "",
        markdown_value(
            analysis.limitations
        ),
    ]

    if result.pdf_error is not None:
        lines.extend(
            [
                "",
                "## Processing Notes",
                "",
                (
                    "The PDF could not be fully "
                    "processed. Analysis used the "
                    "available arXiv metadata and "
                    "other recoverable evidence."
                ),
                "",
                (
                    f"- **PDF error:** "
                    f"{result.pdf_error}"
                ),
            ]
        )

    return (
        "\n".join(lines).rstrip()
        + "\n"
    )


def write_report(
    result: PaperProcessingResult,
    *,
    settings: LLMProviderSettings,
    reports_dir: Path,
) -> Path:
    """
    Atomically write one Markdown report.

    State is intentionally not modified here.
    """

    reports_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    filename = safe_report_filename(
        record_key(result.paper)
    )

    report_path = (
        reports_dir / filename
    )

    temp_path = report_path.with_suffix(
        report_path.suffix + ".tmp"
    )

    markdown = build_report_markdown(
        result,
        settings=settings,
    )

    temp_path.write_text(
        markdown,
        encoding="utf-8",
    )

    temp_path.replace(
        report_path
    )

    return report_path


def resolve_reports_dir(
    config: dict,
) -> Path:
    """
    Resolve the configured report directory safely
    relative to the project root.
    """

    return resolve_project_path(
        config["output"]["reports_dir"]
    )