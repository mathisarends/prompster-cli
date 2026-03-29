from pathlib import Path
from typing import Annotated

from agentory import Agent, Inject, Tools

from prompster.export import DeckRenderer, TrackCard
from prompster.llm import create_llm, default_model_key
from prompster.spotify import SpotifyClient, SpotifyCredentials

_SYSTEM_PROMPT = (Path(__file__).parent / "system_prompt.md").read_text(
    encoding="utf-8"
)


class HitsterAgent:
    def __init__(self, model: str | None = None) -> None:
        self._tools = Tools()
        self._tools.provide(SpotifyClient(SpotifyCredentials()), DeckRenderer())
        self._register_tools()
        self._agent = Agent(
            instructions=_SYSTEM_PROMPT,
            tools=self._tools,
            llm=create_llm(model or default_model_key()),
        )

    def reset(self) -> None:
        self._agent.reset()

    def run(self, user_input: str):
        return self._agent.run(user_input)

    def _register_tools(self) -> None:
        tools = self._tools

        @tools.action(
            description="Search Spotify for tracks matching a query. Returns title, artist, year and URI for each result.",
            status=lambda args: f"Suche nach \u201e{args.get('query', '')}\u201c",
        )
        async def search_tracks(
            spotify: Annotated[SpotifyClient, Inject], query: str, limit: int = 10
        ) -> str:
            tracks = await spotify.search_tracks(query, limit=min(limit, 50))
            if not tracks:
                return "No tracks found."
            return "\n".join(
                self._format_track(index + 1, track)
                for index, track in enumerate(tracks)
            )

        @tools.action(
            description="Search Spotify for albums matching a query. Returns album name, artist, year, track count and URI.",
            status=lambda args: f"Alben suchen: \u201e{args.get('query', '')}\u201c",
        )
        async def search_albums(
            spotify: Annotated[SpotifyClient, Inject], query: str, limit: int = 10
        ) -> str:
            albums = await spotify.search_albums(query, limit=min(limit, 50))
            if not albums:
                return "No albums found."
            return "\n".join(
                self._format_album(index + 1, album)
                for index, album in enumerate(albums)
            )

        @tools.action(
            description="Search Spotify for public playlists matching a query. Returns playlist name, track count and ID.",
            status=lambda args: f"Playlists suchen: \u201e{args.get('query', '')}\u201c",
        )
        async def search_playlists(
            spotify: Annotated[SpotifyClient, Inject], query: str, limit: int = 10
        ) -> str:
            playlists = await spotify.search_playlists(query, limit=min(limit, 50))
            if not playlists:
                return "No playlists found."
            return "\n".join(
                f"{index + 1}. {playlist.name} ({playlist.track_count} tracks)  id={playlist.id}  url={playlist.url}"
                for index, playlist in enumerate(playlists)
            )

        @tools.action(
            description="Get albums by an artist (pass artist URI or ID). Returns album name, year, track count.",
            status="Künstler-Alben laden",
        )
        async def get_artist_albums(
            spotify: Annotated[SpotifyClient, Inject],
            artist_id: str,
            include_groups: str = "album,single",
            limit: int = 20,
        ) -> str:
            albums = await spotify.get_artist_albums(
                artist_id, include_groups=include_groups, limit=limit
            )
            if not albums:
                return "No albums found."
            return "\n".join(
                self._format_album(index + 1, album)
                for index, album in enumerate(albums)
            )

        @tools.action(
            description="Get an artist's top tracks. Pass artist URI or ID. Returns title, artist, year and URI.",
            status="Top-Tracks laden",
        )
        async def get_artist_top_tracks(
            spotify: Annotated[SpotifyClient, Inject],
            artist_id: str,
            country: str = "DE",
        ) -> str:
            tracks = await spotify.get_artist_top_tracks(artist_id, country=country)
            if not tracks:
                return "No top tracks found."
            return "\n".join(
                self._format_track(index + 1, track)
                for index, track in enumerate(tracks)
            )

        @tools.action(
            description="Get all tracks of an album by album URI or ID. Returns title, artist, year and URI.",
            status="Album-Tracks laden",
        )
        async def get_album_tracks(
            spotify: Annotated[SpotifyClient, Inject], album_id: str
        ) -> str:
            tracks = await spotify.get_album_tracks(album_id)
            if not tracks:
                return "No tracks found."
            return "\n".join(
                self._format_track(index + 1, track)
                for index, track in enumerate(tracks)
            )

        @tools.action(
            description="Create a Spotify playlist for the current user. Returns the playlist ID and URL.",
            status=lambda args: f"Playlist erstellen: \u201e{args.get('name', '')}\u201c",
        )
        async def create_playlist(
            spotify: Annotated[SpotifyClient, Inject], name: str, description: str = ""
        ) -> str:
            prefixed_name = "Hitster Deck: " + name
            playlist = await spotify.create_playlist(
                prefixed_name, description=description
            )
            return f"Created playlist '{playlist.name}' — id={playlist.id}  url={playlist.url}"

        @tools.action(
            description="Add tracks to an existing Spotify playlist by playlist ID and a list of Spotify track URIs.",
            status=lambda args: f"{len(args.get('track_uris', []))} Tracks hinzufügen",
        )
        async def add_tracks_to_playlist(
            spotify: Annotated[SpotifyClient, Inject],
            playlist_id: str,
            track_uris: list[str],
        ) -> str:
            invalid = [u for u in track_uris if not u.startswith("spotify:track:")]
            if invalid:
                return f"Error: invalid track URIs (must start with 'spotify:track:'): {invalid}"

            await spotify.add_tracks_to_playlist(playlist_id, track_uris)
            return f"Added {len(track_uris)} track(s) to playlist {playlist_id}."

        @tools.action(
            description="Get all tracks of an existing Spotify playlist. Returns title, artist, year and URI per track.",
            status="Playlist-Tracks laden",
        )
        async def get_playlist_tracks(
            spotify: Annotated[SpotifyClient, Inject], playlist_id: str
        ) -> str:
            tracks = await spotify.get_playlist_tracks(playlist_id)
            if not tracks:
                return "Playlist is empty."
            return "\n".join(
                self._format_track(index + 1, track)
                for index, track in enumerate(tracks)
            )

        @tools.action(
            description="Remove specific tracks from a Spotify playlist by playlist ID and a list of track URIs.",
            status=lambda args: f"{len(args.get('track_uris', []))} Tracks entfernen",
        )
        async def remove_tracks_from_playlist(
            spotify: Annotated[SpotifyClient, Inject],
            playlist_id: str,
            track_uris: list[str],
        ) -> str:
            await spotify.remove_tracks_from_playlist(playlist_id, track_uris)
            return f"Removed {len(track_uris)} track(s) from playlist {playlist_id}."

        @tools.action(
            description="Remove all tracks from a Spotify playlist (clear it completely).",
            status="Playlist leeren",
        )
        async def clear_playlist(
            spotify: Annotated[SpotifyClient, Inject], playlist_id: str
        ) -> str:
            await spotify.clear_playlist(playlist_id)
            return f"Playlist {playlist_id} cleared."

        @tools.action(
            description="Generate Hitster cards as a PDF for the given Spotify playlist. Returns the path to the generated PDF.",
            status="Karten generieren…",
        )
        async def generate_cards(
            spotify: Annotated[SpotifyClient, Inject],
            deck_renderer: Annotated[DeckRenderer, Inject],
            playlist_id: str,
        ) -> str:
            tracks = await spotify.get_playlist_tracks(playlist_id)
            if not tracks:
                return "Playlist is empty — no cards generated."
            cards = [
                TrackCard(
                    title=t.title,
                    artist_names=t.artist_names,
                    release_year=t.release_year,
                    spotify_url=t.url,
                )
                for t in tracks
            ]
            output = Path.cwd() / "output" / "hitster-deck.pdf"
            output.parent.mkdir(exist_ok=True)
            await deck_renderer.render(cards, output)
            return f"Cards generated: {output}  ({len(cards)} cards)"

    @staticmethod
    def _format_track(index: int, track) -> str:
        artist_uris = ", ".join(artist.uri for artist in track.artists)
        return (
            f"{index}. {track.title} – {track.artist_names} ({track.release_year})"
            f"  uri={track.uri}  artist_uris=[{artist_uris}]"
        )

    @staticmethod
    def _format_album(index: int, album) -> str:
        return (
            f"{index}. {album.name} – {album.artist_names}"
            f" ({album.release_year}, {album.total_tracks} tracks)  uri={album.uri}"
        )
