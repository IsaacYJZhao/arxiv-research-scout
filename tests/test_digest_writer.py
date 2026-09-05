from datetime import (
    datetime,
    timezone,
)
from pathlib import Path

from arxiv_research_scout.digest_writer import (
    build_digest_markdown,
    digest_filename,
    write_digest,
)
from arxiv_research_scout.models import (
    PaperRecord,
    BatchProcessingResult,
    LLMProviderSettings,
    PaperAnalysisContext,
    PaperAnalysisResult,
    PaperCommitResult,
    PaperProcessingFailure,
    PaperProcessingResult,
)
from arxiv_research_scout.runner import (
    ScanResult,
)


FIXED_TIME = datetime(
    2026,
    8,
    30,
    20,
    0,
    0,
    tzinfo=timezone.utc,
)


def make_paper() -> PaperRecord:
    return PaperRecord(
        record_id="2608.10000v1",
        title="Example Lung Nodule Paper",
        authors=(
            "Alice Example",
            "Bob Example",
        ),
        abstract="Abstract.",
        published="2026-08-28T10:00:00Z",
        updated="2026-08-28T10:00:00Z",
        categories=("cs.CV",),
        abs_url=(
            "https://arxiv.org/abs/"
            "2608.10000v1"
        ),
        pdf_url=(
            "https://arxiv.org/pdf/"
            "2608.10000v1"
        ),
    )


def make_commit(
    tmp_path: Path,
) -> PaperCommitResult:
    paper = make_paper()

    context = PaperAnalysisContext(
        record_id=paper.record_id,
        title=paper.title,
        authors=paper.authors,
        abstract=paper.abstract,
        introduction="Introduction.",
        methodology="Method evidence.",
        experiments="Experiments.",
        results="Results.",
        discussion="Discussion.",
        conclusion="Conclusion.",
        pdf_text_available=True,
    )

    analysis = PaperAnalysisResult(
        methodology="方法总结。",
        evaluation="评估总结。",
        innovation="创新总结。",
        datasets=("LUNA16",),
        metrics=("FROC",),
        key_results=(
            "报告了关键实验结果。",
        ),
        limitations=(
            "外部验证未报告。"
        ),
        evidence_level="full_text",
        confidence="high",
    )

    processing = PaperProcessingResult(
        paper=paper,
        context=context,
        analysis=analysis,
        pdf_error=None,
    )

    return PaperCommitResult(
        processing=processing,
        report_path=(
            tmp_path
            / "2608.10000v1.md"
        ),
    )


def make_scan(
    *,
    selected_count: int = 1,
) -> ScanResult:
    paper = make_paper()

    selected = tuple(
        (
            paper,
            10,
            "high",
        )
        for _ in range(
            selected_count
        )
    )

    return ScanResult(
        due=True,
        candidate_count=40,
        recent_count=5,
        unique_count=5,
        unprocessed_count=4,
        relevant_count=3,
        selected_papers=selected,
    )


def make_settings() -> LLMProviderSettings:
    return LLMProviderSettings(
        provider="deepseek",
        model="deepseek-v4-pro",
        api_key_env="DEEPSEEK_API_KEY",
        base_url=(
            "https://api.deepseek.com"
        ),
        max_output_tokens=2500,
    )


def test_digest_filename_uses_utc_date() -> None:
    assert digest_filename(
        FIXED_TIME
    ) == "2026-08-30.md"


def test_digest_contains_run_summary(
    tmp_path: Path,
) -> None:
    batch = BatchProcessingResult(
        committed=(
            make_commit(
                tmp_path
            ),
        ),
        failures=(),
        run_marked_successful=True,
    )

    markdown = build_digest_markdown(
        make_scan(),
        batch,
        settings=make_settings(),
        generated_at=FIXED_TIME,
    )

    assert (
        "**Provider:** deepseek"
        in markdown
    )

    assert (
        "**Model:** deepseek-v4-pro"
        in markdown
    )

    assert (
        "**Candidates retrieved:** 40"
        in markdown
    )

    assert (
        "**Successfully analyzed:** 1"
        in markdown
    )


def test_digest_contains_paper_analysis(
    tmp_path: Path,
) -> None:
    batch = BatchProcessingResult(
        committed=(
            make_commit(
                tmp_path
            ),
        ),
        failures=(),
        run_marked_successful=True,
    )

    markdown = build_digest_markdown(
        make_scan(),
        batch,
        settings=make_settings(),
        generated_at=FIXED_TIME,
    )

    assert (
        "## 1. Example Lung Nodule Paper"
        in markdown
    )

    assert "### Methodology" in markdown
    assert "方法总结。" in markdown

    assert "### Evaluation" in markdown
    assert "评估总结。" in markdown

    assert "### Innovation" in markdown
    assert "创新总结。" in markdown

    assert "- LUNA16" in markdown
    assert "- FROC" in markdown


def test_digest_contains_failures(
    tmp_path: Path,
) -> None:
    failure = PaperProcessingFailure(
        record_id="2608.99999v1",
        title="Failed Paper",
        error="RuntimeError: API failed",
    )

    batch = BatchProcessingResult(
        committed=(
            make_commit(
                tmp_path
            ),
        ),
        failures=(failure,),
        run_marked_successful=False,
    )

    markdown = build_digest_markdown(
        make_scan(),
        batch,
        settings=make_settings(),
        generated_at=FIXED_TIME,
    )

    assert (
        "**Run status:** partial"
        in markdown
    )

    assert (
        "## Processing Failures"
        in markdown
    )

    assert (
        "RuntimeError: API failed"
        in markdown
    )


def test_empty_batch_is_reported() -> None:
    batch = BatchProcessingResult(
        committed=(),
        failures=(),
        run_marked_successful=True,
    )

    markdown = build_digest_markdown(
        make_scan(
            selected_count=0
        ),
        batch,
        settings=make_settings(),
        generated_at=FIXED_TIME,
    )

    assert (
        "No papers were successfully "
        "analyzed in this run."
        in markdown
    )

    assert (
        "**Successfully analyzed:** 0"
        in markdown
    )


def test_write_digest_is_atomic(
    tmp_path: Path,
) -> None:
    batch = BatchProcessingResult(
        committed=(
            make_commit(
                tmp_path
            ),
        ),
        failures=(),
        run_marked_successful=True,
    )

    digest_path = write_digest(
        make_scan(),
        batch,
        settings=make_settings(),
        digests_dir=tmp_path,
        generated_at=FIXED_TIME,
    )

    assert digest_path.exists()

    assert digest_path.name == (
        "2026-08-30.md"
    )

    assert not (
        tmp_path
        / "2026-08-30.md.tmp"
    ).exists()

    content = digest_path.read_text(
        encoding="utf-8"
    )

    assert (
        "# Research Digest"
        in content
    )
