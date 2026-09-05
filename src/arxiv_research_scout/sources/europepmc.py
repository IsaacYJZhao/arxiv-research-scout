"""
Europe PMC retrieval source.

Europe PMC indexes the medical and life-science
literature: journal articles, PubMed records and
preprints. It covers the venues where clinical imaging
work is actually published, which arXiv does not, so it
is the source that closes the largest gap for this
project.

The REST API needs no key. Its query language differs
from arXiv's, so the query lives in its own
configuration block rather than being translated:

    (TITLE_ABS:"lung nodule" OR TITLE_ABS:"pulmonary nodule")
    AND (TITLE_ABS:"deep learning")

Documentation:
    https://europepmc.org/RestfulWebService
"""

from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from typing import Any

import requests

from arxiv_research_scout.models import PaperRecord


EUROPEPMC_API_URL = (
    "https://www.ebi.ac.uk"
    "/europepmc/webservices/rest/search"
)

DEFAULT_TIMEOUT_SECONDS = 60

MAX_REQUEST_ATTEMPTS = 4

BASE_RETRY_DELAY_SECONDS = 5.0

RETRYABLE_STATUS_CODES = {
    429,
    500,
    502,
    503,
    504,
}

USER_AGENT = (
    "arxiv-research-scout/0.1 "
    "(academic literature monitoring tool)"
)

# Europe PMC accepts far larger pages, but a scout only
# ever looks at a recent window, and a smaller page is
# a lighter request against a shared public service.
MAX_PAGE_SIZE = 200


def clean_text(value: Any) -> str:
    """
    Collapse repeated whitespace and line breaks.
    """

    if not value:
        return ""

    return " ".join(str(value).split())


def format_date(value: datetime) -> str:
    """
    Format a date the way Europe PMC expects it in a
    FIRST_PDATE range.
    """

    return value.astimezone(
        timezone.utc
    ).strftime("%Y-%m-%d")


def build_search_query(
    base_query: str,
    lookback_days: int,
    now: datetime | None = None,
) -> str:
    """
    Combine the topic query with a publication window.

    The window is applied server-side on purpose.
    Europe PMC sorts by relevance by default and holds
    tens of millions of records, so filtering by date
    only after retrieval would return mostly old work.
    """

    base_query = base_query.strip()

    if not base_query:
        raise ValueError(
            "base_query must not be empty."
        )

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

    start = current_time - timedelta(
        days=lookback_days
    )

    return (
        f"({base_query}) AND "
        f"(FIRST_PDATE:["
        f"{format_date(start)} TO "
        f"{format_date(current_time)}"
        f"])"
    )


def extract_pdf_url(
    entry: dict[str, Any],
) -> str:
    """
    Find a directly downloadable PDF, if one exists.

    Most journal articles indexed here are behind a
    paywall. Their record is still worth having, but
    only their abstract can be analyzed, so the caller
    needs to know the difference.
    """

    full_text_list = (
        entry.get("fullTextUrlList")
        or {}
    ).get("fullTextUrl") or []

    for url_entry in full_text_list:
        style = str(
            url_entry.get("documentStyle", "")
        ).lower()

        availability = str(
            url_entry.get("availability", "")
        ).lower()

        if style != "pdf":
            continue

        if "subscription" in availability:
            continue

        url = clean_text(
            url_entry.get("url")
        )

        if url:
            return url

    return ""


def extract_landing_url(
    entry: dict[str, Any],
) -> str:
    """
    Build a stable human-readable URL for the record.
    """

    doi = clean_text(entry.get("doi"))

    if doi:
        return f"https://doi.org/{doi}"

    source = clean_text(
        entry.get("source")
    )

    record_id = clean_text(
        entry.get("id")
    )

    if source and record_id:
        return (
            "https://europepmc.org/article/"
            f"{source}/{record_id}"
        )

    return ""


def extract_authors(
    entry: dict[str, Any],
) -> tuple[str, ...]:
    """
    Prefer the structured author list, and fall back to
    the pre-joined author string.
    """

    author_list = (
        entry.get("authorList")
        or {}
    ).get("author") or []

    authors = tuple(
        clean_text(
            author.get("fullName")
            or author.get("lastName")
        )
        for author in author_list
    )

    authors = tuple(
        author
        for author in authors
        if author
    )

    if authors:
        return authors

    author_string = clean_text(
        entry.get("authorString")
    )

    if not author_string:
        return ()

    return tuple(
        part.strip(" .")
        for part in author_string.split(",")
        if part.strip(" .")
    )


