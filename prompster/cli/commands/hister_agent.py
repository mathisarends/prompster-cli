from pathlib import Path

import questionary

from prompster.agent import Agent, Tools
from prompster.export import DeckRenderer, TrackCard
from prompster.llm import create_llm, default_model_key
from prompster.spotify import SpotifyClient, SpotifyCredentials

_INSTRUCTIONS = (Path(__file__).parent / "system_prompt.md").read_text(encoding="utf-8")


def _register_spotify_tools(tools: Tools, client: SpotifyClient) -> None:
    @tools.action(
        description="Ask the user how many tracks the playlist should have (= number of cards in the final deck). Call this right before creating the playlist. Returns the number as a string.",
        status="Kartenanzahl abfragen",
    )
    async def ask_card_count() -> str:
        result = await questionary.select(
            "Wie viele Karten?",
            choices=["15", "20", "30", "40", "50"],
            default="30",
        ).ask_async()
        return result or "30"

    @tools.action(
        description="Search Spotify for tracks matching a query. Returns title, artist, year and URI for each result.",
        status=lambda args: f"Suche nach \u201e{args.get('query', '')}\u201c",
    )
    async def search_tracks(query: str, limit: int = 10) -> str:
        tracks = await client.search_tracks(query, limit=min(limit, 50))
        if not tracks:
            return "No tracks found."
        lines = []
        for i, t in enumerate(tracks):
            artist_uris = ", ".join(a.uri for a in t.artists)
            lines.append(
                f"{i + 1}. {t.title} – {t.artist_names} ({t.release_year})  uri={t.uri}  artist_uris=[{artist_uris}]"
            )
        return "\n".join(lines)

    @tools.action(
        description="Search Spotify for albums matching a query. Returns album name, artist, year, track count and URI.",
        status=lambda args: f"Alben suchen: \u201e{args.get('query', '')}\u201c",
    )
    async def search_albums(query: str, limit: int = 10) -> str:
        albums = await client.search_albums(query, limit=min(limit, 50))
        if not albums:
            return "No albums found."
        lines = [
            f"{i + 1}. {a.name} – {a.artist_names} ({a.release_year}, {a.total_tracks} tracks)  uri={a.uri}"
            for i, a in enumerate(albums)
        ]
        return "\n".join(lines)

    @tools.action(
        description="Search Spotify for public playlists matching a query. Returns playlist name, track count and ID.",
        status=lambda args: f"Playlists suchen: \u201e{args.get('query', '')}\u201c",
    )
    async def search_playlists(query: str, limit: int = 10) -> str:
        playlists = await client.search_playlists(query, limit=min(limit, 50))
        if not playlists:
            return "No playlists found."
        lines = [
            f"{i + 1}. {p.name} ({p.track_count} tracks)  id={p.id}  url={p.url}"
            for i, p in enumerate(playlists)
        ]
        return "\n".join(lines)

    @tools.action(
        description="Get albums by an artist (pass artist URI or ID). Returns album name, year, track count.",
        status="Künstler-Alben laden",
    )
    async def get_artist_albums(
        artist_id: str, include_groups: str = "album,single", limit: int = 20
    ) -> str:
        albums = await client.get_artist_albums(
            artist_id, include_groups=include_groups, limit=limit
        )
        if not albums:
            return "No albums found."
        lines = [
            f"{i + 1}. {a.name} – {a.artist_names} ({a.release_year}, {a.total_tracks} tracks)  uri={a.uri}"
            for i, a in enumerate(albums)
        ]
        return "\n".join(lines)

    @tools.action(
        description="Get an artist's top tracks. Pass artist URI or ID. Returns title, artist, year and URI.",
        status="Top-Tracks laden",
    )
    async def get_artist_top_tracks(artist_id: str, country: str = "DE") -> str:
        tracks = await client.get_artist_top_tracks(artist_id, country=country)
        if not tracks:
            return "No top tracks found."
        lines = []
        for i, t in enumerate(tracks):
            artist_uris = ", ".join(a.uri for a in t.artists)
            lines.append(
                f"{i + 1}. {t.title} – {t.artist_names} ({t.release_year})  uri={t.uri}  artist_uris=[{artist_uris}]"
            )
        return "\n".join(lines)

    @tools.action(
        description="Get all tracks of an album by album URI or ID. Returns title, artist, year and URI.",
        status="Album-Tracks laden",
    )
    async def get_album_tracks(album_id: str) -> str:
        tracks = await client.get_album_tracks(album_id)
        if not tracks:
            return "No tracks found."
        lines = []
        for i, t in enumerate(tracks):
            artist_uris = ", ".join(a.uri for a in t.artists)
            lines.append(
                f"{i + 1}. {t.title} – {t.artist_names} ({t.release_year})  uri={t.uri}  artist_uris=[{artist_uris}]"
            )
        return "\n".join(lines)

    @tools.action(
        description="Create a Spotify playlist for the current user. Returns the playlist ID and URL.",
        status=lambda args: f"Playlist erstellen: \u201e{args.get('name', '')}\u201c",
    )
    async def create_playlist(name: str, description: str = "") -> str:
        prefixed_name = "Hitster Deck: " + name
        playlist = await client.create_playlist(prefixed_name, description=description)
        return (
            f"Created playlist '{playlist.name}' — id={playlist.id}  url={playlist.url}"
        )

    @tools.action(
        description="Add tracks to an existing Spotify playlist by playlist ID and a list of Spotify track URIs.",
        status=lambda args: f"{len(args.get('track_uris', []))} Tracks hinzufügen",
    )
    async def add_tracks_to_playlist(playlist_id: str, track_uris: list[str]) -> str:
        await client.add_tracks_to_playlist(playlist_id, track_uris)
        return f"Added {len(track_uris)} track(s) to playlist {playlist_id}."

    @tools.action(
        description="Get all tracks of an existing Spotify playlist. Returns title, artist, year and URI per track.",
        status="Playlist-Tracks laden",
    )
    async def get_playlist_tracks(playlist_id: str) -> str:
        tracks = await client.get_playlist_tracks(playlist_id)
        if not tracks:
            return "Playlist is empty."
        lines = []
        for i, t in enumerate(tracks):
            artist_uris = ", ".join(a.uri for a in t.artists)
            lines.append(
                f"{i + 1}. {t.title} – {t.artist_names} ({t.release_year})  uri={t.uri}  artist_uris=[{artist_uris}]"
            )
        return "\n".join(lines)

    @tools.action(
        description="Remove specific tracks from a Spotify playlist by playlist ID and a list of track URIs.",
        status=lambda args: f"{len(args.get('track_uris', []))} Tracks entfernen",
    )
    async def remove_tracks_from_playlist(
        playlist_id: str, track_uris: list[str]
    ) -> str:
        await client.remove_tracks_from_playlist(playlist_id, track_uris)
        return f"Removed {len(track_uris)} track(s) from playlist {playlist_id}."

    @tools.action(
        description="Remove all tracks from a Spotify playlist (clear it completely).",
        status="Playlist leeren",
    )
    async def clear_playlist(playlist_id: str) -> str:
        await client.clear_playlist(playlist_id)
        return f"Playlist {playlist_id} cleared."

    @tools.action(
        description="Generate Hitster cards as a PDF for the given Spotify playlist. Returns the path to the generated PDF.",
        status="Karten generieren…",
    )
    async def generate_hitster_cards(playlist_id: str) -> str:
        tracks = await client.get_playlist_tracks(playlist_id)
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
        deck_renderer = DeckRenderer()
        await deck_renderer.render(cards, output)
        return f"Cards generated: {output}  ({len(cards)} cards)"


def create_agent(model_key: str | None = None) -> Agent:
    key = model_key or default_model_key()
    tools = Tools()
    spotify = SpotifyClient(SpotifyCredentials())
    _register_spotify_tools(tools, spotify)
    return Agent(
        instructions=_INSTRUCTIONS,
        tools=tools,
        llm=create_llm(key),
    )
