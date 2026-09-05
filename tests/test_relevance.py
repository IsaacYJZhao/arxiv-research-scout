from arxiv_research_scout.models import (
    ArxivPaper,
)

from arxiv_research_scout.relevance import (
    assess_relevance,
    contains_term,
    rank_relevant_papers,
)


def make_paper(
    title: str,
    abstract: str,
    arxiv_id: str = "2608.10000v1",
) -> ArxivPaper:
    return ArxivPaper(
        arxiv_id=arxiv_id,
        title=title,
        authors=("Example Author",),
        abstract=abstract,
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


def relevance_config() -> dict:
    return {
        "min_score": 7,
        "high_score": 10,
        "core_terms": [
            "lung nodule",
            "pulmonary nodule",
            "LUNA16",
            "LNDb",
        ],
        "target_terms": [
            "detection",
            "detector",
            "false positive",
            "false-positive",
            "false positive reduction",
            "false-positive reduction",
            "candidate generation",
            "candidate detection",
            "candidate classification",
            "computer-aided detection",
            "computer aided detection",
        ],
        "supporting_terms": [
            "computed tomography",
            "CT",
            "3D",
            "deep learning",
        ],
        "deprioritize_terms": [
            "segmentation",
            "malignancy",
            "characterization",
            "triage",
            "vision-language model",
            "vision language model",
            "clinical decision making",
        ],
    }

def test_contains_term_avoids_substring_match() -> None:
    assert contains_term(
        "A CAD system for CT imaging",
        "CAD",
    )

    assert not contains_term(
        "A cascade network",
        "CAD",
    )


def test_detection_paper_is_high_relevance() -> None:
    paper = make_paper(
        title=(
            "3D Deep Learning for "
            "Lung Nodule Detection in CT"
        ),
        abstract=(
            "We reduce false positive "
            "detections on LUNA16."
        ),
    )

    result = assess_relevance(
        paper,
        relevance_config(),
    )

    assert result.level == "high"
    assert result.score >= 9


def test_segmentation_paper_is_deprioritized() -> None:
    paper = make_paper(
        title=(
            "Foundation Models for "
            "Lung Nodule Segmentation"
        ),
        abstract=(
            "We study prompt generation "
            "for segmentation."
        ),
    )

    result = assess_relevance(
        paper,
        relevance_config(),
    )

    assert result.level == "low"


def test_abstract_can_make_paper_relevant() -> None:
    paper = make_paper(
        title="Pulmonary CT Analysis",
        abstract=(
            "We propose lung nodule detection "
            "with false positive reduction."
        ),
    )

    result = assess_relevance(
        paper,
        relevance_config(),
    )

    assert result.score >= 5


def test_rank_relevant_papers_filters_low_scores() -> None:
    high = make_paper(
        title=(
            "3D Lung Nodule Detection in CT"
        ),
        abstract=(
            "Deep learning detection method."
        ),
        arxiv_id="2608.10001v1",
    )

    low = make_paper(
        title=(
            "Lung Nodule Segmentation"
        ),
        abstract=(
            "Prompt-based segmentation."
        ),
        arxiv_id="2608.10002v1",
    )

    ranked = rank_relevant_papers(
        [low, high],
        relevance_config(),
    )

    assert len(ranked) == 1

    assert ranked[0][0].arxiv_id == (
        "2608.10001v1"
    )

def test_malignancy_paper_is_deprioritized() -> None:
    paper = make_paper(
        title=(
            "Deep Learning for Pulmonary "
            "Nodule Malignancy Classification"
        ),
        abstract=(
            "We perform malignancy prediction "
            "from chest CT."
        ),
    )

    result = assess_relevance(
        paper,
        relevance_config(),
    )

    assert result.score < 7


def test_candidate_classification_is_relevant() -> None:
    paper = make_paper(
        title=(
            "False Positive Reduction for "
            "Lung Nodule Detection"
        ),
        abstract=(
            "We perform candidate classification "
            "on CT scans using deep learning."
        ),
    )

    result = assess_relevance(
        paper,
        relevance_config(),
    )

    assert result.level == "high"
    assert result.score >= 10

def strict_relevance_config() -> dict:
    """
    Current production-style configuration.

    Admission is governed by require_core; deprioritize
    terms only affect ranking.
    """

    config = relevance_config()

    config["min_score"] = 4
    config["high_score"] = 8
    config["require_core"] = True

    config["core_terms"] = [
        "lung nodule",
        "pulmonary nodule",
        "lung cancer screening",
        "LIDC",
        "LUNA16",
        "LNDb",
        "NLST",
    ]

    return config


def test_deprioritized_terms_cannot_veto_an_on_topic_paper() -> None:
    """
    Regression test.

    Under the previous weights this paper scored 5 and
    was dropped by min_score 7, even though it is a 3D
    lung nodule study on LIDC and LNDb.
    """

    paper = make_paper(
        title=(
            "3D Lung Nodule Segmentation "
            "in Low-Dose CT"
        ),
        abstract=(
            "We evaluate on LIDC and LNDb "
            "using deep learning."
        ),
    )

    config = strict_relevance_config()

    result = assess_relevance(
        paper,
        config,
    )

    assert result.matched_deprioritize_terms
    assert result.score >= config["min_score"]

    ranked = rank_relevant_papers(
        [paper],
        config,
    )

    assert len(ranked) == 1


def test_require_core_excludes_off_topic_paper() -> None:
    """
    A high-scoring paper with no core-term match must
    not enter the candidate set.
    """

    paper = make_paper(
        title=(
            "3D Deep Learning Detection in CT"
        ),
        abstract=(
            "A general-purpose detector for "
            "computed tomography volumes."
        ),
    )

    config = strict_relevance_config()

    result = assess_relevance(
        paper,
        config,
    )

    assert not result.matched_core_terms
    assert result.score >= config["min_score"]

    assert rank_relevant_papers(
        [paper],
        config,
    ) == []


def test_score_is_never_negative() -> None:
    paper = make_paper(
        title=(
            "Segmentation, Malignancy, "
            "Characterization and Triage"
        ),
        abstract=(
            "A vision language model for "
            "clinical decision making."
        ),
    )

    result = assess_relevance(
        paper,
        strict_relevance_config(),
    )

    assert result.score >= 0
