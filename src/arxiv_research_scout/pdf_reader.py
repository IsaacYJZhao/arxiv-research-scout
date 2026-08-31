from __future__ import annotations

import io
import time

import requests
from pypdf import PdfReader


PDF_USER_AGENT = (
    "arxiv-research-scout/0.1 "
    "(academic literature monitoring tool)"
)

RETRYABLE_STATUS_CODES = {
    429,
    500,
    502,
    503,
    504,
}


def clean_pdf_text(
    text: str,
) -> str:
    """
    Normalize text extracted from a PDF.

    Excess blank lines and trailing whitespace
    are removed while paragraph boundaries
    are preserved.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
    ]

    cleaned_lines: list[str] = []
    previous_blank = False

    for line in lines:
        is_blank = not line

        if is_blank:
            if not previous_blank:
                cleaned_lines.append("")

            previous_blank = True
            continue

        cleaned_lines.append(line)
        previous_blank = False

    return "\n".join(
        cleaned_lines
    ).strip()


def extract_text_from_pdf_bytes(
    pdf_bytes: bytes,
    *,
    max_chars: int | None = None,
) -> str:
    """
    Extract text from PDF bytes entirely in memory.

    No PDF file is written into the repository.
    """

    reader = PdfReader(
        io.BytesIO(pdf_bytes)
    )

    pages: list[str] = []

    for page in reader.pages:
        text = page.extract_text() or ""

        if text:
            pages.append(text)

    combined = clean_pdf_text(
        "\n\n".join(pages)
    )

    if (
        max_chars is not None
        and len(combined) > max_chars
    ):
        return combined[:max_chars]

    return combined


def download_pdf(
    pdf_url: str,
    *,
    timeout_seconds: int = 90,
    max_attempts: int = 3,
    max_download_mb: int = 50,
) -> bytes:
    """
    Download a PDF into memory.

    Temporary network failures and rate limiting
    are retried with exponential backoff.
    """

    if max_attempts < 1:
        raise ValueError(
            "max_attempts must be at least 1."
        )

    if max_download_mb < 1:
        raise ValueError(
            "max_download_mb must be at least 1."
        )

    max_bytes = (
        max_download_mb
        * 1024
        * 1024
    )

    headers = {
        "User-Agent": PDF_USER_AGENT,
    }

    for attempt in range(
        1,
        max_attempts + 1,
    ):
        try:
            response = requests.get(
                pdf_url,
                headers=headers,
                timeout=timeout_seconds,
            )

        except (
            requests.exceptions.ReadTimeout,
            requests.exceptions.ConnectionError,
        ):
            if attempt >= max_attempts:
                raise

            delay = 10 * (
                2 ** (attempt - 1)
            )

            print(
                f"PDF download failed. "
                f"Retrying in {delay}s "
                f"[{attempt}/{max_attempts}]..."
            )

            time.sleep(delay)
            continue

        if (
            response.status_code
            in RETRYABLE_STATUS_CODES
        ):
            if attempt >= max_attempts:
                response.raise_for_status()

            retry_after = (
                response.headers.get(
                    "Retry-After"
                )
            )

            try:
                delay = (
                    float(retry_after)
                    if retry_after
                    else 10 * (
                        2 ** (attempt - 1)
                    )
                )
            except ValueError:
                delay = 10 * (
                    2 ** (attempt - 1)
                )

            print(
                f"PDF server returned HTTP "
                f"{response.status_code}. "
                f"Retrying in {delay:.0f}s "
                f"[{attempt}/{max_attempts}]..."
            )

            time.sleep(delay)
            continue

        response.raise_for_status()

        pdf_bytes = response.content

        if len(pdf_bytes) > max_bytes:
            raise ValueError(
                "PDF exceeds configured "
                f"{max_download_mb} MB limit."
            )

        return pdf_bytes

    raise RuntimeError(
        "PDF download failed unexpectedly."
    )


def fetch_pdf_text(
    pdf_url: str,
    *,
    timeout_seconds: int = 90,
    max_attempts: int = 3,
    max_download_mb: int = 50,
    max_text_chars: int = 70000,
) -> str:
    """
    Download an arXiv PDF and extract its text.
    """

    pdf_bytes = download_pdf(
        pdf_url,
        timeout_seconds=timeout_seconds,
        max_attempts=max_attempts,
        max_download_mb=max_download_mb,
    )

    return extract_text_from_pdf_bytes(
        pdf_bytes,
        max_chars=max_text_chars,
    )