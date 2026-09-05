from datetime import datetime, timezone

from arxiv_research_scout.models import PaperRecord

from arxiv_research_scout.paper_filters import (
    deduplicate_papers,
    filter_recent_papers,
    normalize_arxiv_id,
    normalize_doi,
    parse_arxiv_datetime,
    record_key,
)


def make_paper(
    record_id: str,
    published: str,
) -> PaperRecord:
    return PaperRecord(
        record_id=record_id,
        title=f"Paper {record_id}",
        authors=("Example Author",),
        abstract="Example abstract.",
        published=published,
        updated=published,
        categories=("cs.CV",),
        abs_url=(
            f"https://arxiv.org/abs/"
            f"{record_id}"
        ),
        pdf_url=(
            f"https://arxiv.org/pdf/"
            f"{record_id}"
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

    assert recent[0].record_id == (
        "2608.10001v1"
    )


def test_filter_recent_papers_rejects_invalid_window() -> None:
    papers: list[PaperRecord] = []

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

    assert unique[0].record_id == (
        "2608.16855v2"
    )

    assert unique[1].record_id == (
        "2608.20000v1"
    )

def make_record(
    record_id: str,
    *,
    source: str = "arxiv",
    doi: str = "",
) -> PaperRecord:
    return PaperRecord(
        record_id=record_id,
        title="Example",
        authors=(),
        abstract="",
        published="2026-08-28T10:00:00Z",
        updated="2026-08-28T10:00:00Z",
        categories=(),
        abs_url="",
        pdf_url="",
        source=source,
        doi=doi,
    )


def test_normalize_doi() -> None:
    expected = "10.1007/s10278-026-02237-y"

    for raw in [
        "10.1007/s10278-026-02237-y",
        "10.1007/S10278-026-02237-Y",
        "https://doi.org/10.1007/s10278-026-02237-y",
        "http://dx.doi.org/10.1007/S10278-026-02237-Y",
        "  10.1007/s10278-026-02237-y  ",
    ]:
        assert normalize_doi(raw) == expected


def test_record_key_prefers_doi() -> None:
    assert record_key(
        make_record(
            "42675277",
            source="europepmc",
            doi="https://doi.org/10.1007/S10278-1",
        )
    ) == "doi:10.1007/s10278-1"


def test_record_key_falls_back_to_source() -> None:
    assert record_key(
        make_record("2608.16855v2")
    ) == "arxiv:2608.16855"

    assert record_key(
        make_record(
            "42675277",
            source="europepmc",
        )
    ) == "europepmc:42675277"


def test_arxiv_datacite_doi_maps_back_to_arxiv() -> None:
    """
    Europe PMC indexes arXiv preprints and reports their
    DataCite DOI. Without this rule the same preprint
    would be analyzed once per source.
    """

    from_arxiv = make_record("2608.16855v1")

    from_europepmc = make_record(
        "PPR999999",
        source="europepmc",
        doi="10.48550/arXiv.2608.16855",
    )

    assert record_key(from_arxiv) == (
        record_key(from_europepmc)
    )


def test_deduplicate_across_sources_keeps_first() -> None:
    preprint = make_record("2608.16855v1")

    journal_version = make_record(
        "42675277",
        source="europepmc",
        doi="10.48550/arxiv.2608.16855v1",
    )

    unrelated = make_record(
        "42581511",
        source="europepmc",
        doi="10.5090/jcs.26.065",
    )

    unique = deduplicate_papers(
        [
            preprint,
            journal_version,
            unrelated,
        ]
    )

    assert len(unique) == 2

    # arXiv is queried first, so the version with a
    # downloadable PDF is the one that survives.
    assert unique[0].source == "arxiv"
