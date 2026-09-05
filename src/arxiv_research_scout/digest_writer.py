from __future__ import annotations

from datetime import (
    datetime,
    timezone,
)
from pathlib import Path

from arxiv_research_scout.models import (
    BatchProcessingResult,
    LLMProviderSettings,
)
from arxiv_research_scout.report_writer import (
    markdown_list,
    markdown_value,
)
from arxiv_research_scout.runner import (
    ScanResult,
)


def normalize_generated_at(
    generated_at: datetime | None,
) -> datetime:
    """
    Normalize a digest timestamp to UTC.

    If no timestamp is supplied, use the current
    UTC time.
    """

    if generated_at is None:
        return datetime.now(
            timezone.utc
        )

    if generated_at.tzinfo is None:
        return generated_at.replace(
            tzinfo=timezone.utc
        )

    return generated_at.astimezone(
        timezone.utc
    )


def digest_filename(
    generated_at: datetime,
) -> str:
    """
    Generate a deterministic daily digest filename.

    Example:
        2026-08-30.md
    """

    normalized = normalize_generated_at(
        generated_at
    )

    return (
        normalized.strftime(
            "%Y-%m-%d"
        )
        + ".md"
    )


def build_digest_markdown(
    scan: ScanResult,
    batch: BatchProcessingResult,
    *,
    settings: LLMProviderSettings,
    generated_at: datetime | None = None,
) -> str:
    """
    Build one Markdown research digest containing
    the results of a complete research-scout batch.

    No LLM call is made here. The digest only
    summarizes already-produced structured analyses.
    """

    generated = normalize_generated_at(
        generated_at
    )

    run_status = (
        "complete"
        if not batch.failures
        else "partial"
    )

    lines = [
        "# Research Digest",
        "",
        "## Run Summary",
        "",
        (
            f"- **Generated (UTC):** "
            f"{generated.isoformat()}"
        ),
        (
            f"- **Provider:** "
            f"{settings.provider}"
        ),
        (
            f"- **Model:** "
            f"{settings.model}"
        ),
        (
            f"- **Run status:** "
            f"{run_status}"
        ),
        "",
        "## Retrieval Summary",
        "",
    ]

    for source_name, count in scan.source_counts:
        lines.append(
            f"- **Candidates from "
            f"{source_name}:** {count}"
        )

    for source_name, message in scan.source_errors:
        lines.append(
            f"- **{source_name} FAILED:** "
            f"{message}"
        )

    lines += [
        (
            f"- **Candidates retrieved:** "
            f"{scan.candidate_count}"
        ),
        (
            f"- **Recent papers:** "
            f"{scan.recent_count}"
        ),
        (
            f"- **After ID dedup:** "
            f"{scan.unique_count}"
        ),
        (
            f"- **Unprocessed papers:** "
            f"{scan.unprocessed_count}"
        ),
        (
            f"- **Relevant papers:** "
            f"{scan.relevant_count}"
        ),
        (
            f"- **Selected for analysis:** "
            f"{len(scan.selected_papers)}"
        ),
        (
            f"- **Successfully analyzed:** "
            f"{len(batch.committed)}"
        ),
        (
            f"- **Failed:** "
            f"{len(batch.failures)}"
        ),
    ]

    if not batch.committed:
        lines.extend(
            [
                "",
                "## Papers",
                "",
                (
                    "No papers were successfully "
                    "analyzed in this run."
                ),
            ]
        )

    for index, committed in enumerate(
        batch.committed,
        start=1,
    ):
        processing = (
            committed.processing
        )

        paper = processing.paper
        analysis = processing.analysis

        lines.extend(
            [
                "",
                (
                    f"## {index}. "
                    f"{paper.title}"
                ),
                "",
                (
                    f"- **Source:** "
                    f"{paper.source}"
                    + (
                        f" | {paper.venue}"
                        if paper.venue
                        else ""
                    )
                ),
                (
                    f"- **Paper ID:** "
                    f"{paper.record_id}"
                ),
                (
                    f"- **DOI:** "
                    f"{paper.doi or 'Not reported'}"
                ),
                (
                    f"- **Evidence:** "
                    + (
                        "full text"
                        if paper.full_text_available
                        else "abstract only"
                    )
                ),
                (
                    f"- **Authors:** "
                    f"{', '.join(paper.authors)}"
                ),
                (
                    f"- **Published:** "
                    f"{paper.published}"
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
                    f"- **Abstract URL:** "
                    f"{paper.abs_url}"
                ),
                (
                    f"- **Paper report:** "
                    f"{committed.report_path}"
                ),
                "",
                "### Methodology",
                "",
                markdown_value(
                    analysis.methodology
                ),
                "",
                "### Evaluation",
                "",
                markdown_value(
                    analysis.evaluation
                ),
                "",
                "### Innovation",
                "",
                markdown_value(
                    analysis.innovation
                ),
                "",
                "### Datasets",
                "",
                markdown_list(
                    analysis.datasets
                ),
                "",
                "### Metrics",
                "",
                markdown_list(
                    analysis.metrics
                ),
                "",
                "### Key Results",
                "",
                markdown_list(
                    analysis.key_results
                ),
                "",
                "### Limitations",
                "",
                markdown_value(
                    analysis.limitations
                ),
            ]
        )

        if processing.pdf_error is not None:
            lines.extend(
                [
                    "",
                    "### Processing Note",
                    "",
                    (
                        "PDF processing failed or "
                        "was incomplete; fallback "
                        "evidence was used."
                    ),
                ]
            )

    if batch.failures:
        lines.extend(
            [
                "",
                "## Processing Failures",
                "",
            ]
        )

        for failure in batch.failures:
            lines.extend(
                [
                    (
                        f"### {failure.record_id} "
                        f"— {failure.title}"
                    ),
                    "",
                    (
                        f"- **Error:** "
                        f"{failure.error}"
                    ),
                    "",
                ]
            )

    return (
        "\n".join(lines).rstrip()
        + "\n"
    )


def write_digest(
    scan: ScanResult,
    batch: BatchProcessingResult,
    *,
    settings: LLMProviderSettings,
    digests_dir: Path,
    generated_at: datetime | None = None,
) -> Path:
    """
    Atomically write one daily research digest.
    """

    generated = normalize_generated_at(
        generated_at
    )

    digests_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    digest_path = (
        digests_dir
        / digest_filename(
            generated
        )
    )

    temp_path = digest_path.with_suffix(
        digest_path.suffix + ".tmp"
    )

    markdown = build_digest_markdown(
        scan,
        batch,
        settings=settings,
        generated_at=generated,
    )

    temp_path.write_text(
        markdown,
        encoding="utf-8",
    )

    temp_path.replace(
        digest_path
    )

    return digest_path