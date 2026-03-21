import asyncio

from dotenv import load_dotenv
from llmify import ChatOpenAI

from prompster.agent import Agent

load_dotenv()

SYSTEM_PROMPT = """
You are a Hitster card generator assistant. Your job is to understand what the
user wants, ask clarifying questions if needed, and then generate Hitster cards
using the available tools.

When you have enough information, call 'search_spotify' or 'get_playlist_tracks'
and return the result as a list of Hitster cards (song, artist, year).
"""

MOCK_TRACKS = [
    ("Alles nur geliehen", "Die Toten Hosen", 1994),
    ("Westerland", "Die Ärzte", 1990),
    ("99 Luftballons", "Nena", 1983),
    ("Du hast", "Rammstein", 1997),
    ("Schrei", "Tokio Hotel", 2005),
    ("Major Tom", "Peter Schilling", 1982),
    ("Nur geträumt", "Nena", 1983),
    ("Atemlos durch die Nacht", "Helene Fischer", 2013),
    ("Rammstein", "Rammstein", 1995),
    ("Hier kommt Alex", "Die Toten Hosen", 1988),
]


def build_agent() -> Agent:
    agent = Agent(llm=ChatOpenAI(model="gpt-4o"), system_prompt=SYSTEM_PROMPT)

    @agent.tools.register(
        name="search_spotify",
        description="Search Spotify for tracks matching a query.",
        parameters={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 20},
            },
            "required": ["query"],
        },
    )
    async def search_spotify(query: str, limit: int = 20) -> str:
        print(f"\n  [tool] search_spotify(query={query!r}, limit={limit})")
        return "\n".join(
            f"{name} — {artist} ({year})" for name, artist, year in MOCK_TRACKS[:limit]
        )

    @agent.tools.register(
        name="get_playlist_tracks",
        description="Fetch all tracks from a Spotify playlist by ID or URL.",
        parameters={
            "type": "object",
            "properties": {
                "playlist_id": {"type": "string"},
            },
            "required": ["playlist_id"],
        },
    )
    async def get_playlist_tracks(playlist_id: str) -> str:
        print(f"\n  [tool] get_playlist_tracks(playlist_id={playlist_id!r})")
        return "\n".join(
            f"{name} — {artist} ({year})" for name, artist, year in MOCK_TRACKS
        )

    return agent


async def main() -> None:
    agent = build_agent()

    print()
    print("  ██╗  ██╗██╗████████╗███████╗████████╗███████╗██████╗ ")
    print("  ██║  ██║██║╚══██╔══╝██╔════╝╚══██╔══╝██╔════╝██╔══██╗")
    print("  ███████║██║   ██║   ███████╗   ██║   █████╗  ██████╔╝")
    print("  ██╔══██║██║   ██║   ╚════██║   ██║   ██╔══╝  ██╔══██╗")
    print("  ██║  ██║██║   ██║   ███████║   ██║   ███████╗██║  ██║")
    print("  ╚═╝  ╚═╝╚═╝   ╚═╝   ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝")
    print()
    print("  Card Generator — describe your game and I'll build a plan.")
    print("  Type 'exit' to quit.\n")

    async with agent:
        while True:
            try:
                user_input = input("  You › ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\n\n  Bye!\n")
                break

            if not user_input:
                continue

            if user_input.lower() in {"exit", "quit", "q"}:
                print("\n  Bye!\n")
                break

            print()
            print("  Assistant › ", end="", flush=True)

            async for chunk in await agent.stream(user_input):
                print(chunk, end="", flush=True)

            print("\n")


if __name__ == "__main__":
    asyncio.run(main())