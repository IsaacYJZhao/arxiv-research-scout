from __future__ import annotations

import argparse
from collections.abc import (
    Callable,
    Sequence,
)
from dataclasses import dataclass
from datetime import datetime

from arxiv_research_scout.arxiv_client import (
    build_search_query,
    search_arxiv,
)
from arxiv_research_scout.config import (
    load_config,
)
from arxiv_research_scout.models import (
    PaperRecord,
)
from arxiv_research_scout.paper_filters import (
    deduplicate_papers,
    filter_recent_papers,
)
from arxiv_research_scout.paths import (
    resolve_project_path,
)
from arxiv_research_scout.relevance import (
    rank_relevant_papers,
)
from arxiv_research_scout.sources.europepmc import (
    search_europepmc,
)
from arxiv_research_scout.state_manager import (
    filter_unprocessed_papers,
    is_run_due,
    load_state,
)


SearchFunction = Callable[
    [str, int],
    list[PaperRecord],
]


SelectedPaper = tuple[
    PaperRecord,
    int,
    str,
]


@dataclass(
    frozen=True,
    slots=True,
)
class ScanResult:
    """
    Result of one retrieval and relevance scan.

    This object contains no LLM analysis and does
    not modify persistent state.

    source_counts records how many candidates each
    source contributed, before deduplication. It is
    what tells you whether a source is silently
    returning nothing.

    source_errors records sources that failed. A failing
    source is reported rather than raised, so one
    unavailable service cannot cost a whole run.
    """

    due: bool

    candidate_count: int
    recent_count: int
    unique_count: int
    unprocessed_count: int
    relevant_count: int

    selected_papers: tuple[
        SelectedPaper,
        ...,
    ]

    source_counts: tuple[
        tuple[str, int],
        ...,
    ] = ()

    source_errors: tuple[
        tuple[str, str],
        ...,
    ] = ()


def empty_scan_result(
    *,
    due: bool,
) -> ScanResult:
    """
    Construct an empty ScanResult.

    This is primarily used when the configured
    scheduling interval has not elapsed.
    """

    return ScanResult(
        due=due,
        candidate_count=0,
        recent_count=0,
        unique_count=0,
        unprocessed_count=0,
        relevant_count=0,
        selected_papers=(),
    )


SourceSearchFunction = Callable[
    ...,
    list[PaperRecord],
]


def collect_candidates(
    config: dict,
    *,
    lookback_days: int,
    now: datetime | None,
    arxiv_search: SearchFunction,
    europepmc_search: SourceSearchFunction,
) -> tuple[
    list[PaperRecord],
    list[tuple[str, int]],
    list[tuple[str, str]],
]:
    """
    Query every enabled retrieval source.

    Sources are queried in a fixed order and their
    results concatenated, because deduplication keeps
    the first occurrence of a paper: arXiv first, so
    that a preprint with a downloadable PDF wins over
    the paywalled journal record of the same work.

    A source that fails is recorded and skipped rather
    than raised. Losing one source degrades a run;
    aborting it loses the papers every other source
    found.
    """

    sources_config = config.get(
        "sources",
        {},
    )

    candidates: list[PaperRecord] = []
    counts: list[tuple[str, int]] = []
    errors: list[tuple[str, str]] = []

    # --------------------------------------------------
    # arXiv
    # --------------------------------------------------

    arxiv_config = sources_config.get(
        "arxiv",
        {},
    )

    if arxiv_config.get("enabled", True):
        topic_config = config["topic"]

        retrieval_config = config["retrieval"]

        query = build_search_query(
            str(
                topic_config["arxiv_query"]
            ).strip(),
            tuple(
                topic_config.get(
                    "categories",
                    (),
                )
            ),
        )

        try:
            papers = arxiv_search(
                query,
                int(
                    retrieval_config[
                        "max_candidates"
                    ]
                ),
            )

        except Exception as error:
            errors.append(
                (
                    "arxiv",
                    f"{type(error).__name__}: {error}",
                )
            )

        else:
            candidates.extend(papers)
            counts.append(
                ("arxiv", len(papers))
            )

    # --------------------------------------------------
    # Europe PMC
    #
    # Disabled unless configured, so an existing
    # configuration keeps behaving exactly as before.
    # --------------------------------------------------

    europepmc_config = sources_config.get(
        "europepmc",
        {},
    )

    if europepmc_config.get("enabled", False):
        query = str(
            europepmc_config.get("query", "")
        ).strip()

        if not query:
            errors.append(
                (
                    "europepmc",
                    "Enabled but no query configured.",
                )
            )

        else:
            try:
                papers = europepmc_search(
                    query,
                    int(
                        europepmc_config.get(
                            "max_candidates",
                            50,
                        )
                    ),
                    lookback_days=lookback_days,
                    now=now,
                )

            except Exception as error:
                errors.append(
                    (
                        "europepmc",
                        f"{type(error).__name__}: "
                        f"{error}",
                    )
                )

            else:
                candidates.extend(papers)
                counts.append(
                    (
                        "europepmc",
                        len(papers),
                    )
                )

    return candidates, counts, errors


