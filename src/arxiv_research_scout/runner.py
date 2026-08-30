from __future__ import annotations

import argparse
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from arxiv_research_scout.arxiv_client import (
    build_search_query,
    search_arxiv,
)
from arxiv_research_scout.config import load_config
from arxiv_research_scout.models import ArxivPaper
from arxiv_research_scout.paper_filters import (
    deduplicate_papers,
    filter_recent_papers,
)
from arxiv_research_scout.paths import (
    resolve_project_path,
)
from arxiv_research_scout.state_manager import (
    filter_unprocessed_papers,
    is_run_due,
    load_state,
)


SearchFunction = Callable[
    [str, int],
    list[ArxivPaper],
]


@dataclass(frozen=True, slots=True)
class ScanResult:
    """
    Result of one arXiv scan.

    This object contains only retrieval/filtering
    information. It does not modify persistent state.
    """

    due: bool
    candidate_count: int
    recent_count: int
    unique_count: int
    unprocessed_count: int
    selected_papers: tuple[ArxivPaper, ...]


def run_scan(
    config: dict[str, Any],
    state: dict[str, Any],
    *,
    force: bool = False,
    now: datetime | None = None,
    search_function: SearchFunction = search_arxiv,
) -> ScanResult:
    """
    Run one retrieval/filtering cycle.

    This function intentionally does NOT mark papers
    as processed and does NOT update last successful run.

    Persistent state will only be updated later after
    analysis and report generation succeed.
    """

    run_every_days = config["schedule"][
        "run_every_days"
    ]

    due = (
        force
        or is_run_due(
            state,
            run_every_days=run_every_days,
            now=now,
        )
    )

    if not due:
        return ScanResult(
            due=False,
            candidate_count=0,
            recent_count=0,
            unique_count=0,
            unprocessed_count=0,
            selected_papers=(),
        )

    topic_config = config["topic"]

    query = build_search_query(
        topic_config["arxiv_query"],
        topic_config.get(
            "categories",
            [],
        ),
    )

    candidate_papers = search_function(
        query,
        config["retrieval"][
            "max_candidates"
        ],
    )

    recent_papers = filter_recent_papers(
        papers=candidate_papers,
        lookback_days=config["schedule"][
            "lookback_days"
        ],
        now=now,
    )

    unique_papers = deduplicate_papers(
        recent_papers
    )

    unprocessed_papers = (
        filter_unprocessed_papers(
            unique_papers,
            state,
        )
    )

    max_papers = config["retrieval"][
        "max_papers"
    ]

    selected_papers = tuple(
        unprocessed_papers[:max_papers]
    )

    return ScanResult(
        due=True,
        candidate_count=len(
            candidate_papers
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
        selected_papers=selected_papers,
    )


def print_scan_result(
    config: dict[str, Any],
    result: ScanResult,
) -> None:
    """
    Print a human-readable scan summary.
    """

    print()
    print(
        "===== arXiv Research Scout ====="
    )
    print()

    print(
        f"Topic: "
        f"{config['topic']['name']}"
    )

    if not result.due:
        print()
        print(
            "Scan skipped: "
            "the configured interval "
            "has not elapsed yet."
        )
        return

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
        f"Selected for analysis: "
        f"{len(result.selected_papers)}"
    )

    if not result.selected_papers:
        print()
        print(
            "No new papers selected."
        )
        return

    for index, paper in enumerate(
        result.selected_papers,
        start=1,
    ):
        print()
        print("=" * 72)
        print(f"Paper {index}")
        print("=" * 72)

        print(
            f"arXiv ID : "
            f"{paper.arxiv_id}"
        )

        print(
            f"Published: "
            f"{paper.published}"
        )

        print(
            f"Title    : "
            f"{paper.title}"
        )

        print(
            f"PDF      : "
            f"{paper.pdf_url}"
        )


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    """

    parser = argparse.ArgumentParser(
        description=(
            "Search arXiv for new papers "
            "matching the configured topic."
        )
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Run even if the configured "
            "schedule interval has not elapsed."
        ),
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    config = load_config()

    state_file = resolve_project_path(
        config["state"]["file"]
    )

    state = load_state(
        state_file
    )

    result = run_scan(
        config=config,
        state=state,
        force=args.force,
    )

    print_scan_result(
        config,
        result,
    )


if __name__ == "__main__":
    main()