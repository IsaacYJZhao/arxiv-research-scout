from __future__ import annotations

import re
from typing import Any

from arxiv_research_scout.models import (
    ArxivPaper,
    RelevanceAssessment,
)


def contains_term(
    text: str,
    term: str,
) -> bool:
    """
    Match a term case-insensitively while avoiding
    accidental substring matches.

    Example:
        "CAD" should match "CAD system"
        but should not match "cascade".
    """

    pattern = re.compile(
        rf"(?<!\w){re.escape(term)}(?!\w)",
        flags=re.IGNORECASE,
    )

    return bool(
        pattern.search(text)
    )


def score_term_group(
    paper: ArxivPaper,
    terms: list[str],
    *,
    title_points: int,
    abstract_points: int,
) -> tuple[int, tuple[str, ...]]:
    """
    Score one group of relevance terms.

    A title match receives the stronger score.
    If the title does not match, the abstract
    is checked instead.
    """

    score = 0
    matched_terms: list[str] = []

    for term in terms:
        if contains_term(
            paper.title,
            term,
        ):
            score += title_points
            matched_terms.append(term)

        elif contains_term(
            paper.abstract,
            term,
        ):
            score += abstract_points
            matched_terms.append(term)

    return (
        score,
        tuple(matched_terms),
    )


def assess_relevance(
    paper: ArxivPaper,
    relevance_config: dict[str, Any],
) -> RelevanceAssessment:
    """
    Produce a deterministic relevance assessment.

    Scoring:
        core terms:
            title +4
            abstract +2

        target terms:
            title +5
            abstract +3

        supporting terms:
            title +2
            abstract +1

        deprioritize terms:
            title -4
            abstract -1
    """

    core_score, core_matches = (
        score_term_group(
            paper,
            relevance_config.get(
                "core_terms",
                [],
            ),
            title_points=4,
            abstract_points=2,
        )
    )

    target_score, target_matches = (
        score_term_group(
            paper,
            relevance_config.get(
                "target_terms",
                [],
            ),
            title_points=5,
            abstract_points=3,
        )
    )

    support_score, support_matches = (
        score_term_group(
            paper,
            relevance_config.get(
                "supporting_terms",
                [],
            ),
            title_points=2,
            abstract_points=1,
        )
    )

    penalty_score, penalty_matches = (
        score_term_group(
            paper,
            relevance_config.get(
                "deprioritize_terms",
                [],
            ),
            title_points=-4,
            abstract_points=-1,
        )
    )

    total_score = (
        core_score
        + target_score
        + support_score
        + penalty_score
    )

    high_score = relevance_config[
        "high_score"
    ]

    min_score = relevance_config[
        "min_score"
    ]

    if total_score >= high_score:
        level = "high"

    elif total_score >= min_score:
        level = "medium"

    else:
        level = "low"

    return RelevanceAssessment(
        score=total_score,
        level=level,
        matched_core_terms=core_matches,
        matched_target_terms=target_matches,
        matched_supporting_terms=support_matches,
        matched_deprioritize_terms=penalty_matches,
    )


def rank_relevant_papers(
    papers: list[ArxivPaper],
    relevance_config: dict[str, Any],
) -> list[
    tuple[
        ArxivPaper,
        RelevanceAssessment,
    ]
]:
    """
    Score, filter, and rank papers.

    Papers below min_score are excluded.
    Higher scores appear first.
    """

    min_score = relevance_config[
        "min_score"
    ]

    assessed = [
        (
            paper,
            assess_relevance(
                paper,
                relevance_config,
            ),
        )
        for paper in papers
    ]

    relevant = [
        (
            paper,
            assessment,
        )
        for paper, assessment in assessed
        if assessment.score >= min_score
    ]

    return sorted(
        relevant,
        key=lambda item: item[1].score,
        reverse=True,
    )