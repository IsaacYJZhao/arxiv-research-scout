from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

from arxiv_research_scout.models import PaperRecord


VERSION_SUFFIX = re.compile(r"v\d+$")

DOI_URL_PREFIX = re.compile(
    r"^(?:https?://)?(?:dx\.)?doi\.org/",
    flags=re.IGNORECASE,
)

# Every arXiv submission also carries a DataCite DOI
# of the form 10.48550/arXiv.2608.16855. Europe PMC
# reports it for preprint records, so recognizing it
# is what lets one preprint retrieved from both
# sources collapse into a single paper.
ARXIV_DATACITE_DOI = re.compile(
    r"^10\.48550/arxiv\.(?P<record_id>.+)$",
    flags=re.IGNORECASE,
)


def normalize_arxiv_id(record_id: str) -> str:
    """
    Remove the arXiv version suffix.

    Examples:
        2608.16855v1 -> 2608.16855
        2608.16855v3 -> 2608.16855
        2608.16855   -> 2608.16855
    """

    return VERSION_SUFFIX.sub(
        "",
        record_id.strip(),
    )


def normalize_doi(doi: str) -> str:
    """
    Normalize a DOI for identity comparison.

    The same DOI appears both bare and as a resolver
    URL, and its case is not significant in practice.

    Examples:
        https://doi.org/10.1007/S10278-026-02237-Y
            -> 10.1007/s10278-026-02237-y

        10.1007/s10278-026-02237-y
            -> 10.1007/s10278-026-02237-y
    """

    cleaned = DOI_URL_PREFIX.sub(
        "",
        doi.strip(),
    )

    return cleaned.strip().lower()


def record_key(paper: PaperRecord) -> str:
    """
    Return the cross-source identity of one paper.

    A DOI is preferred, because the same work reaches
    us from more than one source: an arXiv preprint and
    its published journal version share a DOI, and
    Europe PMC indexes preprints alongside journal
    articles.

    Without a DOI the key falls back to the source and
    its native identifier. That is unique within the
    source but cannot detect cross-source duplicates,
    which is the price of a record that carries no DOI.

    Examples:
        doi:10.1007/s10278-026-02237-y
        arxiv:2608.16855
        europepmc:42675277
    """

    doi = normalize_doi(paper.doi)

    if doi:
        datacite = ARXIV_DATACITE_DOI.match(doi)

        if datacite is not None:
            return (
                "arxiv:"
                + normalize_arxiv_id(
                    datacite.group("record_id")
                )
            )

        return f"doi:{doi}"

    source = (
        paper.source.strip().lower()
        or "unknown"
    )

    record_id = paper.record_id.strip()

    if source == "arxiv":
        record_id = normalize_arxiv_id(
            record_id
        )

    return f"{source}:{record_id}"


def parse_arxiv_datetime(
    value: str,
) -> datetime:
    """
    Parse an ISO-8601 timestamp as published by the
    retrieval sources.

    Examples:
        2026-08-17T17:38:22Z
        2026-08-17
    """

    value = value.strip()

    if not value:
        raise ValueError(
            "Publication datetime must not be empty."
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
    papers: list[PaperRecord],
    lookback_days: int,
    now: datetime | None = None,
) -> list[PaperRecord]:
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

    recent_papers: list[PaperRecord] = []

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
    papers: list[PaperRecord],
) -> list[PaperRecord]:
    """
    Deduplicate papers by cross-source identity.

    The first occurrence is retained, so the order in
    which sources are queried matters. arXiv is queried
    first, because a preprint usually has a downloadable
    PDF while the journal version of the same work often
    does not, and a full text produces a much stronger
    analysis than an abstract.
    """

    seen_keys: set[str] = set()
    unique_papers: list[PaperRecord] = []

    for paper in papers:
        key = record_key(paper)

        if key in seen_keys:
            continue

        seen_keys.add(key)
        unique_papers.append(paper)

    return unique_papers
