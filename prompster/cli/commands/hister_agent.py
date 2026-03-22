from pathlib import Path

import questionary
from llmify import ChatOpenAI

from prompster.agent import Agent, Tools
from prompster.export import DeckRenderer, TrackCard
from prompster.spotify import SpotifyClient, SpotifyCredentials

_INSTRUCTIONS = """\
You are Prompster, a creative assistant that helps users generate custom Hitster card decks.

Hitster is a music quiz game where players guess the release year of songs. Each card has a song title, artist, year, and a QR code linking to the song on Spotify.

Before generating any cards, gather the following config:

1. **Theme / Vibe** – Infer this from what the user tells you. If unclear, ask via free text in the conversation.
2. **Difficulty** – call `ask_difficulty` to let the user pick from a list.
3. **Number of cards** – call `ask_card_count` to let the user pick a number.

Once you have all three values from the tools, summarize the config and ask for confirmation before generating.

When generating cards:
1. Use the Spotify tools to find matching tracks. Prefer tracks where the release year is clearly identifiable. Aim for variety in years unless the theme implies a specific era.
2. Once all tracks are collected, call `create_playlist` with a fitting playlist name, then `add_tracks_to_playlist`.
3. Include the returned playlist link as a clickable Markdown link so the user can open it directly in Spotify.

Always respond in the same language the user is writing in. Default to German.
"""


def _register_spotify_tools(tools: Tools, client: SpotifyClient) -> None:
    @tools.tool(
        description="Ask the user to pick a difficulty level. Returns one of: Easy, Medium, Hard.",
        status="Schwierigkeitsgrad abfragen",
    )
    async def ask_difficulty() -> str:
        result = await questionary.select(
            "Schwierigkeitsgrad:",
            choices=[
                questionary.Choice("Easy – bekannte Hits", value="Easy"),
                questionary.Choice("Medium – gemischte Auswahl", value="Medium"),
                questionary.Choice("Hard – Deep Cuts & B-Seiten", value="Hard"),
            ],
        ).ask_async()
        return result or "Medium"

    @tools.tool(
        description="Ask the user how many cards to generate. Returns the number as a string.",
        status="Kartenanzahl abfragen",
    )
    async def ask_card_count() -> str:
        result = await questionary.select(
            "Wie viele Karten?",
            choices=["15", "20", "30", "40", "50"],
            default="30",
        ).ask_async()
        return result or "30"

    @tools.tool(
        description="Search Spotify for tracks matching a query. Returns title, artist, year and URI for each result.",
        status="Spotify durchsuchen",
    )
    async def search_tracks(query: str, limit: int = 10) -> str:
        tracks = await client.search_tracks(query, limit=min(limit, 50))
        if not tracks:
            return "No tracks found."
        lines = [
            f"{i + 1}. {t.title} – {t.artist_names} ({t.release_year})  uri={t.uri}"
            for i, t in enumerate(tracks)
        ]
        return "\n".join(lines)

    @tools.tool(
        description="Create a Spotify playlist for the current user. Returns the playlist ID and URL.",
        status="Playlist erstellen",
    )
    async def create_playlist(name: str, description: str = "") -> str:
        playlist = await client.create_playlist(name, description=description)
        return (
            f"Created playlist '{playlist.name}' — id={playlist.id}  url={playlist.url}"
        )

    @tools.tool(
        description="Add tracks to an existing Spotify playlist by playlist ID and a list of Spotify track URIs.",
        status="Tracks zur Playlist hinzufügen",
    )
    async def add_tracks_to_playlist(playlist_id: str, track_uris: list[str]) -> str:
        await client.add_tracks_to_playlist(playlist_id, track_uris)
        return f"Added {len(track_uris)} track(s) to playlist {playlist_id}."

    @tools.tool(
        description="Get all tracks of an existing Spotify playlist. Returns title, artist, year and URI per track.",
        status="Playlist-Tracks laden",
    )
    async def get_playlist_tracks(playlist_id: str) -> str:
        tracks = await client.get_playlist_tracks(playlist_id)
        if not tracks:
            return "Playlist is empty."
        lines = [
            f"{i + 1}. {t.title} – {t.artist_names} ({t.release_year})  uri={t.uri}"
            for i, t in enumerate(tracks)
        ]
        return "\n".join(lines)

    @tools.tool(
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
        output = Path.cwd() / "hitster-deck.pdf"
        await DeckRenderer().render(cards, output)
        return f"Cards generated: {output}  ({len(cards)} cards)"


def create_agent() -> Agent:
    tools = Tools()
    spotify = SpotifyClient(SpotifyCredentials())
    _register_spotify_tools(tools, spotify)
    return Agent(
        instructions=_INSTRUCTIONS,
        tools=tools,
        llm=ChatOpenAI(model="gpt-4o-mini"),
    )
