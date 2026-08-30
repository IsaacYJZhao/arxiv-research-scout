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

@dataclass(frozen=True, slots=True)
class RelevanceAssessment:
    """
    Deterministic relevance assessment for one paper.
    """

    score: int
    level: str

    matched_core_terms: tuple[str, ...]
    matched_target_terms: tuple[str, ...]
    matched_supporting_terms: tuple[str, ...]
    matched_deprioritize_terms: tuple[str, ...]