def run_scan(
    config: dict,
    state: dict,
    *,
    force: bool = False,
    now: datetime | None = None,
    search_function: SearchFunction = (
        search_arxiv
    ),
    europepmc_function: SourceSearchFunction = (
        search_europepmc
    ),
) -> ScanResult:
    """
    Run the retrieval and relevance-selection stage.

    Pipeline:

        schedule check
            ->
        arXiv retrieval
            ->
        lookback filtering
            ->
        arXiv-ID deduplication
            ->
        processed-ID filtering
            ->
        relevance ranking
            ->
        select top papers

    Important:
    This function never modifies state.
    """

    schedule_config = config[
        "schedule"
    ]

    run_every_days = int(
        schedule_config[
            "run_every_days"
        ]
    )

    if (
        not force
        and not is_run_due(
            state,
            run_every_days,
            now=now,
        )
    ):
        return empty_scan_result(
            due=False
        )

    retrieval_config = config[
        "retrieval"
    ]

    relevance_config = config[
        "relevance"
    ]

    lookback_days = int(
        schedule_config[
            "lookback_days"
        ]
    )

    (
        candidates,
        source_counts,
        source_errors,
    ) = collect_candidates(
        config,
        lookback_days=lookback_days,
        now=now,
        arxiv_search=search_function,
        europepmc_search=europepmc_function,
    )

    recent_papers = (
        filter_recent_papers(
            candidates,
            lookback_days,
            now=now,
        )
    )

    unique_papers = (
        deduplicate_papers(
            recent_papers
        )
    )

    unprocessed_papers = (
        filter_unprocessed_papers(
            unique_papers,
            state,
        )
    )

    ranked_papers = (
        rank_relevant_papers(
            unprocessed_papers,
            relevance_config,
        )
    )

    max_papers = int(
        retrieval_config[
            "max_papers"
        ]
    )

    # Relevance decides what is worth reading; among
    # equally relevant papers, prefer the ones whose
    # full text can actually be downloaded, because an
    # abstract-only analysis is much weaker. Python's
    # sort is stable, so relevance order survives.
    prioritized = sorted(
        ranked_papers,
        key=lambda item: (
            item[1].score,
            item[0].full_text_available,
        ),
        reverse=True,
    )

    selected_ranked = (
        prioritized[
            :max_papers
        ]
    )

    selected_papers: list[
        SelectedPaper
    ] = []

    for (
        paper,
        assessment,
    ) in selected_ranked:
        selected_papers.append(
            (
                paper,
                assessment.score,
                assessment.level,
            )
        )

    return ScanResult(
        due=True,
        candidate_count=len(
            candidates
        ),
        recent_count=len(
            recent_papers
        ),
        unique_count=len(
            unique_papers
        ),
        unprocessed_count=len(
            unprocessed_papers
        ),
        relevant_count=len(
            ranked_papers
        ),
        selected_papers=tuple(
            selected_papers
        ),
        source_counts=tuple(
            source_counts
        ),
        source_errors=tuple(
            source_errors
        ),
    )


def print_scan_result(
    config: dict,
    result: ScanResult,
) -> None:
    """
    Print a human-readable scan summary.
    """

    topic_name = str(
        config[
            "topic"
        ][
            "name"
        ]
    )

    print()
    print(
        "===== arXiv Research Scout ====="
    )
    print()

    print(
        f"Topic: {topic_name}"
    )
    print()

    if not result.due:
        print(
            "Run is not due yet."
        )
        return

    for source_name, count in (
        result.source_counts
    ):
        print(
            f"  from {source_name:<12}: "
            f"{count}"
        )

    for source_name, message in (
        result.source_errors
    ):
        print(
            f"  {source_name} FAILED  : "
            f"{message}"
        )

    if result.source_counts or result.source_errors:
        print()

    print(
        f"Candidates retrieved : "
        f"{result.candidate_count}"
    )

    print(
        f"Recent papers        : "
        f"{result.recent_count}"
    )

    print(
        f"After ID dedup       : "
        f"{result.unique_count}"
    )

    print(
        f"Unprocessed papers   : "
        f"{result.unprocessed_count}"
    )

    print(
        f"Relevant papers      : "
        f"{result.relevant_count}"
    )

    print(
        f"Selected for analysis: "
        f"{len(result.selected_papers)}"
    )

    if not result.selected_papers:
        print()
        print(
            "No new papers selected."
        )
        return

    print()
    print(
        "Selected papers:"
    )

    for (
        index,
        selected,
    ) in enumerate(
        result.selected_papers,
        start=1,
    ):
        paper, score, level = (
            selected
        )

        print()

        print(
            f"{index}. "
            f"{paper.title}"
        )

        print(
            f"   Paper ID  : "
            f"{paper.record_id}"
        )

        print(
            f"   Relevance : "
            f"{score} ({level})"
        )

        print(
            f"   Source    : "
            f"{paper.source}"
            + (
                f" | {paper.venue}"
                if paper.venue
                else ""
            )
        )

        print(
            f"   Full text : "
            f"{'yes' if paper.full_text_available else 'abstract only'}"
        )

        print(
            f"   Published : "
            f"{paper.published}"
        )

        print(
            f"   URL       : "
            f"{paper.abs_url}"
        )


def build_parser(
) -> argparse.ArgumentParser:
    """
    Build the legacy runner-only CLI.

    The project's primary CLI is now cli.py, but this
    entry point is retained for backward compatibility.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Run the arXiv retrieval "
            "and relevance scan."
        )
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Ignore the configured "
            "scheduling interval."
        ),
    )

    return parser


def main(
    argv: Sequence[str] | None = None,
) -> int:
    """
    Standalone scan-only entry point.

    For the complete workflow, use:

        arxiv-scout run
    """

    parser = build_parser()

    args = parser.parse_args(
        argv
    )

    config = load_config()

    state_file = resolve_project_path(
        config[
            "state"
        ][
            "file"
        ]
    )

    state = load_state(
        state_file
    )

    result = run_scan(
        config,
        state,
        force=args.force,
    )

    print_scan_result(
        config,
        result,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )