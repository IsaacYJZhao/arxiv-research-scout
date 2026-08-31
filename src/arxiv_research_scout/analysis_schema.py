from __future__ import annotations

from typing import Any

from arxiv_research_scout.models import (
    PaperAnalysisResult,
)


VALID_EVIDENCE_LEVELS = {
    "full_text",
    "partial_text",
    "abstract_only",
}

VALID_CONFIDENCE_LEVELS = {
    "high",
    "medium",
    "low",
}


ANALYSIS_JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "methodology": {
            "type": "string",
        },
        "evaluation": {
            "type": "string",
        },
        "innovation": {
            "type": "string",
        },
        "datasets": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "metrics": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "key_results": {
            "type": "array",
            "items": {
                "type": "string",
            },
        },
        "limitations": {
            "type": "string",
        },
        "evidence_level": {
            "type": "string",
            "enum": [
                "full_text",
                "partial_text",
                "abstract_only",
            ],
        },
        "confidence": {
            "type": "string",
            "enum": [
                "high",
                "medium",
                "low",
            ],
        },
    },
    "required": [
        "methodology",
        "evaluation",
        "innovation",
        "datasets",
        "metrics",
        "key_results",
        "limitations",
        "evidence_level",
        "confidence",
    ],
    "additionalProperties": False,
}


def require_string(
    data: dict[str, Any],
    field: str,
) -> str:
    """
    Read and validate one required string field.
    """

    value = data.get(field)

    if not isinstance(value, str):
        raise ValueError(
            f"{field} must be a string."
        )

    return value.strip()


def require_string_list(
    data: dict[str, Any],
    field: str,
) -> tuple[str, ...]:
    """
    Read and validate one required list of strings.
    """

    value = data.get(field)

    if not isinstance(value, list):
        raise ValueError(
            f"{field} must be a list."
        )

    if not all(
        isinstance(item, str)
        for item in value
    ):
        raise ValueError(
            f"{field} must contain "
            "only strings."
        )

    return tuple(
        item.strip()
        for item in value
        if item.strip()
    )


def parse_analysis_result(
    data: dict[str, Any],
) -> PaperAnalysisResult:
    """
    Convert provider JSON output into the common
    PaperAnalysisResult model.

    This validation is provider-independent.
    """

    if not isinstance(data, dict):
        raise ValueError(
            "Analysis result must be "
            "a JSON object."
        )

    methodology = require_string(
        data,
        "methodology",
    )

    evaluation = require_string(
        data,
        "evaluation",
    )

    innovation = require_string(
        data,
        "innovation",
    )

    datasets = require_string_list(
        data,
        "datasets",
    )

    metrics = require_string_list(
        data,
        "metrics",
    )

    key_results = require_string_list(
        data,
        "key_results",
    )

    limitations = require_string(
        data,
        "limitations",
    )

    evidence_level = require_string(
        data,
        "evidence_level",
    )

    confidence = require_string(
        data,
        "confidence",
    )

    if (
        evidence_level
        not in VALID_EVIDENCE_LEVELS
    ):
        raise ValueError(
            "Invalid evidence_level."
        )

    if (
        confidence
        not in VALID_CONFIDENCE_LEVELS
    ):
        raise ValueError(
            "Invalid confidence."
        )

    return PaperAnalysisResult(
        methodology=methodology,
        evaluation=evaluation,
        innovation=innovation,
        datasets=datasets,
        metrics=metrics,
        key_results=key_results,
        limitations=limitations,
        evidence_level=evidence_level,
        confidence=confidence,
    )