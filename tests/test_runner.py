from datetime import (
    datetime,
    timezone,
)

from arxiv_research_scout.models import (
    PaperRecord,
)

from arxiv_research_scout.runner import (
    run_scan,
)

from arxiv_research_scout.state_manager import (
    default_state,
    mark_paper_processed,
)


def make_paper(
    record_id: str,
    published: str,
) -> PaperRecord:
    return PaperRecord(
        record_id=record_id,
        title=(
            f"3D Lung Nodule Detection "
            f"{record_id}"
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
            f"{record_id}"
        ),
        pdf_url=(
            f"https://arxiv.org/pdf/"
            f"{record_id}"
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
        make_paper(
            "2608.10003v1",
            "2026-08-28T10:00:00Z",
        ),
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
    ) -> list[PaperRecord]:
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
        result.selected_papers[0][0].record_id
        == "2608.10001v2"
    )

    assert (
        result.selected_papers[1][0].record_id
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
    ) -> list[PaperRecord]:
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
    ) -> list[PaperRecord]:
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

def make_europepmc_paper(
    record_id: str,
    published: str,
    *,
    doi: str = "",
    full_text: bool = True,
) -> PaperRecord:
    return PaperRecord(
        record_id=record_id,
        title=(
            f"Lung Nodule Detection in CT "
            f"{record_id}"
        ),
        abstract=(
            "A deep learning detector evaluated "
            "on LUNA16."
        ),
        authors=("Journal Author",),
        published=published,
        updated=published,
        categories=(),
        abs_url="https://europepmc.org/x",
        pdf_url=(
            "https://europepmc.org/x.pdf"
            if full_text
            else ""
        ),
        source="europepmc",
        doi=doi,
        venue="Journal of Imaging Informatics",
        full_text_available=full_text,
    )


def multi_source_config() -> dict:
    config = make_config()

    config["sources"] = {
        "arxiv": {"enabled": True},
        "europepmc": {
            "enabled": True,
            "max_candidates": 25,
            "query": 'TITLE_ABS:"lung nodule"',
        },
    }

    return config


NOW = datetime(
    2026,
    8,
    29,
    12,
    0,
    0,
    tzinfo=timezone.utc,
)


def test_scan_merges_enabled_sources() -> None:
    result = run_scan(
        multi_source_config(),
        default_state(),
        force=True,
        now=NOW,
        search_function=lambda query, limit: [
            make_paper(
                "2608.10001v1",
                "2026-08-28T10:00:00Z",
            )
        ],
        europepmc_function=(
            lambda query, limit, **kwargs: [
                make_europepmc_paper(
                    "42675277",
                    "2026-08-27",
                )
            ]
        ),
    )

    assert result.candidate_count == 2

    assert dict(result.source_counts) == {
        "arxiv": 1,
        "europepmc": 1,
    }

    assert result.source_errors == ()

    sources = {
        paper.source
        for paper, _, _ in result.selected_papers
    }

    assert sources == {"arxiv", "europepmc"}


def test_europepmc_stays_off_without_configuration() -> None:
    """
    An existing configuration has no sources block and
    must keep behaving exactly as it did before.
    """

    called = []

    result = run_scan(
        make_config(),
        default_state(),
        force=True,
        now=NOW,
        search_function=lambda query, limit: [
            make_paper(
                "2608.10001v1",
                "2026-08-28T10:00:00Z",
            )
        ],
        europepmc_function=(
            lambda *args, **kwargs: called.append(1)
            or []
        ),
    )

    assert called == []

    assert dict(result.source_counts) == {
        "arxiv": 1,
    }


def test_failing_source_does_not_abort_the_run() -> None:
    """
    Losing one source degrades a run. Aborting loses the
    papers every other source found.
    """

    def broken_europepmc(*args, **kwargs):
        raise RuntimeError("service unavailable")

    result = run_scan(
        multi_source_config(),
        default_state(),
        force=True,
        now=NOW,
        search_function=lambda query, limit: [
            make_paper(
                "2608.10001v1",
                "2026-08-28T10:00:00Z",
            )
        ],
        europepmc_function=broken_europepmc,
    )

    assert len(result.selected_papers) == 1

    assert dict(result.source_errors) == {
        "europepmc": (
            "RuntimeError: service unavailable"
        )
    }


def test_same_paper_from_two_sources_is_one_paper() -> None:
    result = run_scan(
        multi_source_config(),
        default_state(),
        force=True,
        now=NOW,
        search_function=lambda query, limit: [
            make_paper(
                "2608.10001v1",
                "2026-08-28T10:00:00Z",
            )
        ],
        europepmc_function=(
            lambda query, limit, **kwargs: [
                make_europepmc_paper(
                    "PPR123",
                    "2026-08-28",
                    doi=(
                        "10.48550/arXiv.2608.10001"
                    ),
                )
            ]
        ),
    )

    assert result.candidate_count == 2
    assert result.unique_count == 1

    assert (
        result.selected_papers[0][0].source
        == "arxiv"
    )


def test_full_text_wins_a_relevance_tie() -> None:
    """
    Two equally relevant papers, one paywalled. The one
    that can actually be read should get the slot.
    """

    config = multi_source_config()

    config["retrieval"]["max_papers"] = 1

    result = run_scan(
        config,
        default_state(),
        force=True,
        now=NOW,
        search_function=lambda query, limit: [],
        europepmc_function=(
            lambda query, limit, **kwargs: [
                make_europepmc_paper(
                    "closed",
                    "2026-08-28",
                    doi="10.1/closed",
                    full_text=False,
                ),
                make_europepmc_paper(
                    "open",
                    "2026-08-28",
                    doi="10.1/open",
                    full_text=True,
                ),
            ]
        ),
    )

    assert len(result.selected_papers) == 1

    chosen = result.selected_papers[0][0]

    assert chosen.record_id == "open"
    assert chosen.full_text_available
