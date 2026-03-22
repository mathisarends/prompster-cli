import asyncio
from collections.abc import Sequence
from typing import Self

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from prompster.spotify.credentials import SPOTIFY_SCOPES, SpotifyCredentials
from prompster.spotify.schemas import (
    RawArtistAlbumsPage,
    RawArtistTopTracksResponse,
    RawPlaylist,
    RawPlaylistItemsPage,
    RawSearchAlbumsPage,
    RawSearchPlaylistsPage,
    RawSearchResponse,
    RawTrack,
    RawTracksResponse,
    SpotifyAlbum,
    SpotifyPlaylist,
    SpotifySearchPlaylist,
    SpotifyTrack,
)


class SpotifyClient:
    def __init__(
        self, credentials: SpotifyCredentials, cache_path: str = ".spotify_cache"
    ) -> None:
        auth = SpotifyOAuth(
            client_id=credentials.spotify_client_id,
            client_secret=credentials.spotify_client_secret,
            redirect_uri=credentials.spotify_redirect_uri,
            scope=SPOTIFY_SCOPES,
            cache_path=cache_path,
        )
        self._sp = spotipy.Spotify(auth_manager=auth)
        self._user_id: str | None = None

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *_) -> None:
        pass

    async def _get_user_id(self) -> str:
        if self._user_id is None:
            raw = await self._run(self._sp.me)
            self._user_id = raw["id"]
        return self._user_id

    async def search_tracks(
        self, query: str, limit: int = 10, market: str | None = None
    ) -> list[SpotifyTrack]:
        raw = await self._run(
            self._sp.search, q=query, type="track", limit=limit, market=market
        )
        response = RawSearchResponse.model_validate(raw)
        return [SpotifyTrack.from_raw(t) for t in response.tracks.items if t.id]

    async def get_track(self, track_id: str, market: str | None = None) -> SpotifyTrack:
        raw = await self._run(self._sp.track, track_id, market=market)
        return SpotifyTrack.from_raw(RawTrack.model_validate(raw))

    async def get_tracks(
        self, track_ids: Sequence[str], market: str | None = None
    ) -> list[SpotifyTrack]:
        raw = await self._run(self._sp.tracks, list(track_ids), market=market)
        response = RawTracksResponse.model_validate(raw)
        return [SpotifyTrack.from_raw(t) for t in response.tracks if t and t.id]

    async def search_albums(
        self, query: str, limit: int = 10, market: str | None = None
    ) -> list[SpotifyAlbum]:
        raw = await self._run(
            self._sp.search, q=query, type="album", limit=limit, market=market
        )
        page = RawSearchAlbumsPage.model_validate(raw.get("albums", {"items": []}))
        return [SpotifyAlbum.from_raw(a) for a in page.items if a.id]

    async def search_playlists(
        self, query: str, limit: int = 10, market: str | None = None
    ) -> list[SpotifySearchPlaylist]:
        raw = await self._run(
            self._sp.search, q=query, type="playlist", limit=limit, market=market
        )
        page = RawSearchPlaylistsPage.model_validate(
            raw.get("playlists", {"items": []})
        )
        return [SpotifySearchPlaylist.from_raw(p) for p in page.items if p and p.id]

    async def get_artist_albums(
        self, artist_id: str, include_groups: str = "album,single", limit: int = 20
    ) -> list[SpotifyAlbum]:
        raw = await self._run(
            self._sp.artist_albums,
            artist_id,
            include_groups=include_groups,
            limit=limit,
        )
        page = RawArtistAlbumsPage.model_validate(raw)
        return [SpotifyAlbum.from_raw(a) for a in page.items if a.id]

    async def get_artist_top_tracks(
        self, artist_id: str, country: str = "DE"
    ) -> list[SpotifyTrack]:
        raw = await self._run(self._sp.artist_top_tracks, artist_id, country=country)
        response = RawArtistTopTracksResponse.model_validate(raw)
        return [SpotifyTrack.from_raw(t) for t in response.tracks if t.id]

    async def get_album_tracks(
        self, album_id: str, market: str | None = None
    ) -> list[SpotifyTrack]:
        raw = await self._run(self._sp.album_tracks, album_id, market=market)
        tracks = []
        for item in raw.get("items", []):
            # album_tracks returns simplified tracks without album info, so fetch full tracks
            if item.get("id"):
                tracks.append(item["id"])
        if not tracks:
            return []
        return await self.get_tracks(tracks, market=market)

    async def create_playlist(
        self, name: str, description: str = "", public: bool = False
    ) -> SpotifyPlaylist:
        user_id = await self._get_user_id()
        raw = await self._run(
            self._sp.user_playlist_create,
            user=user_id,
            name=name,
            public=public,
            collaborative=False,
            description=description,
        )
        return SpotifyPlaylist.from_raw(RawPlaylist.model_validate(raw))

    async def add_tracks_to_playlist(
        self, playlist_id: str, track_uris: Sequence[str], position: int | None = None
    ) -> None:
        chunks = [list(track_uris[i : i + 100]) for i in range(0, len(track_uris), 100)]
        for chunk in chunks:
            await self._run(self._sp.playlist_add_items, playlist_id, chunk, position)

    async def get_playlist(self, playlist_id: str) -> SpotifyPlaylist:
        raw = await self._run(self._sp.playlist, playlist_id)
        return SpotifyPlaylist.from_raw(RawPlaylist.model_validate(raw))

    async def get_playlist_tracks(
        self, playlist_id: str, market: str | None = None, limit: int = 50
    ) -> list[SpotifyTrack]:
        tracks: list[SpotifyTrack] = []
        offset = 0
        while True:
            raw = await self._run(
                self._sp.playlist_items,
                playlist_id,
                limit=limit,
                offset=offset,
                market=market,
                additional_types=("track",),
            )
            page = RawPlaylistItemsPage.model_validate(raw)
            for item in page.items:
                if item.track and item.track.id:
                    tracks.append(SpotifyTrack.from_raw(item.track))
            if page.next is None:
                break
            offset += limit
        return tracks

    async def clear_playlist(self, playlist_id: str) -> None:
        tracks = await self.get_playlist_tracks(playlist_id)
        if not tracks:
            return
        uris = [t.uri for t in tracks]
        chunks = [uris[i : i + 100] for i in range(0, len(uris), 100)]
        for chunk in chunks:
            await self._run(
                self._sp.playlist_remove_all_occurrences_of_items, playlist_id, chunk
            )

    async def remove_tracks_from_playlist(
        self, playlist_id: str, track_uris: Sequence[str]
    ) -> None:
        chunks = [list(track_uris[i : i + 100]) for i in range(0, len(track_uris), 100)]
        for chunk in chunks:
            await self._run(
                self._sp.playlist_remove_all_occurrences_of_items, playlist_id, chunk
            )

    async def _run(self, fn, *args, **kwargs):
        return await asyncio.to_thread(fn, *args, **kwargs)
