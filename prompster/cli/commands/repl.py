from llmify import ChatOpenAI
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console

from prompster.agent import Agent, Tools
from prompster.agent.views import ToolCallEvent
from prompster.spotify import SpotifyClient, SpotifyCredentials

COMMANDS: dict[str, str] = {
    "/help": "Show available commands",
    "/reset": "Reset the conversation history",
    "/exit": "Exit Prompster",
}


def _print_help(console: Console) -> None:
    console.print()
    console.print("  [bold yellow]Available commands:[/bold yellow]\n")
    for cmd, desc in COMMANDS.items():
        console.print(f"  [bold cyan]{cmd:<20}[/bold cyan] [dim]{desc}[/dim]")
    console.print()


async def _handle_message(agent: Agent, user_input: str, console: Console) -> None:
    console.print()
    async for event in agent.run(user_input):
        if isinstance(event, ToolCallEvent):
            console.print(f"[dim]⚙ {event.status or event.tool_name}…[/dim]")
        else:
            console.print(event, end="")
    console.print("\n")


def _build_spotify_tools(tools: Tools, client: SpotifyClient) -> None:
    @tools.tool(
        description="Search Spotify for tracks matching a query. Returns title, artist, year and URI for each result.",
        status="Spotify durchsuchen",
    )
    async def search_tracks(query: str, limit: int = 10) -> str:
        tracks = await client.search_tracks(query, limit=limit)
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


async def run_repl(console: Console) -> None:
    tools = Tools()

    credentials = SpotifyCredentials()
    spotify = SpotifyClient(credentials)
    _build_spotify_tools(tools, spotify)

    llm = ChatOpenAI(model="gpt-4o-mini")

    agent = Agent(
        instructions=(
            "You are Prompster, a Hitster deck assistant. "
            "Help the user build thematic Spotify playlists for Hitster card games. "
            "Search for fitting tracks, propose a selection, create the playlist once confirmed, "
            "and summarise the final deck with title, artist and year per card."
        ),
        llm=llm,
        tools=tools,
    )

    session: PromptSession[str] = PromptSession(history=InMemoryHistory())

    while True:
        try:
            user_input = (
                await session.prompt_async(
                    HTML("<ansicyan><b>❯</b></ansicyan> "),
                    placeholder=HTML(
                        '<style fg="ansidarkgray">Describe a Hitster theme…</style>'
                    ),
                )
            ).strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n  [bold magenta]Bye![/bold magenta]\n")
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        if cmd in ("/exit", "/quit", "/q"):
            console.print("\n  [bold magenta]Bye![/bold magenta]\n")
            break
        elif cmd == "/help":
            _print_help(console)
        elif cmd == "/reset":
            agent.reset()
            console.print("\n  [dim]Conversation reset.[/dim]\n")
        else:
            await _handle_message(agent, user_input, console)
