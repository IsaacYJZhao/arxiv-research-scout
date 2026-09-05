import requests

from arxiv_research_scout.arxiv_client import (
    build_search_query,
    clean_text,
    parse_arxiv_id,
    parse_feed,
    search_arxiv,
)


def test_clean_text() -> None:
    value = """
        Lung     nodule
        detection
    """

    assert clean_text(value) == (
        "Lung nodule detection"
    )


def test_parse_arxiv_id() -> None:
    url = (
        "https://arxiv.org/abs/"
        "2608.12345v1"
    )

    assert parse_arxiv_id(url) == (
        "2608.12345v1"
    )


def test_build_query_without_categories() -> None:
    query = build_search_query(
        'all:"lung nodule"',
    )

    assert query == (
        'all:"lung nodule"'
    )


def test_build_query_with_categories() -> None:
    query = build_search_query(
        'all:"lung nodule"',
        [
            "cs.CV",
            "eess.IV",
        ],
    )

    assert query == (
        '(all:"lung nodule") '
        'AND '
        '(cat:cs.CV OR cat:eess.IV)'
    )

def test_parse_feed() -> None:
    xml_content = b"""<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <entry>
        <id>https://arxiv.org/abs/2608.12345v1</id>

        <updated>2026-08-20T12:00:00Z</updated>

        <published>2026-08-20T10:00:00Z</published>

        <title>
            A Lung Nodule Detection Method
        </title>

        <summary>
            We propose a lightweight method
            for lung nodule detection.
        </summary>

        <author>
            <name>Alice Example</name>
        </author>

        <author>
            <name>Bob Example</name>
        </author>

        <category term="cs.CV"/>

        <link
            title="pdf"
            href="https://arxiv.org/pdf/2608.12345v1"
            type="application/pdf"
        />
    </entry>
</feed>
"""

    papers = parse_feed(xml_content)

    assert len(papers) == 1

    paper = papers[0]

    assert paper.record_id == "2608.12345v1"

    assert paper.title == (
        "A Lung Nodule Detection Method"
    )

    assert paper.abstract == (
        "We propose a lightweight method "
        "for lung nodule detection."
    )

    assert paper.authors == (
        "Alice Example",
        "Bob Example",
    )

    assert paper.published == (
        "2026-08-20T10:00:00Z"
    )

    assert paper.updated == (
        "2026-08-20T12:00:00Z"
    )

    assert paper.categories == (
        "cs.CV",
    )

    assert paper.abs_url == (
        "https://arxiv.org/abs/2608.12345v1"
    )

    assert paper.pdf_url == (
        "https://arxiv.org/pdf/2608.12345v1"
    )

def test_search_arxiv_retries_after_429(
    monkeypatch,
) -> None:
    rate_limited = requests.Response()
    rate_limited.status_code = 429
    rate_limited._content = b"rate limited"

    success = requests.Response()
    success.status_code = 200
    success._content = (
        b'<?xml version="1.0" '
        b'encoding="UTF-8"?>'
        b'<feed '
        b'xmlns="http://www.w3.org/2005/Atom">'
        b'</feed>'
    )

    responses = [
        rate_limited,
        success,
    ]

    sleep_calls: list[float] = []

    def fake_get(
        *args,
        **kwargs,
    ):
        return responses.pop(0)

    def fake_sleep(
        seconds: float,
    ) -> None:
        sleep_calls.append(seconds)

    monkeypatch.setattr(
        "arxiv_research_scout."
        "arxiv_client.requests.get",
        fake_get,
    )

    monkeypatch.setattr(
        "arxiv_research_scout."
        "arxiv_client.time.sleep",
        fake_sleep,
    )

    papers = search_arxiv(
        'all:"lung nodule"',
        max_results=1,
    )

    assert papers == []

    assert len(sleep_calls) == 1

    assert sleep_calls[0] >= 0