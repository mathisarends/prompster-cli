import asyncio

from llmify import ChatOpenAI
from dotenv import load_dotenv

from prompster.agent import HitsterAgent

load_dotenv()


SYSTEM_PROMPT = """
You are a Hitster card generator. Given a theme or playlist, search Spotify
for matching tracks and return a list of Hitster cards (song, artist, year).
Always call 'search_spotify' or 'get_playlist_tracks' first, then summarize the result.
"""

MOCK_TRACKS = [
    ("Alles nur geliehen", "Die Toten Hosen", 1994),
    ("Sonne", "Rammstein", 2001),
    ("Nur geträumt", "Nena", 1983),
    ("Atemlos durch die Nacht", "Helene Fischer", 2013),
    ("Du hast", "Rammstein", 1997),
    ("99 Luftballons", "Nena", 1983),
    ("Schrei", "Tokio Hotel", 2005),
    ("Major Tom", "Peter Schilling", 1982),
    ("Rammstein", "Rammstein", 1995),
    ("Westerland", "Die Ärzte", 1990),
]


def build_agent() -> HitsterAgent:
    agent = HitsterAgent(
        llm=ChatOpenAI(model="gpt-4o"),
        system_prompt=SYSTEM_PROMPT,
    )

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
        return "\n".join(
            f"{name} — {artist} ({year})"
            for name, artist, year in MOCK_TRACKS[:limit]
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
        return "\n".join(
            f"{name} — {artist} ({year})"
            for name, artist, year in MOCK_TRACKS
        )

    return agent


async def main() -> None:
    agent = build_agent()

    result = await agent.run("Generate 10 Hitster cards for 90s German pop music")

    if result.success:
        print(result.message)
    else:
        print(f"Agent failed after {len(result.tool_calls_made)} tool calls: {result.message}")


if __name__ == "__main__":
    asyncio.run(main())