import click
import questionary
from questionary import Style

from prompster.cli.config import DEFAULT_MODEL, MODELS, get_model, set_model

STYLE = Style([
    ("qmark", "fg:magenta bold"),
    ("question", "fg:white bold"),
    ("pointer", "fg:cyan bold"),
    ("highlighted", "fg:cyan bold"),
    ("selected", "fg:green bold"),
    ("answer", "fg:green bold"),
])


def _format_choice(model_id: str) -> str:
    info = MODELS[model_id]
    return f"{info['name']}  ({info['provider']} — {info['description']})"


@click.command()
def model() -> None:
    """Switch the AI model used for card generation."""
    current = get_model()
    current_info = MODELS.get(current, {})

    click.echo()
    click.echo(
        "  Current model: "
        + click.style(current_info.get("name", current), fg="green", bold=True)
        + click.style(f"  ({current})", fg="bright_black")
    )
    click.echo()

    choices = [
        questionary.Choice(
            title=_format_choice(mid),
            value=mid,
            checked=(mid == current),
        )
        for mid in MODELS
    ]

    selected = questionary.select(
        "Switch model",
        choices=choices,
        default=current,
        style=STYLE,
        instruction="(arrow keys to move, enter to select)",
    ).ask()

    if selected is None:
        click.echo(click.style("  Aborted.\n", fg="red"))
        return

    if selected == current:
        click.echo(click.style("  No change — keeping current model.\n", fg="bright_black"))
        return

    set_model(selected)
    new_info = MODELS[selected]
    click.echo(
        "\n  Switched to "
        + click.style(new_info["name"], fg="green", bold=True)
        + click.style(f"  ({selected})\n", fg="bright_black")
    )
