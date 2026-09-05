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


def describe_output_language(
        output_language: str,
) -> str:
    """
    Convert a language code into an explicit
    natural-language instruction for the LLM.
    """

    normalized = (
        output_language
        .strip()
        .lower()
    )

    if normalized in {
        "zh-cn",
        "zh_hans",
        "zh-hans",
    }:
        return (
            "Simplified Chinese "
            "(简体中文, zh-CN)"
        )

    if normalized in {
        "zh-tw",
        "zh_hant",
        "zh-hant",
    }:
        return (
            "Traditional Chinese "
            "(繁體中文, zh-TW)"
        )

    if normalized in {
        "en",
        "en-us",
        "en-gb",
    }:
        return "English"

    return output_language.strip()

def build_analysis_prompt(
    context: PaperAnalysisContext,
    *,
    output_language: str,
    max_context_chars: int,
) -> tuple[str, str]:
    """
    Build system instructions and the paper-analysis
    input for either OpenAI or DeepSeek.

    The prompt enforces:
    - evidence-grounded analysis;
    - explicit output language;
    - no unsupported experimental claims;
    - provider-independent structured output.
    """

    evidence_level = determine_evidence_level(
        context
    )

    language_instruction = (
        describe_output_language(
            output_language
        )
    )

    system_prompt = f"""
You are a research-paper analysis engine.

Analyze only the paper evidence supplied by the user.

Write all natural-language analysis fields in
{language_instruction}.

This language requirement is mandatory.

The following fields must use
{language_instruction}:
- methodology
- evaluation
- innovation
- key_results
- limitations

Dataset names, model names, architecture names,
metric names, statistical-test names, acronyms,
software names, and other official technical terms
may remain in their original language when
translation would reduce technical precision.

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

1. Use only information explicitly supported by
   the supplied paper evidence.

2. Never invent or assume:
   - datasets;
   - sample sizes;
   - patient counts;
   - scan counts;
   - nodule counts;
   - train/validation/test splits;
   - cross-validation settings;
   - model architectures;
   - preprocessing procedures;
   - augmentation procedures;
   - training strategies;
   - optimizers;
   - learning rates;
   - epoch counts;
   - loss functions;
   - parameter counts;
   - inference times;
   - baselines;
   - ablation studies;
   - evaluation metrics;
   - statistical tests;
   - numerical results;
   - performance improvements;
   - conclusions not supported by the evidence.

3. If a requested detail is not explicitly present
   in the supplied evidence, state clearly that it
   was not reported or could not be determined from
   the available evidence.

4. Do not use outside knowledge about the paper,
   dataset, authors, research field, or related work.

5. Do not infer a numerical result from qualitative
   wording.

6. Do not convert qualitative statements such as
   "improved performance" into invented percentages,
   scores, sensitivities, false-positive rates, or
   other numerical values.

7. Methodology:
   Summarize what the authors actually propose.

   When supported by the evidence, describe:
   - the overall pipeline;
   - major processing stages;
   - architecture or algorithm;
   - model components;
   - preprocessing;
   - training strategy;
   - inference procedure.

   Distinguish clearly between explicitly described
   components and information that is not available.

8. Evaluation:
   Summarize only experimentally supported details.

   When explicitly available, describe:
   - datasets;
   - dataset sizes;
   - experimental design;
   - train/test protocol;
   - baselines;
   - metrics;
   - statistical tests;
   - quantitative results.

   If some of these are absent, say that they were
   not reported in the supplied evidence.

9. Innovation:
   Summarize the technical or methodological
   contribution claimed by the authors.

   Do not exaggerate novelty.

   Do not describe a method as "first", "novel",
   "state-of-the-art", or superior to previous work
   unless this claim is supported by the supplied
   evidence.

10. datasets:
    Include only dataset names explicitly mentioned
    in the supplied evidence.

    Do not infer datasets from the research topic.

11. metrics:
    Include only metrics or statistical measures
    explicitly reported in the supplied evidence.

12. key_results:
    Include only concrete findings supported by the
    supplied evidence.

    Preserve important numerical values when they
    are explicitly stated.

    Do not manufacture missing numbers.

13. limitations:
    Distinguish between:

    A. limitations explicitly stated by the authors;

    and

    B. limitations inferred only because the supplied
       evidence is incomplete.

    Do not present inferred limitations as author-
    stated limitations.

14. evidence_level MUST be exactly:

    {evidence_level}

    Do not change this value.

15. confidence describes confidence in the evidence
    available for producing this analysis, not general
    confidence in the paper itself.

    Use only:
    - high
    - medium
    - low

    Guidance:

    high:
        Detailed methodology and experimental evidence
        directly support most of the analysis.

    medium:
        Useful evidence is available, but important
        methodological or experimental details are
        incomplete.

    low:
        Analysis relies mainly on abstract-level or
        otherwise very limited evidence.

16. Empty or unavailable information must not be
    replaced with plausible-looking guesses.

17. Keep the analysis concise, technical, and useful
    for literature review.

18. Return only content compatible with the required
    structured JSON schema.

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
# Paper Metadata

arXiv ID: {context.record_id}

Title:
{context.title}

Authors:
{authors}

# Available Paper Evidence

{evidence}

# Analysis Task

Using only the evidence above, produce the required
structured analysis.

Pay particular attention to:
- the actual methodology proposed by the authors;
- how the method was evaluated;
- the central technical innovation;
- datasets explicitly used;
- metrics explicitly reported;
- key quantitative or qualitative results;
- limitations supported by the available evidence.

Do not fill missing information using assumptions or
outside knowledge.
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

    status = getattr(
        response,
        "status",
        None,
    )

    if status == "incomplete":
        incomplete_details = getattr(
            response,
            "incomplete_details",
            None,
        )

        raise ValueError(
            "LLM response was incomplete. "
            f"Details: {incomplete_details}"
        )

    if status == "failed":
        error = getattr(
            response,
            "error",
            None,
        )

        raise ValueError(
            "LLM response failed. "
            f"Details: {error}"
        )

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
        reasoning={
            "effort": "none",
        },
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