from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Iterable

import requests

from arxiv_research_scout.models import ArxivPaper


ARXIV_API_URL = "https://export.arxiv.org/api/query"

DEFAULT_TIMEOUT_SECONDS = 30

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


def parse_entry(entry: ET.Element) -> ArxivPaper:
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

    return ArxivPaper(
        arxiv_id=parse_arxiv_id(abs_url),
        title=title,
        authors=authors,
        abstract=abstract,
        published=published,
        updated=updated,
        categories=categories,
        abs_url=abs_url,
        pdf_url=pdf_url,
    )


def parse_feed(
    xml_content: bytes,
) -> list[ArxivPaper]:
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


def search_arxiv(
    query: str,
    max_results: int = 20,
) -> list[ArxivPaper]:
    """
    Search arXiv and return standardized paper objects.
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

    response = requests.get(
        ARXIV_API_URL,
        params=params,
        headers=headers,
        timeout=DEFAULT_TIMEOUT_SECONDS,
    )

    response.raise_for_status()

    return parse_feed(
        response.content
    )