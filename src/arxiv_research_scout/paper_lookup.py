from __future__ import annotations

from collections.abc import Callable

from arxiv_research_scout.arxiv_client import (
    search_arxiv,
)
from arxiv_research_scout.models import (
    ArxivPaper,
)
from arxiv_research_scout.paper_filters import (
    normalize_arxiv_id,
)


SearchFunction = Callable[
    [str, int],
    list[ArxivPaper],
]


def find_arxiv_paper(
    arxiv_id: str,
    *,
    search_function: SearchFunction = search_arxiv,
) -> ArxivPaper:
    """
    Retrieve one exact arXiv paper by ID.

    Version suffixes are ignored for identity
    matching, so v1/v2/v3 are treated as the
    same paper.
    """

    requested_id = arxiv_id.strip()

    if not requested_id:
        raise ValueError(
            "arXiv ID must not be empty."
        )

    normalized_requested = (
        normalize_arxiv_id(
            requested_id
        )
    )

    query = (
        f"id:{normalized_requested}"
    )

    candidates = search_function(
        query,
        5,
    )

    for paper in candidates:
        if (
            normalize_arxiv_id(
                paper.arxiv_id
            )
            == normalized_requested
        ):
            return paper

    raise LookupError(
        "arXiv paper not found: "
        f"{requested_id}"
    )