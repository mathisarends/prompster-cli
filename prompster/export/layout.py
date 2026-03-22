"""
Page layout helpers.

Each Hitster card produces two PDF pages (front + back).
This module provides utilities for composing those pages into a
single multi-page PDF in print-ready order.
"""

from pathlib import Path

import pypdf


def merge_card_pdfs(card_pdfs: list[tuple[Path, Path]], output: Path) -> None:
    """
    Merge (front, back) PDF pairs into a single PDF.

    Pages are interleaved: front_1, back_1, front_2, back_2, …
    This matches standard duplex / print-at-home order for Hitster decks.
    """
    writer = pypdf.PdfWriter()
    for front, back in card_pdfs:
        for pdf_path in (front, back):
            reader = pypdf.PdfReader(str(pdf_path))
            for page in reader.pages:
                writer.add_page(page)
    with output.open("wb") as f:
        writer.write(f)
