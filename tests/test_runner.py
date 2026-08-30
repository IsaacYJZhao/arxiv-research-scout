from datetime import (
    datetime,
    timezone,
)

from arxiv_research_scout.models import (
    ArxivPaper,
)

from arxiv_research_scout.runner import (
    run_scan,
)

from arxiv_research_scout.state_manager import (
    default_state,
    mark_paper_processed,
)


def make_paper(
    arxiv_id: str,
    published: str,
) -> ArxivPaper:
    return ArxivPaper(
        arxiv_id=arxiv_id,
        title=(
            f"3D Lung Nodule Detection "
            f"{arxiv_id}"
        ),
        abstract=(
            "A deep learning method for "
            "false positive reduction in CT."
        ),
        authors=("Example Author",),
        published=published,
        updated=published,
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


def make_config() -> dict:
    return {
        "topic": {
            "name": "Test Topic",
            "arxiv_query": (
                'all:"lung nodule"'
            ),
            "categories": [
                "cs.CV",
            ],
        },
        "schedule": {
            "run_every_days": 3,
            "lookback_days": 5,
        },
        "retrieval": {
            "max_candidates": 40,
            "max_papers": 2,
        },
        "relevance": {
            "min_score": 7,
            "high_score": 10,
            "core_terms": [
                "lung nodule",
            ],
            "target_terms": [
                "detection",
                "false positive",
                "candidate classification",
            ],
            "supporting_terms": [
                "CT",
                "3D",
                "deep learning",
            ],
            "deprioritize_terms": [
                "segmentation",
                "malignancy",
            ],
        },
    }


def test_run_scan_filters_papers() -> None:
    config = make_config()

    state = default_state()

    mark_paper_processed(
        state,
        "2608.10003v1",
    )

    papers = [
        make_paper(
            "2608.10001v2",
            "2026-08-28T10:00:00Z",
        ),
        make_paper(
            "2608.10001v1",
            "2026-08-27T10:00:00Z",
        ),
        make_paper(
            "2608.10002v1",
            "2026-08-28T11:00:00Z",
        ),
        make_paper(
            "2608.10003v2",
            "2026-08-28T12:00:00Z",
        ),
        make_paper(
            "2608.10004v1",
            "2026-08-20T12:00:00Z",
        ),
    ]

    def fake_search(
        query: str,
        max_results: int,
    ) -> list[ArxivPaper]:
        assert "lung nodule" in query
        assert max_results == 40

        return papers

    now = datetime(
        2026,
        8,
        29,
        12,
        0,
        0,
        tzinfo=timezone.utc,
    )

    result = run_scan(
        config=config,
        state=state,
        now=now,
        search_function=fake_search,
    )

    assert result.due

    assert result.candidate_count == 5
    assert result.recent_count == 4
    assert result.unique_count == 3
    assert result.unprocessed_count == 2

    assert len(
        result.selected_papers
    ) == 2

    assert (
        result.selected_papers[0][0].arxiv_id
        == "2608.10001v2"
    )

    assert (
        result.selected_papers[1][0].arxiv_id
        == "2608.10002v1"
    )
    assert result.relevant_count == 2


def test_run_scan_skips_when_not_due() -> None:
    config = make_config()

    state = default_state()

    state[
        "last_successful_run_utc"
    ] = (
        "2026-08-28T12:00:00+00:00"
    )

    def should_not_run(
        query: str,
        max_results: int,
    ) -> list[ArxivPaper]:
        raise AssertionError(
            "arXiv search should not run."
        )

    now = datetime(
        2026,
        8,
        29,
        12,
        0,
        0,
        tzinfo=timezone.utc,
    )

    result = run_scan(
        config=config,
        state=state,
        now=now,
        search_function=should_not_run,
    )

    assert not result.due
    assert result.selected_papers == ()


def test_force_ignores_schedule() -> None:
    config = make_config()

    state = default_state()

    state[
        "last_successful_run_utc"
    ] = (
        "2026-08-29T11:59:00+00:00"
    )

    calls = []

    def fake_search(
        query: str,
        max_results: int,
    ) -> list[ArxivPaper]:
        calls.append(
            (
                query,
                max_results,
            )
        )

        return []

    now = datetime(
        2026,
        8,
        29,
        12,
        0,
        0,
        tzinfo=timezone.utc,
    )

    result = run_scan(
        config=config,
        state=state,
        force=True,
        now=now,
        search_function=fake_search,
    )

    assert result.due
    assert len(calls) == 1