def extract_keywords(
    entry: dict[str, Any],
) -> tuple[str, ...]:
    """
    Europe PMC keywords stand in for arXiv categories.

    They are optional, and often absent.
    """

    keywords = (
        entry.get("keywordList")
        or {}
    ).get("keyword") or []

    return tuple(
        clean_text(keyword)
        for keyword in keywords
        if clean_text(keyword)
    )


def parse_entry(
    entry: dict[str, Any],
) -> PaperRecord:
    """
    Convert one Europe PMC result into a PaperRecord.
    """

    pdf_url = extract_pdf_url(entry)

    published = clean_text(
        entry.get("firstPublicationDate")
    )

    venue = clean_text(
        (
            (
                entry.get("journalInfo")
                or {}
            ).get("journal")
            or {}
        ).get("title")
    )

    return PaperRecord(
        record_id=clean_text(
            entry.get("id")
        ),
        title=clean_text(
            entry.get("title")
        ).rstrip("."),
        authors=extract_authors(entry),
        abstract=clean_text(
            entry.get("abstractText")
        ),
        published=published,
        updated=published,
        categories=extract_keywords(entry),
        abs_url=extract_landing_url(entry),
        pdf_url=pdf_url,
        source="europepmc",
        doi=clean_text(entry.get("doi")),
        venue=venue,
        full_text_available=bool(pdf_url),
    )


def parse_response(
    payload: dict[str, Any],
) -> list[PaperRecord]:
    """
    Parse one Europe PMC JSON response.
    """

    results = (
        payload.get("resultList")
        or {}
    ).get("result") or []

    papers = [
        parse_entry(entry)
        for entry in results
    ]

    return [
        paper
        for paper in papers
        if paper.record_id and paper.title
    ]


def get_retry_delay_seconds(
    response: requests.Response | None,
    attempt: int,
) -> float:
    """
    Determine how long to wait before retrying.

    A server-provided Retry-After wins when it holds a
    plain number of seconds; otherwise back off
    exponentially: 5s, 10s, 20s, ...
    """

    if response is not None:
        retry_after = response.headers.get(
            "Retry-After"
        )

        if retry_after:
            try:
                return max(
                    float(retry_after),
                    0.0,
                )
            except ValueError:
                pass

    return (
        BASE_RETRY_DELAY_SECONDS
        * (2 ** (attempt - 1))
    )


def search_europepmc(
    query: str,
    max_results: int = 50,
    *,
    lookback_days: int = 14,
    now: datetime | None = None,
) -> list[PaperRecord]:
    """
    Search Europe PMC and return normalized papers.

    Temporary network failures and rate limiting are
    retried with exponential backoff, mirroring the
    arXiv client, so one flaky source cannot fail a run
    on its own.
    """

    if max_results < 1:
        raise ValueError(
            "max_results must be at least 1."
        )

    params = {
        "query": build_search_query(
            query,
            lookback_days,
            now=now,
        ),
        "format": "json",
        "resultType": "core",
        "pageSize": min(
            max_results,
            MAX_PAGE_SIZE,
        ),
        "sort": "P_PDATE_D desc",
    }

    headers = {
        "User-Agent": USER_AGENT,
    }

    last_error: Exception | None = None

    for attempt in range(
        1,
        MAX_REQUEST_ATTEMPTS + 1,
    ):
        try:
            response = requests.get(
                EUROPEPMC_API_URL,
                params=params,
                headers=headers,
                timeout=DEFAULT_TIMEOUT_SECONDS,
            )

        except (
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError,
        ) as error:
            last_error = error

            if attempt >= MAX_REQUEST_ATTEMPTS:
                raise

            delay = get_retry_delay_seconds(
                response=None,
                attempt=attempt,
            )

            print(
                f"Europe PMC request failed "
                f"({type(error).__name__}). "
                f"Retrying in {delay:.0f}s "
                f"[{attempt}/{MAX_REQUEST_ATTEMPTS}]..."
            )

            time.sleep(delay)

            continue

        if (
            response.status_code
            in RETRYABLE_STATUS_CODES
        ):
            if attempt >= MAX_REQUEST_ATTEMPTS:
                response.raise_for_status()

            delay = get_retry_delay_seconds(
                response=response,
                attempt=attempt,
            )

            print(
                f"Europe PMC returned HTTP "
                f"{response.status_code}. "
                f"Retrying in {delay:.0f}s "
                f"[{attempt}/{MAX_REQUEST_ATTEMPTS}]..."
            )

            time.sleep(delay)

            continue

        response.raise_for_status()

        return parse_response(
            response.json()
        )

    if last_error is not None:
        raise last_error

    raise RuntimeError(
        "Europe PMC request failed unexpectedly."
    )
