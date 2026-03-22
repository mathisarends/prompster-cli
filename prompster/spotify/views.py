import io

import qrcode
from pydantic import BaseModel, computed_field, model_validator


class SpotifyArtist(BaseModel):
    id: str
    name: str
    uri: str


class SpotifyTrack(BaseModel):
    id: str
    title: str
    artists: list[SpotifyArtist]
    album: str
    release_year: int
    uri: str
    url: str
    preview_url: str | None = None
    duration_ms: int

    @model_validator(mode="before")
    @classmethod
    def _from_raw(cls, data: dict) -> dict:
        if "external_urls" not in data:
            return data
        return {
            "id": data["id"],
            "title": data["name"],
            "artists": data["artists"],
            "album": data["album"]["name"],
            "release_year": int(data["album"]["release_date"].split("-")[0]),
            "uri": data["uri"],
            "url": data["external_urls"]["spotify"],
            "preview_url": data.get("preview_url"),
            "duration_ms": data["duration_ms"],
        }

    @computed_field
    @property
    def artist_names(self) -> str:
        return ", ".join(a.name for a in self.artists)

    @computed_field
    @property
    def qr_code_png_bytes(self) -> bytes:
        img = qrcode.make(self.url)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()


class SpotifyPlaylist(BaseModel):
    id: str
    name: str
    description: str
    uri: str
    url: str
    public: bool
    track_count: int = 0

    @model_validator(mode="before")
    @classmethod
    def _from_raw(cls, data: dict) -> dict:
        if "external_urls" not in data:
            return data
        tracks = data.get("tracks", {})
        return {
            "id": data["id"],
            "name": data["name"],
            "description": data.get("description", ""),
            "uri": data["uri"],
            "url": data["external_urls"]["spotify"],
            "public": data.get("public", False),
            "track_count": tracks.get("total", 0) if isinstance(tracks, dict) else 0,
        }

    @computed_field
    @property
    def qr_code_png_bytes(self) -> bytes:
        img = qrcode.make(self.url)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()


class HitsterCard(BaseModel):
    track: SpotifyTrack

    @computed_field
    @property
    def title(self) -> str:
        return self.track.title

    @computed_field
    @property
    def artist(self) -> str:
        return self.track.artist_names

    @computed_field
    @property
    def year(self) -> int:
        return self.track.release_year

    @computed_field
    @property
    def spotify_url(self) -> str:
        return self.track.url

    @computed_field
    @property
    def qr_code_png_bytes(self) -> bytes:
        return self.track.qr_code_png_bytes
