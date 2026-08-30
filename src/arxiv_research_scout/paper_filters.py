from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from arxiv_research_scout.models import ArxivPaper


VERSION_SUFFIX = re.compile(r"v\d+$")


def normalize_arxiv_id(arxiv_id: str) -> str:
    """
    Remove the arXiv version suffix.

    Examples:
        2608.16855v1 -> 2608.16855
        2608.16855v3 -> 2608.16855
        2608.16855   -> 2608.16855
    """

    return VERSION_SUFFIX.sub(
        "",
        arxiv_id.strip(),
    )


def parse_arxiv_datetime(
    value: str,
) -> datetime:
    """
    Parse an arXiv ISO-8601 timestamp.

    Example:
        2026-08-17T17:38:22Z
    """

    value = value.strip()

    if not value:
        raise ValueError(
            "arXiv datetime must not be empty."
        )

    parsed = datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )

    if parsed.tzinfo is None:
        parsed = parsed.replace(
            tzinfo=timezone.utc
        )

    return parsed.astimezone(
        timezone.utc
    )


def filter_recent_papers(
    papers: list[ArxivPaper],
    lookback_days: int,
    now: datetime | None = None,
) -> list[ArxivPaper]:
    """
    Keep papers published within the requested
    lookback window.
    """

    if lookback_days < 1:
        raise ValueError(
            "lookback_days must be at least 1."
        )

    current_time = (
        now
        if now is not None
        else datetime.now(timezone.utc)
    )

    if current_time.tzinfo is None:
        current_time = current_time.replace(
            tzinfo=timezone.utc
        )

    current_time = current_time.astimezone(
        timezone.utc
    )

    cutoff = current_time - timedelta(
        days=lookback_days
    )

    recent_papers: list[ArxivPaper] = []

    for paper in papers:
        if not paper.published:
            continue

        published_time = parse_arxiv_datetime(
            paper.published
        )

        if published_time >= cutoff:
            recent_papers.append(paper)

    return recent_papers


def deduplicate_papers(
    papers: list[ArxivPaper],
) -> list[ArxivPaper]:
    """
    Deduplicate papers by version-independent
    arXiv ID.

    The first occurrence is retained.
    """

    seen_ids: set[str] = set()
    unique_papers: list[ArxivPaper] = []

    for paper in papers:
        base_id = normalize_arxiv_id(
            paper.arxiv_id
        )

        if base_id in seen_ids:
            continue

        seen_ids.add(base_id)
        unique_papers.append(paper)

    return unique_papers