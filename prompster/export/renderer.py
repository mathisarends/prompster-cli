import asyncio
import json
import shutil
import tempfile
from pathlib import Path

import typst

from prompster.export.views import TrackCard


class DeckRenderer:
    _DECK_TEMPLATE = Path(__file__).parent / "templates" / "deck.typ"

    async def render(self, tracks: list[TrackCard], output: Path) -> Path:
        output.parent.mkdir(parents=True, exist_ok=True)
        loop = asyncio.get_event_loop()

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)

            songs_data = []
            for i, track in enumerate(tracks):
                qr_file = f"qr_{i}.svg"
                (tmp_path / qr_file).write_bytes(track.qr_code_svg_bytes)
                songs_data.append(
                    {
                        "title": track.title,
                        "artist_names": track.artist_names,
                        "release_year": track.release_year,
                        "qr_file": qr_file,
                    }
                )

            (tmp_path / "songs.json").write_text(
                json.dumps(songs_data, ensure_ascii=False), encoding="utf-8"
            )

            deck_typ = tmp_path / "deck.typ"
            shutil.copy(self._DECK_TEMPLATE, deck_typ)

            await loop.run_in_executor(
                None,
                lambda: typst.compile(str(deck_typ), output=str(output)),
            )

        return output
