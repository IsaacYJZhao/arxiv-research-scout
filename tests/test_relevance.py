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