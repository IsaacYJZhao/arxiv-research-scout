from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ArxivPaper:
    """
    Standard representation of one paper returned by arXiv.
    """

    arxiv_id: str
    title: str
    authors: tuple[str, ...]
    abstract: str
    published: str
    updated: str
    categories: tuple[str, ...]
    abs_url: str
    pdf_url: str