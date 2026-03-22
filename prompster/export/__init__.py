from pathlib import Path

from .renderer import DeckRenderer
from .views import TrackCard


async def render_deck(tracks, output: Path) -> Path:
    """Render a deck from a list of TrackCard or SpotifyTrack objects."""
    cards = [
        t
        if isinstance(t, TrackCard)
        else TrackCard(
            title=t.title,
            artist_names=t.artist_names,
            release_year=t.release_year,
            spotify_url=t.url,
        )
        for t in tracks
    ]
    return await DeckRenderer().render(cards, output)


__all__ = ["DeckRenderer", "TrackCard", "render_deck"]
