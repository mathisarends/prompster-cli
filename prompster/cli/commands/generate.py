import click
import questionary
from questionary import Style

from prompster.cli.config import MODELS, get_model

GENRES = [
    "Pop", "Rock", "Hip-Hop", "R&B", "Electronic",
    "Jazz", "Classical", "Metal", "Indie", "Country",
    "Reggae", "Latin", "Folk", "Soul", "Punk",
]

VIBES = [
    "Party", "Chill", "Nostalgia", "Road Trip",
    "Workout", "Heartbreak", "Summer", "Dark & Moody",
    "Feel Good", "Epic",
]

STYLE = Style([
    ("qmark", "fg:magenta bold"),
    ("question", "fg:white bold"),
    ("pointer", "fg:cyan bold"),
    ("highlighted", "fg:cyan bold"),
    ("checked", "fg:green bold"),
    ("answer", "fg:green bold"),
])


def run_generate() -> None:
    """Interactive card generation wizard."""
    model_id = get_model()
    model_info = MODELS.get(model_id, {})

    click.echo()
    click.echo(
        "  Using model: "
        + click.style(model_info.get("name", model_id), fg="green", bold=True)
        + click.style("  (change with ", fg="bright_black")
        + click.style("/model", fg="yellow")
        + click.style(")", fg="bright_black")
    )

    # Step 1 — Genres
    click.echo(click.style("\n  ── Step 1 / 3 — Genres", fg="magenta", bold=True))
    click.echo()
    genres = questionary.checkbox(
        "Select genres",
        choices=GENRES,
        style=STYLE,
        instruction="(space to select, enter to confirm)",
    ).ask()

    if genres is None:
        click.echo(click.style("  Aborted.\n", fg="red"))
        return

    # Step 2 — Vibes
    click.echo(click.style("\n  ── Step 2 / 3 — Vibes", fg="magenta", bold=True))
    click.echo()
    vibes = questionary.checkbox(
        "Select vibes",
        choices=VIBES,
        style=STYLE,
        instruction="(space to select, enter to confirm)",
    ).ask()

    if vibes is None:
        click.echo(click.style("  Aborted.\n", fg="red"))
        return

    # Step 3 — Notes
    click.echo(click.style("\n  ── Step 3 / 3 — Notes", fg="magenta", bold=True))
    click.echo()
    notes = questionary.text(
        "Any additional notes?",
        style=STYLE,
    ).ask()

    if notes is None:
        click.echo(click.style("  Aborted.\n", fg="red"))
        return

    # Summary
    click.echo(click.style("\n  ── Summary ──────────────────────────\n", fg="magenta", bold=True))
    click.echo(f"  {click.style('Model:', bold=True)}  {model_info.get('name', model_id)}")
    click.echo(f"  {click.style('Genres:', bold=True)} {', '.join(genres) or '—'}")
    click.echo(f"  {click.style('Vibes:', bold=True)}  {', '.join(vibes) or '—'}")
    click.echo(f"  {click.style('Notes:', bold=True)}  {notes or '—'}")
    click.echo()

    if not click.confirm("  Generate cards with these settings?"):
        click.echo(click.style("\n  Aborted.\n", fg="red"))
        return

    click.echo(click.style("\n  Generating your Hitster deck…\n", fg="green", bold=True))
    # → hier kommt dann dein PlanningAgent rein
