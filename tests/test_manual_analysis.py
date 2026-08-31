from pathlib import Path

from arxiv_research_scout.manual_analysis import (
    analyze_single_paper,
)
from arxiv_research_scout.models import (
    ArxivPaper,
    PaperAnalysisContext,
    PaperAnalysisResult,
    PaperProcessingResult,
)


def make_config() -> dict:
    return {
        "llm": {
            "default_provider": "openai",
            "max_context_chars": 45000,
            "max_output_tokens": 2500,
            "openai": {
                "model": "gpt-5.6-terra",
            },
            "deepseek": {
                "model": "deepseek-v4-pro",
                "base_url": (
                    "https://api.deepseek.com"
                ),
            },
        }
    }


def make_paper() -> ArxivPaper:
    return ArxivPaper(
        arxiv_id="2608.16855v1",
        title="Example Paper",
        authors=("Alice Example",),
        abstract="Abstract.",
        published="2026-08-28T10:00:00Z",
        updated="2026-08-28T10:00:00Z",
        categories=("cs.CV",),
        abs_url=(
            "https://arxiv.org/abs/"
            "2608.16855v1"
        ),
        pdf_url=(
            "https://arxiv.org/pdf/"
            "2608.16855v1"
        ),
    )


def make_processing() -> PaperProcessingResult:
    paper = make_paper()

    context = PaperAnalysisContext(
        arxiv_id=paper.arxiv_id,
        title=paper.title,
        authors=paper.authors,
        abstract=paper.abstract,
        introduction="Introduction.",
        methodology="Method.",
        experiments="Experiments.",
        results="Results.",
        discussion="Discussion.",
        conclusion="Conclusion.",
        pdf_text_available=True,
    )

    analysis = PaperAnalysisResult(
        methodology="Method.",
        evaluation="Evaluation.",
        innovation="Innovation.",
        datasets=(),
        metrics=(),
        key_results=(),
        limitations="Limitations.",
        evidence_level="full_text",
        confidence="high",
    )

    return PaperProcessingResult(
        paper=paper,
        context=context,
        analysis=analysis,
        pdf_error=None,
    )


def test_manual_report_uses_provider_directory(
    tmp_path: Path,
) -> None:
    captured = {}

    def fake_lookup(
        arxiv_id: str,
    ):
        return make_paper()

    def fake_key_loader(
        settings,
    ):
        return "secret"

    def fake_client_factory(
        settings,
        *,
        api_key,
    ):
        return object()

    def fake_processor(
        paper,
        **kwargs,
    ):
        return make_processing()

    def fake_report_writer(
        result,
        *,
        settings,
        reports_dir,
    ):
        captured["reports_dir"] = (
            reports_dir
        )

        return (
            reports_dir
            / "2608.16855v1.md"
        )

    result = analyze_single_paper(
        "2608.16855v1",
        config=make_config(),
        reports_root=tmp_path,
        provider_override="deepseek",
        paper_lookup=fake_lookup,
        processor=fake_processor,
        api_key_loader=fake_key_loader,
        client_factory=(
            fake_client_factory
        ),
        report_writer=(
            fake_report_writer
        ),
    )

    assert captured[
        "reports_dir"
    ] == (
        tmp_path
        / "manual"
        / "deepseek"
    )

    assert (
        result.settings.provider
        == "deepseek"
    )


def test_manual_model_override_is_used(
    tmp_path: Path,
) -> None:
    captured = {}

    def fake_lookup(
        arxiv_id: str,
    ):
        return make_paper()

    def fake_key_loader(
        settings,
    ):
        captured["settings"] = (
            settings
        )

        return "secret"

    def fake_client_factory(
        settings,
        *,
        api_key,
    ):
        return object()

    def fake_processor(
        paper,
        **kwargs,
    ):
        return make_processing()

    def fake_report_writer(
        result,
        *,
        settings,
        reports_dir,
    ):
        return (
            reports_dir
            / "report.md"
        )

    analyze_single_paper(
        "2608.16855v1",
        config=make_config(),
        reports_root=tmp_path,
        provider_override="openai",
        model_override=(
            "temporary-model"
        ),
        paper_lookup=fake_lookup,
        processor=fake_processor,
        api_key_loader=fake_key_loader,
        client_factory=(
            fake_client_factory
        ),
        report_writer=(
            fake_report_writer
        ),
    )

    assert (
        captured[
            "settings"
        ].model
        == "temporary-model"
    )


def test_lookup_happens_before_api_key_loading(
    tmp_path: Path,
) -> None:
    key_called = False

    def failing_lookup(
        arxiv_id: str,
    ):
        raise LookupError(
            "not found"
        )

    def fake_key_loader(
        settings,
    ):
        nonlocal key_called
        key_called = True
        return "secret"

    try:
        analyze_single_paper(
            "2608.00000v1",
            config=make_config(),
            reports_root=tmp_path,
            paper_lookup=failing_lookup,
            api_key_loader=(
                fake_key_loader
            ),
        )
    except LookupError:
        pass

    assert not key_called