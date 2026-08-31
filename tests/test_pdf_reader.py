import io

from pypdf import PdfWriter

from arxiv_research_scout.pdf_reader import (
    clean_pdf_text,
    extract_text_from_pdf_bytes,
)


def test_clean_pdf_text() -> None:
    raw = (
        "Introduction   \n"
        "\n"
        "\n"
        "Methodology\n"
        "Results   \n"
    )

    cleaned = clean_pdf_text(raw)

    assert cleaned == (
        "Introduction\n"
        "\n"
        "Methodology\n"
        "Results"
    )


def test_extract_text_from_valid_pdf_bytes() -> None:
    writer = PdfWriter()

    writer.add_blank_page(
        width=612,
        height=792,
    )

    buffer = io.BytesIO()

    writer.write(buffer)

    pdf_bytes = buffer.getvalue()

    text = extract_text_from_pdf_bytes(
        pdf_bytes
    )

    assert isinstance(text, str)


def test_extract_text_respects_character_limit() -> None:
    text = (
        "a" * 100
    )

    from arxiv_research_scout import (
        pdf_reader,
    )

    original_clean = (
        pdf_reader.clean_pdf_text
    )

    try:
        pdf_reader.clean_pdf_text = (
            lambda value: text
        )

        writer = PdfWriter()

        writer.add_blank_page(
            width=612,
            height=792,
        )

        buffer = io.BytesIO()
        writer.write(buffer)

        result = (
            pdf_reader
            .extract_text_from_pdf_bytes(
                buffer.getvalue(),
                max_chars=20,
            )
        )

        assert len(result) == 20

    finally:
        pdf_reader.clean_pdf_text = (
            original_clean
        )