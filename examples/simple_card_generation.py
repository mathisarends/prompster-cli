import asyncio
from pathlib import Path

from prompster.export import DeckRenderer, TrackCard

TRACKS = [
    TrackCard(
        "Bohemian Rhapsody",
        "Queen",
        1975,
        "https://open.spotify.com/track/7tFiyTwD0nx5a1eklYtX2J",
    ),
    TrackCard(
        "Billie Jean",
        "Michael Jackson",
        1982,
        "https://open.spotify.com/track/5ChkMS8OtdzJeqyybCc9R5",
    ),
    TrackCard(
        "Smells Like Teen Spirit",
        "Nirvana",
        1991,
        "https://open.spotify.com/track/5ghIJDpPoe3CfHMGu71E6T",
    ),
    TrackCard(
        "Lose Yourself",
        "Eminem",
        2002,
        "https://open.spotify.com/track/7MJQ9Nfxzh8LPZ9e9u68Fq",
    ),
    TrackCard(
        "Rolling in the Deep",
        "Adele",
        2010,
        "https://open.spotify.com/track/4OSBTEdBClEp9dMoRYgTBJ",
    ),
]


async def main() -> None:
    output = Path.cwd() / "output" / "test-deck.pdf"
    output.parent.mkdir(exist_ok=True)
    renderer = DeckRenderer()
    await renderer.render(TRACKS, output)
    print(f"✓ Generated {output} ({len(TRACKS)} cards)")


if __name__ == "__main__":
    asyncio.run(main())
