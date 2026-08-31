from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ArxivPaper:
    """
    Standard representation of one paper returned by arXiv.
    """

    arxiv_id: str
    title: str
    authors: tuple[str, ...]
    abstract: str
    published: str
    updated: str
    categories: tuple[str, ...]
    abs_url: str
    pdf_url: str

@dataclass(frozen=True, slots=True)
class RelevanceAssessment:
    """
    Deterministic relevance assessment for one paper.
    """

    score: int
    level: str

    matched_core_terms: tuple[str, ...]
    matched_target_terms: tuple[str, ...]
    matched_supporting_terms: tuple[str, ...]
    matched_deprioritize_terms: tuple[str, ...]

@dataclass(frozen=True, slots=True)
class PaperSections:
    """
    Structured sections recovered from paper text.
    """

    abstract: str = ""
    introduction: str = ""
    related_work: str = ""
    methodology: str = ""
    experiments: str = ""
    results: str = ""
    discussion: str = ""
    conclusion: str = ""

@dataclass(frozen=True, slots=True)
class PaperAnalysisContext:
    """
    Structured evidence prepared for LLM analysis.

    The abstract comes primarily from arXiv metadata,
    while detailed sections come from the PDF.
    """

    arxiv_id: str
    title: str
    authors: tuple[str, ...]

    abstract: str

    introduction: str
    methodology: str
    experiments: str
    results: str
    discussion: str
    conclusion: str

    pdf_text_available: bool

@dataclass(frozen=True, slots=True)
class PaperAnalysisContext:
    """
    Structured evidence prepared for LLM analysis.

    The abstract primarily comes from arXiv metadata.
    Detailed evidence comes from parsed PDF sections.
    """

    arxiv_id: str
    title: str
    authors: tuple[str, ...]

    abstract: str

    introduction: str
    methodology: str
    experiments: str
    results: str
    discussion: str
    conclusion: str

    pdf_text_available: bool

@dataclass(frozen=True, slots=True)
class PaperAnalysisResult:
    """
    Provider-independent structured analysis
    of one research paper.

    Both OpenAI and DeepSeek analyzers must
    produce this same structure.
    """

    methodology: str
    evaluation: str
    innovation: str

    datasets: tuple[str, ...]
    metrics: tuple[str, ...]
    key_results: tuple[str, ...]

    limitations: str

    evidence_level: str
    confidence: str

@dataclass(frozen=True, slots=True)
class LLMProviderSettings:
    """
    Runtime settings for one LLM provider.
    """

    provider: str
    model: str
    api_key_env: str
    base_url: str | None
    max_output_tokens: int