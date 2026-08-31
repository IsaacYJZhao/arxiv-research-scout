from arxiv_research_scout.section_parser import (
    identify_section,
    extract_inline_abstract,
    normalize_heading,
    parse_sections,
)


def test_normalize_heading() -> None:
    assert normalize_heading(
        "1 Introduction"
    ) == "introduction"

    assert normalize_heading(
        "III. Methodology"
    ) == "methodology"

    assert normalize_heading(
        "4.2 Experimental Setup"
    ) == "experimental setup"


def test_identify_section() -> None:
    assert identify_section(
        "1 Introduction"
    ) == "introduction"

    assert identify_section(
        "3 Proposed Method"
    ) == "methodology"

    assert identify_section(
        "5 Results"
    ) == "results"


def test_body_text_is_not_heading() -> None:
    line = (
        "The proposed method improves "
        "lung nodule detection using "
        "multi-scale contextual features."
    )

    assert identify_section(
        line
    ) is None


def test_parse_sections() -> None:
    text = """
Abstract
We propose a lightweight detector.

1 Introduction
Lung nodule detection is important.

2 Related Work
Previous methods use 3D CNNs.

3 Methodology
Our model uses three branches.

4 Experimental Setup
We evaluate the model on LUNA16.

5 Results
The model achieves strong FROC performance.

6 Conclusion
The proposed model is lightweight.
"""

    sections = parse_sections(text)

    assert sections.abstract == (
        "We propose a lightweight detector."
    )

    assert sections.introduction == (
        "Lung nodule detection is important."
    )

    assert sections.related_work == (
        "Previous methods use 3D CNNs."
    )

    assert sections.methodology == (
        "Our model uses three branches."
    )

    assert sections.experiments == (
        "We evaluate the model on LUNA16."
    )

    assert sections.results == (
        "The model achieves strong "
        "FROC performance."
    )

    assert sections.conclusion == (
        "The proposed model is lightweight."
    )


def test_missing_sections_remain_empty() -> None:
    text = """
1 Introduction
Example introduction.

2 Conclusion
Example conclusion.
"""

    sections = parse_sections(text)

    assert sections.introduction
    assert sections.conclusion

    assert sections.methodology == ""
    assert sections.experiments == ""
    assert sections.results == ""

def test_extract_inline_abstract() -> None:
    line = (
        "Abstract—We propose a lightweight "
        "lung nodule detection method."
    )

    result = extract_inline_abstract(line)

    assert result == (
        "We propose a lightweight "
        "lung nodule detection method."
    )

def test_references_stop_conclusion() -> None:
    text = """
6 Conclusion
Our method improves detection performance.

References
[1] Example reference.
[2] Another reference.
"""

    sections = parse_sections(text)

    assert sections.conclusion == (
        "Our method improves detection performance."
    )

    assert "Example reference" not in (
        sections.conclusion
    )


def test_inline_abstract_is_parsed() -> None:
    text = """
Abstract—We propose a 3D detection network.

1 Introduction
Example introduction.
"""

    sections = parse_sections(text)

    assert sections.abstract == (
        "We propose a 3D detection network."
    )

def test_front_matter_does_not_stop_parsing() -> None:
    text = """
Acknowledgments
We thank the clinical collaborators.

Guarantor statement
Example statement.

1 Introduction
Lung nodule detection is important.

2 Methods
We propose a lightweight model.

3 Results
The model achieves strong performance.

4 Conclusion
The method is effective.

References
[1] Example reference.
"""

    sections = parse_sections(text)

    assert sections.introduction == (
        "Lung nodule detection is important."
    )

    assert sections.methodology == (
        "We propose a lightweight model."
    )

    assert sections.results == (
        "The model achieves strong performance."
    )

    assert sections.conclusion == (
        "The method is effective."
    )

    assert "Example reference" not in (
        sections.conclusion
    )