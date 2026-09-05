from __future__ import annotations

import json
from datetime import (
    datetime,
    timedelta,
    timezone,
)
from pathlib import Path
from typing import Any

from arxiv_research_scout.models import (
    PaperRecord,
)

from arxiv_research_scout.paper_filters import (
    record_key,
)


# Schema history:
#
#   1: processed_ids held bare arXiv IDs, because arXiv
#      was the only retrieval source.
#
#   2: processed_ids holds cross-source record keys, so
#      that the same work retrieved from two sources is
#      recognized as already processed.
SCHEMA_VERSION = 2


def default_state() -> dict[str, Any]:
    """
    Return a fresh application state.
    """

    return {
        "schema_version": SCHEMA_VERSION,
        "last_successful_run_utc": None,
        "processed_ids": [],
    }


def migrate_state(
    state: dict[str, Any],
) -> dict[str, Any]:
    """
    Bring a state document up to the current schema.

    Schema 1 stored bare arXiv IDs. Those become
    arxiv:<id> keys so that they keep matching the
    papers they were recorded for.

    Entries that already look like keys are left alone,
    which makes this migration safe to run repeatedly.
    """

    version = state.get(
        "schema_version",
        1,
    )

    if version >= SCHEMA_VERSION:
        return state

    migrated_ids: list[str] = []

    for entry in state.get(
        "processed_ids",
        [],
    ):
        text = str(entry).strip()

        if not text:
            continue

        if ":" in text:
            migrated_ids.append(text)
            continue

        migrated_ids.append(
            f"arxiv:{text}"
        )

    state["processed_ids"] = migrated_ids
    state["schema_version"] = SCHEMA_VERSION

    return state


def load_state(
    state_file: Path,
) -> dict[str, Any]:
    """
    Load state from disk, migrating it if necessary.

    If the file does not exist, return a fresh state.
    """

    if not state_file.exists():
        return default_state()

    with state_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        state = json.load(file)

    if not isinstance(state, dict):
        raise ValueError(
            "State file must contain "
            "a JSON object."
        )

    return migrate_state(state)


def save_state(
    state_file: Path,
    state: dict[str, Any],
) -> None:
    """
    Save state atomically.

    A temporary file is written first,
    then replaces the old state file.
    """

    state_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file = state_file.with_suffix(
        state_file.suffix + ".tmp"
    )

    with temporary_file.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            state,
            file,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )

        file.write("\n")

    temporary_file.replace(
        state_file
    )


def has_processed_paper(
    state: dict[str, Any],
    paper: PaperRecord,
) -> bool:
    """
    Check whether a paper has already been
    successfully processed.
    """

    return record_key(paper) in state.get(
        "processed_ids",
        [],
    )


def filter_unprocessed_papers(
    papers: list[PaperRecord],
    state: dict[str, Any],
) -> list[PaperRecord]:
    """
    Keep only papers that have not been
    successfully processed before.
    """

    return [
        paper
        for paper in papers
        if not has_processed_paper(
            state,
            paper,
        )
    ]


def mark_paper_processed(
    state: dict[str, Any],
    paper: PaperRecord,
) -> None:
    """
    Mark one paper as successfully processed.
    """

    key = record_key(paper)

    processed_ids = state.setdefault(
        "processed_ids",
        [],
    )

    if key not in processed_ids:
        processed_ids.append(key)


def is_run_due(
    state: dict[str, Any],
    run_every_days: int,
    now: datetime | None = None,
) -> bool:
    """
    Return True when enough time has passed
    since the last successful run.
    """

    if run_every_days < 1:
        raise ValueError(
            "run_every_days must be "
            "at least 1."
        )

    last_run_text = state.get(
        "last_successful_run_utc"
    )

    if not last_run_text:
        return True

    last_run = datetime.fromisoformat(
        last_run_text
    )

    if last_run.tzinfo is None:
        last_run = last_run.replace(
            tzinfo=timezone.utc
        )

    current_time = (
        now
        if now is not None
        else datetime.now(timezone.utc)
    )

    if current_time.tzinfo is None:
        current_time = current_time.replace(
            tzinfo=timezone.utc
        )

    next_run = (
        last_run.astimezone(timezone.utc)
        + timedelta(days=run_every_days)
    )

    return (
        current_time.astimezone(timezone.utc)
        >= next_run
    )


def mark_run_successful(
    state: dict[str, Any],
    now: datetime | None = None,
) -> None:
    """
    Record a successfully completed run.
    """

    current_time = (
        now
        if now is not None
        else datetime.now(timezone.utc)
    )

    if current_time.tzinfo is None:
        current_time = current_time.replace(
            tzinfo=timezone.utc
        )

    state["last_successful_run_utc"] = (
        current_time
        .astimezone(timezone.utc)
        .isoformat()
    )
