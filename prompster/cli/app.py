import sys

import rich_click as click
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import InMemoryHistory

from prompster.cli.commands.generate import run_generate
from prompster.cli.commands.model import run_model
from prompster.cli.config import MODELS, get_model

BANNER = """\

  ██████╗ ██████╗  ██████╗ ███╗   ███╗██████╗ ███████╗████████╗███████╗██████╗
  ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗
  ██████╔╝██████╔╝██║   ██║██╔████╔██║██████╔╝███████╗   ██║   █████╗  ██████╔╝
  ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔═══╝ ╚════██║   ██║   ██╔══╝  ██╔══██╗
  ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║     ███████║   ██║   ███████╗██║  ██║
  ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
"""

COMMANDS: dict[str, str] = {
    "/generate": "Generate a custom Hitster card deck",
    "/model": "Switch the AI model",
    "/help": "Show available commands",
    "/exit": "Exit Prompster",
}


def _print_help() -> None:
    click.echo()
    click.echo(click.style("  Available commands:\n", fg="yellow", bold=True))
    for cmd, desc in COMMANDS.items():
        click.echo(
            f"  {click.style(cmd, fg='cyan', bold=True):<30s} {desc}"
        )
    click.echo()


def _print_status_bar() -> None:
    model_id = get_model()
    model_name = MODELS.get(model_id, {}).get("name", model_id)
    click.echo(
        click.style("  Model: ", fg="bright_black")
        + click.style(model_name, fg="green", bold=True)
        + click.style(f"  (/model to change)", fg="bright_black")
    )
    click.echo()


def _make_prompt() -> HTML:
    model_id = get_model()
    model_name = MODELS.get(model_id, {}).get("name", model_id)
    return HTML(
        f'<style fg="grey">({model_name})</style> '
        f'<style fg="magenta" bold="true">prompster</style>'
        f'<style fg="cyan" bold="true"> > </style>'
    )


def _repl() -> None:
    click.echo(click.style(BANNER, fg="magenta", bold=True))
    click.echo(
        "  "
        + click.style("Describe a theme", fg="cyan", bold=True)
        + click.style(" → ", fg="white")
        + click.style("get a Hitster deck.", fg="green")
    )
    click.echo()
    _print_status_bar()
    click.echo(
        click.style("  Type ", fg="bright_black")
        + click.style("/help", fg="yellow")
        + click.style(" for commands, ", fg="bright_black")
        + click.style("Ctrl+C", fg="yellow")
        + click.style(" to exit.\n", fg="bright_black")
    )

    session: PromptSession[str] = PromptSession(history=InMemoryHistory())

    while True:
        try:
            user_input = session.prompt(_make_prompt()).strip()
        except (KeyboardInterrupt, EOFError):
            click.echo(click.style("\n  Bye!\n", fg="magenta", bold=True))
            break

        if not user_input:
            continue

        cmd = user_input.lower()

        if cmd in ("/exit", "/quit", "/q"):
            click.echo(click.style("\n  Bye!\n", fg="magenta", bold=True))
            break
        elif cmd == "/help":
            _print_help()
        elif cmd == "/model":
            run_model()
        elif cmd == "/generate":
            run_generate()
        else:
            click.echo(
                click.style(f"\n  Unknown command: ", fg="red")
                + click.style(user_input, fg="white", bold=True)
                + click.style("  — type /help for available commands.\n", fg="bright_black")
            )


@click.rich_config(
    help_config=click.RichHelpConfiguration(
        style_header_text="bold magenta",
        style_option="bold cyan",
        style_switch="bold green",
        style_metavar="dim",
        style_commands_table_show_lines=True,
        style_options_panel_border="magenta",
        style_commands_panel_border="cyan",
        use_rich_markup=True,
        use_markdown=True,
    )
)
@click.command()
def cli() -> None:
    """Prompster — Generate unique Hitster card decks with AI."""
    _repl()
