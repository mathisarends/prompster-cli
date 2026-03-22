import asyncio
import tempfile
from pathlib import Path

import typst

from prompster.export.layout import merge_card_pdfs
from prompster.spotify.schemas import SpotifyTrack

_TEMPLATES = Path(__file__).parent / "templates"
_FRONT_TEMPLATE = _TEMPLATES / "card_front.typ"
_BACK_TEMPLATE = _TEMPLATES / "card_back.typ"


def _compile_card(
    template: Path,
    inputs: dict[str, str],
    output: Path,
) -> None:
    typst.compile(
        str(template),
        output=str(output),
        inputs=inputs,
    )


async def render_deck(tracks: list[SpotifyTrack], output: Path) -> Path:
    """
    Render a Hitster deck PDF from a list of SpotifyTrack objects.

    Each track produces two pages (front QR, back year+title+artist).
    Returns the path to the merged output PDF.
    """
    output.parent.mkdir(parents=True, exist_ok=True)

    loop = asyncio.get_event_loop()
    card_pdfs: list[tuple[Path, Path]] = []

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        for i, track in enumerate(tracks):
            idx = str(i + 1)

            # Write QR code PNG
            qr_path = tmp_path / f"qr_{i}.png"
            qr_path.write_bytes(track.qr_code_png_bytes)

            front_pdf = tmp_path / f"front_{i}.pdf"
            back_pdf = tmp_path / f"back_{i}.pdf"

            await loop.run_in_executor(
                None,
                _compile_card,
                _FRONT_TEMPLATE,
                {"qr_path": str(qr_path), "card_index": idx},
                front_pdf,
            )
            await loop.run_in_executor(
                None,
                _compile_card,
                _BACK_TEMPLATE,
                {
                    "year": str(track.release_year),
                    "title": track.title,
                    "artist": track.artist_names,
                    "card_index": idx,
                },
                back_pdf,
            )

            card_pdfs.append((front_pdf, back_pdf))

        await loop.run_in_executor(None, merge_card_pdfs, card_pdfs, output)

    return output
