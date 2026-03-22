import io
from dataclasses import dataclass

import qrcode
import qrcode.image.svg

MAX_ARTISTS = 3
MAX_ARTIST_CHARS = 40


@dataclass
class TrackCard:
    title: str
    artist_names: str
    release_year: int
    spotify_url: str

    @property
    def display_artists(self) -> str:
        artists = [a.strip() for a in self.artist_names.split(",")]
        truncated = artists[:MAX_ARTISTS]
        if len(artists) > MAX_ARTISTS:
            truncated.append("...")
        result = ", ".join(truncated)
        if len(result) > MAX_ARTIST_CHARS:
            result = result[: MAX_ARTIST_CHARS - 1] + "\u2026"
        return result

    @property
    def qr_code_svg_bytes(self) -> bytes:
        img = qrcode.make(self.spotify_url, image_factory=qrcode.image.svg.SvgPathImage)
        buf = io.BytesIO()
        img.save(buf)
        return buf.getvalue()
