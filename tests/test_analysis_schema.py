import pytest

from arxiv_research_scout.analysis_schema import (
    ANALYSIS_JSON_SCHEMA,
    parse_analysis_result,
)


def valid_result() -> dict:
    return {
        "methodology": (
            "A lightweight 3D CNN is used "
            "for candidate classification."
        ),
        "evaluation": (
            "The model is evaluated on LUNA16."
        ),
        "innovation": (
            "The method reduces computation "
            "while maintaining sensitivity."
        ),
        "datasets": [
            "LUNA16",
        ],
        "metrics": [
            "FROC",
            "CPM",
        ],
        "key_results": [
            "High sensitivity at low FP/scan.",
        ],
        "limitations": (
            "External validation was not reported."
        ),
        "evidence_level": "full_text",
        "confidence": "high",
    }


def test_parse_valid_analysis_result() -> None:
    result = parse_analysis_result(
        valid_result()
    )

    assert result.methodology.startswith(
        "A lightweight"
    )

    assert result.datasets == (
        "LUNA16",
    )

    assert result.metrics == (
        "FROC",
        "CPM",
    )

    assert result.evidence_level == (
        "full_text"
    )

    assert result.confidence == "high"


def test_invalid_evidence_level_is_rejected() -> None:
    data = valid_result()

    data["evidence_level"] = (
        "probably_full_text"
    )

    with pytest.raises(ValueError):
        parse_analysis_result(data)


def test_invalid_confidence_is_rejected() -> None:
    data = valid_result()

    data["confidence"] = "very_high"

    with pytest.raises(ValueError):
        parse_analysis_result(data)


def test_non_string_list_item_is_rejected() -> None:
    data = valid_result()

    data["metrics"] = [
        "FROC",
        123,
    ]

    with pytest.raises(ValueError):
        parse_analysis_result(data)


def test_schema_disallows_extra_properties() -> None:
    assert (
        ANALYSIS_JSON_SCHEMA[
            "additionalProperties"
        ]
        is False
    )