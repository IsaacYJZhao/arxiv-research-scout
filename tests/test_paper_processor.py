import pytest

from arxiv_research_scout.models import (
    ArxivPaper,
    LLMProviderSettings,
    PaperAnalysisResult,
    PaperSections,
)
from arxiv_research_scout.paper_processor import (
    process_paper,
)


def make_paper(
    *,
    abstract: str = "Official arXiv abstract.",
) -> ArxivPaper:
    return ArxivPaper(
        arxiv_id="2608.10000v1",
        title="Example Paper",
        authors=("Alice Example",),
        abstract=abstract,
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


def make_config() -> dict:
    return {
        "pdf": {
            "timeout_seconds": 90,
            "max_attempts": 3,
            "max_download_mb": 50,
            "max_text_chars": 70000,
        },
        "llm": {
            "max_context_chars": 45000,
        },
        "output": {
            "language": "zh-CN",
        },
    }


def make_settings() -> LLMProviderSettings:
    return LLMProviderSettings(
        provider="openai",
        model="test-model",
        api_key_env="OPENAI_API_KEY",
        base_url=None,
        max_output_tokens=2500,
    )


def make_analysis() -> PaperAnalysisResult:
    return PaperAnalysisResult(
        methodology="Method summary.",
        evaluation="Evaluation summary.",
        innovation="Innovation summary.",
        datasets=("LUNA16",),
        metrics=("FROC",),
        key_results=("Result.",),
        limitations="Limitations.",
        evidence_level="full_text",
        confidence="high",
    )


def test_successful_pdf_pipeline() -> None:
    captured = {}

    def fake_pdf_fetcher(
        url: str,
        **kwargs,
    ) -> str:
        return "PDF text"

    def fake_parser(
        text: str,
    ) -> PaperSections:
        return PaperSections(
            methodology="Method evidence.",
            experiments="Experiment evidence.",
            results="Result evidence.",
        )

    def fake_analyzer(
        context,
        **kwargs,
    ) -> PaperAnalysisResult:
        captured["context"] = context
        return make_analysis()

    result = process_paper(
        make_paper(),
        config=make_config(),
        client=object(),
        settings=make_settings(),
        pdf_fetcher=fake_pdf_fetcher,
        section_parser=fake_parser,
        analyzer=fake_analyzer,
    )

    assert result.pdf_error is None

    assert (
        captured["context"].methodology
        == "Method evidence."
    )

    assert (
        captured[
            "context"
        ].pdf_text_available
    )


def test_pdf_failure_falls_back_to_abstract() -> None:
    captured = {}

    def failing_pdf_fetcher(
        url: str,
        **kwargs,
    ) -> str:
        raise RuntimeError(
            "download failed"
        )

    def fake_analyzer(
        context,
        **kwargs,
    ) -> PaperAnalysisResult:
        captured["context"] = context
        return make_analysis()

    result = process_paper(
        make_paper(),
        config=make_config(),
        client=object(),
        settings=make_settings(),
        pdf_fetcher=(
            failing_pdf_fetcher
        ),
        analyzer=fake_analyzer,
    )

    context = captured["context"]

    assert (
        context.abstract
        == "Official arXiv abstract."
    )

    assert not (
        context.pdf_text_available
    )

    assert result.pdf_error == (
        "RuntimeError: download failed"
    )


def test_parser_failure_falls_back_to_abstract() -> None:
    captured = {}

    def fake_pdf_fetcher(
        url: str,
        **kwargs,
    ) -> str:
        return "PDF text"

    def failing_parser(
        text: str,
    ) -> PaperSections:
        raise ValueError(
            "parse failed"
        )

    def fake_analyzer(
        context,
        **kwargs,
    ) -> PaperAnalysisResult:
        captured["context"] = context
        return make_analysis()

    result = process_paper(
        make_paper(),
        config=make_config(),
        client=object(),
        settings=make_settings(),
        pdf_fetcher=fake_pdf_fetcher,
        section_parser=failing_parser,
        analyzer=fake_analyzer,
    )

    assert not (
        captured[
            "context"
        ].pdf_text_available
    )

    assert result.pdf_error == (
        "ValueError: parse failed"
    )


def test_analyzer_failure_is_not_swallowed() -> None:
    def fake_pdf_fetcher(
        url: str,
        **kwargs,
    ) -> str:
        return "PDF text"

    def fake_parser(
        text: str,
    ) -> PaperSections:
        return PaperSections(
            methodology="Method.",
            results="Results.",
        )

    def failing_analyzer(
        context,
        **kwargs,
    ) -> PaperAnalysisResult:
        raise RuntimeError(
            "LLM failed"
        )

    with pytest.raises(
        RuntimeError,
        match="LLM failed",
    ):
        process_paper(
            make_paper(),
            config=make_config(),
            client=object(),
            settings=make_settings(),
            pdf_fetcher=(
                fake_pdf_fetcher
            ),
            section_parser=fake_parser,
            analyzer=failing_analyzer,
        )


def test_pdf_settings_are_forwarded() -> None:
    captured = {}

    def fake_pdf_fetcher(
        url: str,
        **kwargs,
    ) -> str:
        captured["url"] = url
        captured["kwargs"] = kwargs
        return "PDF text"

    def fake_parser(
        text: str,
    ) -> PaperSections:
        return PaperSections(
            methodology="Method.",
            results="Results.",
        )

    def fake_analyzer(
        context,
        **kwargs,
    ) -> PaperAnalysisResult:
        return make_analysis()

    paper = make_paper()

    process_paper(
        paper,
        config=make_config(),
        client=object(),
        settings=make_settings(),
        pdf_fetcher=fake_pdf_fetcher,
        section_parser=fake_parser,
        analyzer=fake_analyzer,
    )

    assert captured["url"] == (
        paper.pdf_url
    )

    assert captured["kwargs"] == {
        "timeout_seconds": 90,
        "max_attempts": 3,
        "max_download_mb": 50,
        "max_text_chars": 70000,
    }


def test_no_available_evidence_is_rejected() -> None:
    def failing_pdf_fetcher(
        url: str,
        **kwargs,
    ) -> str:
        raise RuntimeError(
            "download failed"
        )

    with pytest.raises(
        ValueError,
        match=(
            "No analyzable paper evidence"
        ),
    ):
        process_paper(
            make_paper(
                abstract=""
            ),
            config=make_config(),
            client=object(),
            settings=make_settings(),
            pdf_fetcher=(
                failing_pdf_fetcher
            ),
        )