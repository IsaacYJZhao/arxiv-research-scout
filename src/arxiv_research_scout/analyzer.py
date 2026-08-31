from __future__ import annotations

import json
from typing import Any

from arxiv_research_scout.analysis_schema import (
    ANALYSIS_JSON_SCHEMA,
    parse_analysis_result,
)
from arxiv_research_scout.models import (
    LLMProviderSettings,
    PaperAnalysisContext,
    PaperAnalysisResult,
)


def determine_evidence_level(
    context: PaperAnalysisContext,
) -> str:
    """
    Determine the evidence level locally.

    The LLM is not allowed to decide whether full-text
    evidence exists.
    """

    has_method = bool(
        context.methodology.strip()
    )

    has_evaluation = bool(
        context.experiments.strip()
        or context.results.strip()
    )

    if has_method and has_evaluation:
        return "full_text"

    if context.pdf_text_available:
        return "partial_text"

    return "abstract_only"


def append_section(
    parts: list[str],
    heading: str,
    content: str,
) -> None:
    """
    Append one non-empty evidence section.
    """

    cleaned = content.strip()

    if not cleaned:
        return

    parts.append(
        f"## {heading}\n{cleaned}"
    )


def build_evidence_text(
    context: PaperAnalysisContext,
    *,
    max_chars: int,
) -> str:
    """
    Build a bounded evidence package for LLM analysis.

    Higher-value experimental sections are placed
    before lower-priority discussion material so that
    truncation preserves the most useful evidence.
    """

    if max_chars < 1000:
        raise ValueError(
            "max_chars must be at least 1000."
        )

    parts: list[str] = []

    append_section(
        parts,
        "Abstract",
        context.abstract,
    )

    append_section(
        parts,
        "Methodology",
        context.methodology,
    )

    append_section(
        parts,
        "Experiments / Evaluation",
        context.experiments,
    )

    append_section(
        parts,
        "Results",
        context.results,
    )

    append_section(
        parts,
        "Introduction",
        context.introduction,
    )

    append_section(
        parts,
        "Discussion",
        context.discussion,
    )

    append_section(
        parts,
        "Conclusion",
        context.conclusion,
    )

    evidence = "\n\n".join(parts)

    return evidence[:max_chars]


def build_analysis_prompt(
    context: PaperAnalysisContext,
    *,
    output_language: str,
    max_context_chars: int,
) -> tuple[str, str]:
    """
    Build system instructions and the paper-analysis
    input for either OpenAI or DeepSeek.
    """

    evidence_level = determine_evidence_level(
        context
    )

    system_prompt = f"""
You are a research-paper analysis engine.

Analyze only the evidence supplied by the user.

Return the analysis in {output_language}.

The required output fields are:
- methodology
- evaluation
- innovation
- datasets
- metrics
- key_results
- limitations
- evidence_level
- confidence

Strict evidence rules:

1. Never invent datasets, metrics, sample sizes,
   baselines, hyperparameters, ablation results,
   numerical improvements, or experimental outcomes.

2. If a detail is not explicitly supported by the
   supplied evidence, say that it is not reported in
   the available evidence.

3. Methodology should explain what the authors
   actually propose, including the major pipeline,
   architecture, training strategy, or algorithm when
   those details are available.

4. Evaluation should summarize datasets, experiment
   design, baselines, metrics, and quantitative
   findings only when supported by evidence.

5. Innovation should summarize the authors' claimed
   technical or methodological contribution. Do not
   exaggerate novelty.

6. Limitations should distinguish limitations stated
   by the authors from limitations inferred from
   missing evidence.

7. evidence_level MUST be exactly:
   {evidence_level}

8. confidence means confidence in the evidence
   available for this summary:
   - high: strong direct support from detailed paper
     sections;
   - medium: useful but incomplete paper evidence;
   - low: mostly abstract-level evidence.

Do not include information from outside the supplied
paper evidence.
""".strip()

    evidence = build_evidence_text(
        context,
        max_chars=max_context_chars,
    )

    authors = ", ".join(
        context.authors
    )

    user_prompt = f"""
# Paper metadata

arXiv ID: {context.arxiv_id}
Title: {context.title}
Authors: {authors}

# Available paper evidence

{evidence}
""".strip()

    return (
        system_prompt,
        user_prompt,
    )


def extract_response_json(
    response: Any,
) -> dict[str, Any]:
    """
    Extract JSON text from an OpenAI-compatible
    Responses API response.
    """

    output_text = getattr(
        response,
        "output_text",
        None,
    )

    if not isinstance(
        output_text,
        str,
    ):
        raise ValueError(
            "LLM response does not contain "
            "output_text."
        )

    output_text = output_text.strip()

    if not output_text:
        raise ValueError(
            "LLM returned empty output."
        )

    try:
        data = json.loads(
            output_text
        )
    except json.JSONDecodeError as error:
        raise ValueError(
            "LLM output is not valid JSON."
        ) from error

    if not isinstance(data, dict):
        raise ValueError(
            "LLM JSON output must be "
            "an object."
        )

    return data


def analyze_with_client(
    context: PaperAnalysisContext,
    *,
    client: Any,
    settings: LLMProviderSettings,
    output_language: str,
    max_context_chars: int,
) -> PaperAnalysisResult:
    """
    Analyze one paper using any OpenAI-compatible
    Responses API client.

    This function is shared by OpenAI and DeepSeek.
    """

    system_prompt, user_prompt = (
        build_analysis_prompt(
            context,
            output_language=output_language,
            max_context_chars=max_context_chars,
        )
    )

    response = client.responses.create(
        model=settings.model,
        instructions=system_prompt,
        input=user_prompt,
        max_output_tokens=(
            settings.max_output_tokens
        ),
        text={
            "format": {
                "type": "json_schema",
                "name": "paper_analysis",
                "schema": (
                    ANALYSIS_JSON_SCHEMA
                ),
            }
        },
    )

    data = extract_response_json(
        response
    )

    # Evidence level is determined by local code,
    # not trusted to the model.
    data["evidence_level"] = (
        determine_evidence_level(
            context
        )
    )

    return parse_analysis_result(
        data
    )