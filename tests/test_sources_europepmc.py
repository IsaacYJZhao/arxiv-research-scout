from datetime import datetime, timezone

from arxiv_research_scout.sources.europepmc import (
    build_search_query,
    extract_authors,
    extract_pdf_url,
    parse_entry,
    parse_response,
)


NOW = datetime(
    2026,
    9,
    5,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)


def open_access_entry() -> dict:
    """
    Shaped after a real Europe PMC `resultType=core`
    record for an open-access journal article.
    """

    return {
        "id": "42675277",
        "source": "MED",
        "pmid": "42675277",
        "doi": "10.1007/s10278-026-02237-y",
        "title": (
            "Resolution-Aware Evidential Fusion for "
            "Scale-Invariant Attribution in 3D Lung "
            "Nodule Detection."
        ),
        "authorString": "Haddar B, Elleuch MA.",
        "authorList": {
            "author": [
                {"fullName": "Haddar B"},
                {"fullName": "Elleuch MA"},
            ]
        },
        "journalInfo": {
            "journal": {
                "title": (
                    "Journal of imaging "
                    "informatics in medicine"
                )
            }
        },
        "abstractText": (
            "Post hoc attribution is the standard "
            "transparency layer for detection models."
        ),
        "firstPublicationDate": "2026-08-25",
        "isOpenAccess": "Y",
        "keywordList": {
            "keyword": [
                "Lung nodule detection",
                "Evidential deep learning",
            ]
        },
        "fullTextUrlList": {
            "fullTextUrl": [
                {
                    "availability": "Open access",
                    "documentStyle": "pdf",
                    "site": "Europe_PMC",
                    "url": (
                        "https://europepmc.org/"
                        "articles/PMC1/pdf"
                    ),
                }
            ]
        },
    }


def closed_access_entry() -> dict:
    return {
        "id": "42581511",
        "source": "MED",
        "doi": "10.5090/jcs.26.065",
        "title": (
            "Is Thoracic Computed Tomography Imaging "
            "Sufficient for Evaluating a Solitary "
            "Pulmonary Nodule?"
        ),
        "authorString": "Kermenli T.",
        "journalInfo": {
            "journal": {
                "title": "Journal of chest surgery"
            }
        },
        "abstractText": "",
        "firstPublicationDate": "2026-08-12",
        "isOpenAccess": "N",
        "fullTextUrlList": {
            "fullTextUrl": [
                {
                    "availability": (
                        "Subscription required"
                    ),
                    "documentStyle": "doi",
                    "site": "DOI",
                    "url": (
                        "https://doi.org/"
                        "10.5090/jcs.26.065"
                    ),
                }
            ]
        },
    }


def test_build_search_query_adds_publication_window() -> None:
    query = build_search_query(
        'TITLE_ABS:"lung nodule"',
        lookback_days=14,
        now=NOW,
    )

    assert 'TITLE_ABS:"lung nodule"' in query

    assert (
        "FIRST_PDATE:[2026-08-22 TO 2026-09-05]"
        in query
    )


def test_build_search_query_rejects_empty_input() -> None:
    for bad_call in (
        lambda: build_search_query(
            "   ",
            lookback_days=14,
            now=NOW,
        ),
        lambda: build_search_query(
            'TITLE_ABS:"x"',
            lookback_days=0,
            now=NOW,
        ),
    ):
        try:
            bad_call()
        except ValueError:
            continue

        raise AssertionError(
            "expected ValueError"
        )


def test_parse_open_access_entry() -> None:
    paper = parse_entry(
        open_access_entry()
    )

    assert paper.source == "europepmc"
    assert paper.record_id == "42675277"

    assert paper.doi == (
        "10.1007/s10278-026-02237-y"
    )

    assert paper.venue == (
        "Journal of imaging informatics in medicine"
    )

    # The trailing period Europe PMC keeps on titles is
    # noise in a report heading.
    assert not paper.title.endswith(".")

    assert paper.authors == (
        "Haddar B",
        "Elleuch MA",
    )

    assert paper.published == "2026-08-25"

    assert paper.full_text_available

    assert paper.pdf_url.endswith("/pdf")

    assert "Lung nodule detection" in (
        paper.categories
    )


def test_parse_closed_access_entry() -> None:
    """
    A paywalled article is still worth knowing about,
    but the pipeline must be able to tell that only its
    abstract can be analyzed.
    """

    paper = parse_entry(
        closed_access_entry()
    )

    assert paper.pdf_url == ""
    assert not paper.full_text_available

    # No structured author list, so the joined string
    # is split instead.
    assert paper.authors == ("Kermenli T",)

    assert paper.abs_url == (
        "https://doi.org/10.5090/jcs.26.065"
    )


def test_subscription_pdf_is_not_treated_as_full_text() -> None:
    entry = closed_access_entry()

    entry["fullTextUrlList"]["fullTextUrl"] = [
        {
            "availability": "Subscription required",
            "documentStyle": "pdf",
            "url": "https://publisher.example/x.pdf",
        }
    ]

    assert extract_pdf_url(entry) == ""


def test_extract_authors_falls_back_to_string() -> None:
    assert extract_authors(
        {"authorString": "Zhao I, Baur S."}
    ) == ("Zhao I", "Baur S")


def test_parse_response_skips_unusable_records() -> None:
    payload = {
        "resultList": {
            "result": [
                open_access_entry(),
                {"id": "", "title": "No id"},
                {"id": "1", "title": ""},
            ]
        }
    }

    papers = parse_response(payload)

    assert len(papers) == 1

    assert papers[0].record_id == "42675277"


def test_parse_response_handles_empty_payload() -> None:
    assert parse_response({}) == []
