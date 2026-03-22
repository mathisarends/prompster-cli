import io
from typing import Self

import qrcode
from pydantic import BaseModel, computed_field


class RawExternalUrls(BaseModel):
    spotify: str


class RawArtist(BaseModel):
    id: str
    name: str
    uri: str


class RawAlbum(BaseModel):
    name: str
    release_date: str


class RawTrack(BaseModel):
    id: str | None = None
    name: str
    artists: list[RawArtist]
    album: RawAlbum
    uri: str
    external_urls: RawExternalUrls
    preview_url: str | None = None
    duration_ms: int


class RawSearchTracksPage(BaseModel):
    items: list[RawTrack]


class RawSearchResponse(BaseModel):
    tracks: RawSearchTracksPage


class RawTracksResponse(BaseModel):
    tracks: list[RawTrack | None]


class RawSearchAlbum(BaseModel):
    id: str | None = None
    name: str
    artists: list[RawArtist]
    release_date: str
    uri: str
    external_urls: RawExternalUrls
    total_tracks: int = 0


class RawSearchAlbumsPage(BaseModel):
    items: list[RawSearchAlbum]


class RawSearchPlaylist(BaseModel):
    id: str | None = None
    name: str
    description: str = ""
    uri: str
    external_urls: RawExternalUrls
    tracks: RawPlaylistTracks | None = None


class RawSearchPlaylistsPage(BaseModel):
    items: list[RawSearchPlaylist | None]


class RawArtistAlbumsPage(BaseModel):
    items: list[RawSearchAlbum]
    next: str | None = None


class RawArtistTopTracksResponse(BaseModel):
    tracks: list[RawTrack]


class RawPlaylistTracks(BaseModel):
    total: int = 0


class RawPlaylist(BaseModel):
    id: str
    name: str
    description: str = ""
    uri: str
    external_urls: RawExternalUrls
    public: bool = False
    tracks: RawPlaylistTracks | None = None


class RawPlaylistItem(BaseModel):
    track: RawTrack | None = None


class RawPlaylistItemsPage(BaseModel):
    items: list[RawPlaylistItem]
    next: str | None = None


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

    @classmethod
    def from_raw(cls, raw: RawTrack) -> Self:
        assert raw.id is not None
        return cls(
            id=raw.id,
            title=raw.name,
            artists=[
                SpotifyArtist(id=a.id, name=a.name, uri=a.uri) for a in raw.artists
            ],
            album=raw.album.name,
            release_year=int(raw.album.release_date.split("-")[0]),
            uri=raw.uri,
            url=raw.external_urls.spotify,
            preview_url=raw.preview_url,
            duration_ms=raw.duration_ms,
        )

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


class SpotifyAlbum(BaseModel):
    id: str
    name: str
    artists: list[SpotifyArtist]
    release_year: int
    uri: str
    url: str
    total_tracks: int = 0

    @classmethod
    def from_raw(cls, raw: RawSearchAlbum) -> Self:
        assert raw.id is not None
        return cls(
            id=raw.id,
            name=raw.name,
            artists=[
                SpotifyArtist(id=a.id, name=a.name, uri=a.uri) for a in raw.artists
            ],
            release_year=int(raw.release_date.split("-")[0]),
            uri=raw.uri,
            url=raw.external_urls.spotify,
            total_tracks=raw.total_tracks,
        )

    @computed_field
    @property
    def artist_names(self) -> str:
        return ", ".join(a.name for a in self.artists)


class SpotifySearchPlaylist(BaseModel):
    id: str
    name: str
    description: str
    uri: str
    url: str
    track_count: int = 0

    @classmethod
    def from_raw(cls, raw: RawSearchPlaylist) -> Self:
        assert raw.id is not None
        return cls(
            id=raw.id,
            name=raw.name,
            description=raw.description,
            uri=raw.uri,
            url=raw.external_urls.spotify,
            track_count=raw.tracks.total if raw.tracks else 0,
        )


class SpotifyPlaylist(BaseModel):
    id: str
    name: str
    description: str
    uri: str
    url: str
    public: bool
    track_count: int = 0

    @classmethod
    def from_raw(cls, raw: RawPlaylist) -> Self:
        return cls(
            id=raw.id,
            name=raw.name,
            description=raw.description,
            uri=raw.uri,
            url=raw.external_urls.spotify,
            public=raw.public,
            track_count=raw.tracks.total if raw.tracks else 0,
        )

    @computed_field
    @property
    def qr_code_png_bytes(self) -> bytes:
        img = qrcode.make(self.url)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
