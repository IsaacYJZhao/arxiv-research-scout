from datetime import (
    datetime,
    timezone,
)

from arxiv_research_scout.models import (
    PaperRecord,
)

from arxiv_research_scout.state_manager import (
    default_state,
    migrate_state,
    filter_unprocessed_papers,
    has_processed_paper,
    is_run_due,
    load_state,
    mark_paper_processed,
    mark_run_successful,
    save_state,
)


def make_paper(
    record_id: str,
) -> PaperRecord:
    return PaperRecord(
        record_id=record_id,
        title="Example Paper",
        authors=("Example Author",),
        abstract="Example abstract.",
        published="2026-08-28T10:00:00Z",
        updated="2026-08-28T10:00:00Z",
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


def test_default_state() -> None:
    state = default_state()

    assert state["schema_version"] == 2

    assert (
        state["last_successful_run_utc"]
        is None
    )

    assert state["processed_ids"] == []


def test_state_round_trip(
    tmp_path,
) -> None:
    state_file = (
        tmp_path / "state.json"
    )

    state = default_state()

    mark_paper_processed(
        state,
        make_paper("2608.16855v1"),
    )

    save_state(
        state_file,
        state,
    )

    loaded = load_state(
        state_file
    )

    assert loaded == state


def test_versions_are_treated_as_same_paper() -> None:
    state = default_state()

    mark_paper_processed(
        state,
        make_paper("2608.16855v1"),
    )

    assert has_processed_paper(
        state,
        make_paper("2608.16855v2"),
    )


def test_filter_unprocessed_papers() -> None:
    state = default_state()

    mark_paper_processed(
        state,
        make_paper("2608.10001v1"),
    )

    papers = [
        make_paper(
            "2608.10001v2"
        ),
        make_paper(
            "2608.10002v1"
        ),
    ]

    remaining = (
        filter_unprocessed_papers(
            papers,
            state,
        )
    )

    assert len(remaining) == 1

    assert remaining[0].record_id == (
        "2608.10002v1"
    )


def test_first_run_is_due() -> None:
    state = default_state()

    assert is_run_due(
        state,
        run_every_days=3,
    )


def test_run_is_not_due_before_interval() -> None:
    state = default_state()

    state["last_successful_run_utc"] = (
        "2026-08-28T12:00:00+00:00"
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

    assert not is_run_due(
        state,
        run_every_days=3,
        now=now,
    )


def test_run_is_due_after_interval() -> None:
    state = default_state()

    state["last_successful_run_utc"] = (
        "2026-08-25T12:00:00+00:00"
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

    assert is_run_due(
        state,
        run_every_days=3,
        now=now,
    )


def test_mark_run_successful() -> None:
    state = default_state()

    now = datetime(
        2026,
        8,
        29,
        12,
        0,
        0,
        tzinfo=timezone.utc,
    )

    mark_run_successful(
        state,
        now=now,
    )

    assert (
        state[
            "last_successful_run_utc"
        ]
        ==
        "2026-08-29T12:00:00+00:00"
    )

def test_schema_1_ids_are_migrated_to_arxiv_keys() -> None:
    """
    Schema 1 stored bare arXiv IDs. They must keep
    matching the papers they were recorded for, or every
    already-analyzed paper would be analyzed again.
    """

    state = {
        "schema_version": 1,
        "last_successful_run_utc": (
            "2026-09-03T12:52:17+00:00"
        ),
        "processed_ids": [
            "2608.16855",
            "2608.14766",
        ],
    }

    migrated = migrate_state(state)

    assert migrated["schema_version"] == 2

    assert migrated["processed_ids"] == [
        "arxiv:2608.16855",
        "arxiv:2608.14766",
    ]

    assert has_processed_paper(
        migrated,
        make_paper("2608.16855v3"),
    )


def test_migration_is_idempotent() -> None:
    state = {
        "schema_version": 1,
        "processed_ids": [
            "arxiv:2608.16855",
            "doi:10.1007/s10278-1",
            "2608.14766",
            "",
        ],
    }

    once = migrate_state(dict(state))
    twice = migrate_state(dict(once))

    assert once["processed_ids"] == [
        "arxiv:2608.16855",
        "doi:10.1007/s10278-1",
        "arxiv:2608.14766",
    ]

    assert twice == once


def test_load_state_migrates_on_disk_format(
    tmp_path,
) -> None:
    import json

    state_file = tmp_path / "state.json"

    state_file.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "last_successful_run_utc": None,
                "processed_ids": ["2608.16855"],
            }
        ),
        encoding="utf-8",
    )

    loaded = load_state(state_file)

    assert loaded["schema_version"] == 2

    assert loaded["processed_ids"] == [
        "arxiv:2608.16855"
    ]
