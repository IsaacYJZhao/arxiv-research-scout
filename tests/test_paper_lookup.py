import pytest

from arxiv_research_scout.models import (
    ArxivPaper,
)
from arxiv_research_scout.paper_lookup import (
    find_arxiv_paper,
)


def make_paper(
    arxiv_id: str,
) -> ArxivPaper:
    return ArxivPaper(
        arxiv_id=arxiv_id,
        title="Example Paper",
        authors=("Alice Example",),
        abstract="Abstract.",
        published="2026-08-28T10:00:00Z",
        updated="2026-08-28T10:00:00Z",
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


def test_find_exact_arxiv_paper() -> None:
    captured = {}

    def fake_search(
        query: str,
        max_results: int,
    ):
        captured["query"] = query
        captured["max_results"] = (
            max_results
        )

        return [
            make_paper(
                "2608.16855v2"
            )
        ]

    paper = find_arxiv_paper(
        "2608.16855v1",
        search_function=fake_search,
    )

    assert paper.arxiv_id == (
        "2608.16855v2"
    )

    assert captured["query"] == (
        "id:2608.16855"
    )

    assert (
        captured["max_results"]
        == 5
    )


def test_missing_arxiv_paper_is_rejected() -> None:
    def fake_search(
        query: str,
        max_results: int,
    ):
        return [
            make_paper(
                "2608.99999v1"
            )
        ]

    with pytest.raises(
        LookupError,
        match="arXiv paper not found",
    ):
        find_arxiv_paper(
            "2608.16855v1",
            search_function=fake_search,
        )


def test_empty_arxiv_id_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match=(
            "arXiv ID must not be empty"
        ),
    ):
        find_arxiv_paper(
            "   ",
            search_function=lambda q, n: [],
        )