from datetime import datetime, timezone

from arxiv_research_scout.models import ArxivPaper

from arxiv_research_scout.paper_filters import (
    deduplicate_papers,
    filter_recent_papers,
    normalize_arxiv_id,
    parse_arxiv_datetime,
)


def make_paper(
    arxiv_id: str,
    published: str,
) -> ArxivPaper:
    return ArxivPaper(
        arxiv_id=arxiv_id,
        title=f"Paper {arxiv_id}",
        authors=("Example Author",),
        abstract="Example abstract.",
        published=published,
        updated=published,
        categories=("cs.CV",),
        abs_url=(
            f"https://arxiv.org/abs/"
            f"{arxiv_id}"
        ),
        pdf_url=(
            f"https://arxiv.org/pdf/"
            f"{arxiv_id}"
        ),
    )


def test_normalize_arxiv_id() -> None:
    assert normalize_arxiv_id(
        "2608.16855v1"
    ) == "2608.16855"

    assert normalize_arxiv_id(
        "2608.16855v3"
    ) == "2608.16855"

    assert normalize_arxiv_id(
        "2608.16855"
    ) == "2608.16855"


def test_parse_arxiv_datetime() -> None:
    value = "2026-08-20T10:00:00Z"

    parsed = parse_arxiv_datetime(value)

    assert parsed == datetime(
        2026,
        8,
        20,
        10,
        0,
        0,
        tzinfo=timezone.utc,
    )


def test_filter_recent_papers() -> None:
    papers = [
        make_paper(
            "2608.10001v1",
            "2026-08-28T10:00:00Z",
        ),
        make_paper(
            "2608.10002v1",
            "2026-08-20T10:00:00Z",
        ),
    ]

    now = datetime(
        2026,
        8,
        29,
        12,
        0,
        0,
        tzinfo=timezone.utc,
    )

    recent = filter_recent_papers(
        papers=papers,
        lookback_days=5,
        now=now,
    )

    assert len(recent) == 1

    assert recent[0].arxiv_id == (
        "2608.10001v1"
    )


def test_filter_recent_papers_rejects_invalid_window() -> None:
    papers: list[ArxivPaper] = []

    try:
        filter_recent_papers(
            papers,
            lookback_days=0,
        )
    except ValueError:
        pass
    else:
        raise AssertionError(
            "Expected ValueError."
        )


def test_deduplicate_papers() -> None:
    papers = [
        make_paper(
            "2608.16855v2",
            "2026-08-28T10:00:00Z",
        ),
        make_paper(
            "2608.16855v1",
            "2026-08-27T10:00:00Z",
        ),
        make_paper(
            "2608.20000v1",
            "2026-08-28T11:00:00Z",
        ),
    ]

    unique = deduplicate_papers(
        papers
    )

    assert len(unique) == 2

    assert unique[0].arxiv_id == (
        "2608.16855v2"
    )

    assert unique[1].arxiv_id == (
        "2608.20000v1"
    )