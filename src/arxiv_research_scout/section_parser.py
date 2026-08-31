from __future__ import annotations

import re

from arxiv_research_scout.models import (
    PaperSections,
)


# --------------------------------------------------
# Canonical section names and common aliases
# --------------------------------------------------

SECTION_ALIASES = {
    "abstract": {
        "abstract",
    },

    "introduction": {
        "introduction",
    },

    "related_work": {
        "related work",
        "related works",
        "background",
        "literature review",
    },

    "methodology": {
        "method",
        "methods",
        "methodology",
        "materials and methods",
        "methods and materials",
        "proposed method",
        "proposed methods",
        "proposed approach",
        "approach",
    },

    "experiments": {
        "experiments",
        "experiment",
        "experimental setup",
        "experimental settings",
        "experiment setup",
        "experiment settings",
        "evaluation",
        "evaluation setup",
        "evaluation protocol",
        "experimental design",
    },

    "results": {
        "results",
        "experimental results",
        "evaluation results",
        "results and analysis",
        "quantitative results",
        "qualitative results",
    },

    "discussion": {
        "discussion",
        "results and discussion",
    },

    "conclusion": {
        "conclusion",
        "conclusions",
        "conclusion and future work",
        "conclusions and future work",
        "conclusion and future works",
        "conclusions and future works",
    },
}


# --------------------------------------------------
# Headings after which useful paper-body parsing
# should stop.
# --------------------------------------------------

STOP_SECTION_ALIASES = {
    "references",
    "reference",
    "bibliography",
}


# --------------------------------------------------
# Section-number prefix
#
# Examples handled:
#
# 1 Introduction
# 1. Introduction
# 2.3 Methodology
# III Methodology
# III. Methodology
# --------------------------------------------------

NUMBER_PREFIX = re.compile(
    r"""
    ^
    \s*
    (?:
        \d+(?:\.\d+)*
        |
        [IVXLC]+
    )
    [.)]?
    \s+
    """,
    flags=re.IGNORECASE | re.VERBOSE,
)


# --------------------------------------------------
# Heading normalization
# --------------------------------------------------

def normalize_heading(
    line: str,
) -> str:
    """
    Normalize a possible academic section heading.

    Examples
    --------
    "1 Introduction"
        -> "introduction"

    "III. Methodology"
        -> "methodology"

    "4.2 Experimental Setup"
        -> "experimental setup"
    """

    normalized = line.strip()

    normalized = NUMBER_PREFIX.sub(
        "",
        normalized,
    )

    normalized = normalized.strip(
        " :.-–—"
    )

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    )

    return normalized.lower()


# --------------------------------------------------
# Section identification
# --------------------------------------------------

def identify_section(
    line: str,
) -> str | None:
    """
    Identify a known academic section heading.

    Returns the canonical section name, such as:

        introduction
        methodology
        experiments
        results
        conclusion

    Returns "stop" for terminal sections such as
    References or Appendix.

    Returns None when the line does not look like a
    known section heading.
    """

    stripped = line.strip()

    if not stripped:
        return None

    # Body-text sentences are usually much longer
    # than section headings. This also helps avoid
    # accidental matches inside paragraphs.
    if len(stripped) > 120:
        return None

    heading = normalize_heading(
        stripped
    )

    if heading in STOP_SECTION_ALIASES:
        return "stop"

    for section_name, aliases in (
        SECTION_ALIASES.items()
    ):
        if heading in aliases:
            return section_name

    return None


# --------------------------------------------------
# Inline Abstract support
# --------------------------------------------------

def extract_inline_abstract(
    line: str,
) -> str | None:
    """
    Extract abstract text when the heading and body
    occur on the same line.

    Examples
    --------
    Abstract—We propose a lightweight method.

    Abstract: We propose a lightweight method.

    ABSTRACT - We propose a lightweight method.
    """

    match = re.match(
        r"""
        ^\s*
        abstract
        \s*
        [:\-–—.]
        \s*
        (.+)
        $
        """,
        line,
        flags=re.IGNORECASE | re.VERBOSE,
    )

    if match is None:
        return None

    abstract_text = match.group(1).strip()

    if not abstract_text:
        return None

    return abstract_text


# --------------------------------------------------
# Section-text cleanup
# --------------------------------------------------

def clean_section_text(
    lines: list[str],
) -> str:
    """
    Clean text collected for one section.

    Repeated empty lines are collapsed while normal
    paragraph boundaries are retained.
    """

    cleaned_lines: list[str] = []

    previous_blank = False

    for raw_line in lines:
        line = raw_line.strip()

        is_blank = not line

        if is_blank:
            if (
                cleaned_lines
                and not previous_blank
            ):
                cleaned_lines.append("")

            previous_blank = True
            continue

        cleaned_lines.append(line)
        previous_blank = False

    return "\n".join(
        cleaned_lines
    ).strip()


# --------------------------------------------------
# Main parser
# --------------------------------------------------

def parse_sections(
    text: str,
) -> PaperSections:
    """
    Recover common academic-paper sections from
    text extracted from a PDF.

    PDF text normally does not retain reliable
    document structure, so this parser is deliberately
    heuristic.

    Recognized major sections include:

        Abstract
        Introduction
        Related Work
        Methodology
        Experiments / Evaluation
        Results
        Discussion
        Conclusion

    Parsing stops when terminal content such as
    References, Bibliography, Appendix, or
    Acknowledgments is encountered.
    """

    collected: dict[str, list[str]] = {
        section_name: []
        for section_name
        in SECTION_ALIASES
    }

    current_section: str | None = None
    has_started_body = False

    for raw_line in text.splitlines():

        # ------------------------------------------
        # Case 1:
        # Abstract and its body are on one line.
        #
        # Example:
        # Abstract—We propose ...
        # ------------------------------------------

        inline_abstract = (
            extract_inline_abstract(
                raw_line
            )
        )

        if inline_abstract is not None:
            current_section = "abstract"
            has_started_body = True

            collected[
                "abstract"
            ].append(
                inline_abstract
            )

            continue

        # ------------------------------------------
        # Case 2:
        # Normal standalone heading.
        # ------------------------------------------

        detected = identify_section(
            raw_line
        )

        # References / Appendix / etc.
        #
        # Once these sections are reached, the
        # remaining document usually does not
        # contain useful core-paper content.
        if detected == "stop":
            if has_started_body:
                break

            continue

        if detected is not None:
            current_section = detected

            if detected in {
                "abstract",
                "introduction",
                "related_work",
                "methodology",
                "experiments",
                "results",
                "discussion",
                "conclusion",
            }:
                has_started_body = True

            continue

        # ------------------------------------------
        # Ignore text before the first recognized
        # section.
        # ------------------------------------------

        if current_section is None:
            continue

        # ------------------------------------------
        # Normal body text belonging to the current
        # section.
        # ------------------------------------------

        collected[
            current_section
        ].append(
            raw_line
        )

    # --------------------------------------------------
    # Final cleanup
    # --------------------------------------------------

    cleaned = {
        section_name: clean_section_text(
            lines
        )
        for section_name, lines
        in collected.items()
    }

    return PaperSections(
        abstract=cleaned[
            "abstract"
        ],

        introduction=cleaned[
            "introduction"
        ],

        related_work=cleaned[
            "related_work"
        ],

        methodology=cleaned[
            "methodology"
        ],

        experiments=cleaned[
            "experiments"
        ],

        results=cleaned[
            "results"
        ],

        discussion=cleaned[
            "discussion"
        ],

        conclusion=cleaned[
            "conclusion"
        ],
    )