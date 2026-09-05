from __future__ import annotations

import time
import xml.etree.ElementTree as ET
from collections.abc import Iterable

import requests

from arxiv_research_scout.models import PaperRecord


ARXIV_API_URL = "https://export.arxiv.org/api/query"

DEFAULT_TIMEOUT_SECONDS = 60

MAX_REQUEST_ATTEMPTS = 4

BASE_RETRY_DELAY_SECONDS = 10.0

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

NAMESPACES = {
    "atom": "http://www.w3.org/2005/Atom",
    "arxiv": "http://arxiv.org/schemas/atom",
}


def clean_text(value: str | None) -> str:
    """
    Collapse repeated whitespace and line breaks.
    """

    if not value:
        return ""

    return " ".join(value.split())


def build_search_query(
    base_query: str,
    categories: Iterable[str] | None = None,
) -> str:
    """
    Combine the topic query with optional arXiv categories.

    Example:

        (all:"lung nodule")
        AND
        (cat:cs.CV OR cat:eess.IV)
    """

    base_query = base_query.strip()

    if not base_query:
        raise ValueError(
            "base_query must not be empty."
        )

    category_list = [
        category.strip()
        for category in (categories or [])
        if category.strip()
    ]

    if not category_list:
        return base_query

    category_query = " OR ".join(
        f"cat:{category}"
        for category in category_list
    )

    return (
        f"({base_query}) "
        f"AND ({category_query})"
    )


def parse_arxiv_id(entry_url: str) -> str:
    """
    Extract an arXiv ID from an entry URL.

    Example:

        https://arxiv.org/abs/2608.12345v1
        ->
        2608.12345v1
    """

    return entry_url.rstrip("/").split("/")[-1]


def parse_entry(entry: ET.Element) -> PaperRecord:
    """
    Parse one Atom <entry> element.
    """

    abs_url = clean_text(
        entry.findtext(
            "atom:id",
            namespaces=NAMESPACES,
        )
    )

    title = clean_text(
        entry.findtext(
            "atom:title",
            namespaces=NAMESPACES,
        )
    )

    abstract = clean_text(
        entry.findtext(
            "atom:summary",
            namespaces=NAMESPACES,
        )
    )

    published = clean_text(
        entry.findtext(
            "atom:published",
            namespaces=NAMESPACES,
        )
    )

    updated = clean_text(
        entry.findtext(
            "atom:updated",
            namespaces=NAMESPACES,
        )
    )

    authors = tuple(
        clean_text(
            author.findtext(
                "atom:name",
                namespaces=NAMESPACES,
            )
        )
        for author in entry.findall(
            "atom:author",
            namespaces=NAMESPACES,
        )
    )

    authors = tuple(
        author
        for author in authors
        if author
    )

    categories = tuple(
        category.attrib.get(
            "term",
            "",
        ).strip()
        for category in entry.findall(
            "atom:category",
            namespaces=NAMESPACES,
        )
        if category.attrib.get(
            "term",
            "",
        ).strip()
    )

    pdf_url = ""

    for link in entry.findall(
        "atom:link",
        namespaces=NAMESPACES,
    ):
        title_attr = link.attrib.get(
            "title",
            "",
        )

        type_attr = link.attrib.get(
            "type",
            "",
        )

        if (
            title_attr == "pdf"
            or type_attr == "application/pdf"
        ):
            pdf_url = link.attrib.get(
                "href",
                "",
            ).strip()

            break

    # Authors may declare the DOI of the published
    # version. When they do, the preprint and the
    # journal article collapse into one paper instead
    # of being analyzed twice.
    doi = clean_text(
        entry.findtext(
            "arxiv:doi",
            namespaces=NAMESPACES,
        )
    )

    venue = clean_text(
        entry.findtext(
            "arxiv:journal_ref",
            namespaces=NAMESPACES,
        )
    )

    return PaperRecord(
        record_id=parse_arxiv_id(abs_url),
        title=title,
        authors=authors,
        abstract=abstract,
        published=published,
        updated=updated,
        categories=categories,
        abs_url=abs_url,
        pdf_url=pdf_url,
        source="arxiv",
        doi=doi,
        venue=venue,
        full_text_available=bool(pdf_url),
    )


def parse_feed(
    xml_content: bytes,
) -> list[PaperRecord]:
    """
    Parse an arXiv Atom feed.
    """

    root = ET.fromstring(xml_content)

    entries = root.findall(
        "atom:entry",
        namespaces=NAMESPACES,
    )

    return [
        parse_entry(entry)
        for entry in entries
    ]


def get_retry_delay_seconds(
    response: requests.Response | None,
    attempt: int,
) -> float:
    """
    Determine how long to wait before retrying.

    Prefer the server-provided Retry-After header
    when it contains a numeric number of seconds.

    Otherwise use exponential backoff:
        10s, 20s, 40s, ...
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

def search_arxiv(
    query: str,
    max_results: int = 20,
) -> list[PaperRecord]:
    """
    Search arXiv and return standardized paper objects.

    Temporary network failures and rate limiting are
    retried with exponential backoff.
    """

    if max_results < 1:
        raise ValueError(
            "max_results must be at least 1."
        )

    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
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
                ARXIV_API_URL,
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
                f"arXiv request failed "
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
                f"arXiv returned HTTP "
                f"{response.status_code}. "
                f"Retrying in {delay:.0f}s "
                f"[{attempt}/{MAX_REQUEST_ATTEMPTS}]..."
            )

            time.sleep(delay)

            continue

        response.raise_for_status()

        return parse_feed(
            response.content
        )

    if last_error is not None:
        raise last_error

    raise RuntimeError(
        "arXiv request failed unexpectedly."
    )