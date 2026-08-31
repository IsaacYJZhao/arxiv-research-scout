from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


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

@dataclass(frozen=True, slots=True)
class PaperProcessingResult:
    """
    Complete in-memory processing result for one paper.

    State is intentionally not updated here.
    A paper should only be marked as processed after
    its final report has been written successfully.
    """

    paper: ArxivPaper
    context: PaperAnalysisContext
    analysis: PaperAnalysisResult
    pdf_error: str | None

@dataclass(frozen=True, slots=True)
class PaperCommitResult:
    """
    Result of one successfully committed paper.

    A commit means:
    1. paper analysis succeeded;
    2. report writing succeeded;
    3. processed state was persisted successfully.
    """

    processing: PaperProcessingResult
    report_path: Path

@dataclass(frozen=True, slots=True)
class PaperProcessingFailure:
    """
    Information about one paper that failed during
    batch processing.
    """

    arxiv_id: str
    title: str
    error: str


@dataclass(frozen=True, slots=True)
class BatchProcessingResult:
    """
    Result of processing one selected paper batch.
    """

    committed: tuple[
        PaperCommitResult,
        ...
    ]

    failures: tuple[
        PaperProcessingFailure,
        ...
    ]

    run_marked_successful: bool