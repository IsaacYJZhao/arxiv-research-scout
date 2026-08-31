import json
from types import SimpleNamespace

import pytest

from arxiv_research_scout.analyzer import (
    analyze_with_client,
    build_analysis_prompt,
    build_evidence_text,
    determine_evidence_level,
    extract_response_json,
)

from arxiv_research_scout.models import (
    LLMProviderSettings,
    PaperAnalysisContext,
)


def make_context(
    *,
    methodology: str = "Method evidence.",
    experiments: str = "Experiment evidence.",
    results: str = "Result evidence.",
    pdf_text_available: bool = True,
) -> PaperAnalysisContext:
    return PaperAnalysisContext(
        arxiv_id="2608.10000v1",
        title="Example Lung Nodule Paper",
        authors=("Alice Example",),
        abstract="Official abstract.",
        introduction="Introduction evidence.",
        methodology=methodology,
        experiments=experiments,
        results=results,
        discussion="Discussion evidence.",
        conclusion="Conclusion evidence.",
        pdf_text_available=pdf_text_available,
    )


def make_settings() -> LLMProviderSettings:
    return LLMProviderSettings(
        provider="openai",
        model="test-model",
        api_key_env="OPENAI_API_KEY",
        base_url=None,
        max_output_tokens=2500,
    )


def valid_json_result() -> dict:
    return {
        "methodology": "Method summary.",
        "evaluation": "Evaluation summary.",
        "innovation": "Innovation summary.",
        "datasets": ["LUNA16"],
        "metrics": ["FROC"],
        "key_results": [
            "Reported result."
        ],
        "limitations": (
            "External validation not reported."
        ),
        "evidence_level": "full_text",
        "confidence": "high",
    }


def test_full_text_evidence_level() -> None:
    context = make_context()

    assert determine_evidence_level(
        context
    ) == "full_text"


def test_partial_text_evidence_level() -> None:
    context = make_context(
        methodology="",
        experiments="",
        results="",
        pdf_text_available=True,
    )

    assert determine_evidence_level(
        context
    ) == "partial_text"


def test_abstract_only_evidence_level() -> None:
    context = make_context(
        methodology="",
        experiments="",
        results="",
        pdf_text_available=False,
    )

    assert determine_evidence_level(
        context
    ) == "abstract_only"


def test_evidence_text_respects_limit() -> None:
    context = make_context()

    evidence = build_evidence_text(
        context,
        max_chars=1000,
    )

    assert len(evidence) <= 1000

    assert "Official abstract." in (
        evidence
    )


def test_prompt_contains_evidence_rules() -> None:
    context = make_context()

    system_prompt, user_prompt = (
        build_analysis_prompt(
            context,
            output_language="zh-CN",
            max_context_chars=5000,
        )
    )

    assert "Never invent datasets" in (
        system_prompt
    )

    assert (
        "evidence_level MUST be exactly"
        in system_prompt
    )

    assert context.title in user_prompt
    assert context.abstract in user_prompt


def test_extract_response_json() -> None:
    response = SimpleNamespace(
        output_text=json.dumps(
            valid_json_result()
        )
    )

    result = extract_response_json(
        response
    )

    assert result["datasets"] == [
        "LUNA16"
    ]


def test_invalid_json_is_rejected() -> None:
    response = SimpleNamespace(
        output_text="not-json"
    )

    with pytest.raises(ValueError):
        extract_response_json(
            response
        )


def test_analyze_with_client_uses_common_schema() -> None:
    calls = []

    class FakeResponses:
        def create(
            self,
            **kwargs,
        ):
            calls.append(kwargs)

            data = valid_json_result()

            # Deliberately return the wrong value.
            # Local code must overwrite it.
            data["evidence_level"] = (
                "abstract_only"
            )

            return SimpleNamespace(
                output_text=json.dumps(
                    data
                )
            )

    fake_client = SimpleNamespace(
        responses=FakeResponses()
    )

    context = make_context()

    result = analyze_with_client(
        context,
        client=fake_client,
        settings=make_settings(),
        output_language="zh-CN",
        max_context_chars=5000,
    )

    assert result.methodology == (
        "Method summary."
    )

    assert result.evidence_level == (
        "full_text"
    )

    assert len(calls) == 1

    request = calls[0]

    assert request["model"] == (
        "test-model"
    )

    assert request[
        "max_output_tokens"
    ] == 2500

    assert (
        request["text"]["format"]["type"]
        ==
        "json_schema"
    )

    assert (
        request["text"]["format"]["name"]
        ==
        "paper_analysis"
    )