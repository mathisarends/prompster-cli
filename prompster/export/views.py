import io
from dataclasses import dataclass

import qrcode
import qrcode.image.svg


@dataclass
class TrackCard:
    title: str
    artist_names: str
    release_year: int
    spotify_url: str

    @property
    def qr_code_svg_bytes(self) -> bytes:
        img = qrcode.make(self.spotify_url, image_factory=qrcode.image.svg.SvgPathImage)
        buf = io.BytesIO()
        img.save(buf)
        return buf.getvalue()
