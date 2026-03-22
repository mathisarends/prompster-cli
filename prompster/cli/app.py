import asyncio
from pathlib import Path

import rich_click as click
from dotenv import load_dotenv
from rich.console import Console

from prompster.cli.commands.repl import run_repl

load_dotenv(override=True)

BANNER = """\

  ██████╗ ██████╗  ██████╗ ███╗   ███╗██████╗ ███████╗████████╗███████╗██████╗
  ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗
  ██████╔╝██████╔╝██║   ██║██╔████╔██║██████╔╝███████╗   ██║   █████╗  ██████╔╝
  ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔═══╝ ╚════██║   ██║   ██╔══╝  ██╔══██╗
  ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║     ███████║   ██║   ███████╗██║  ██║
  ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
"""


def _print_welcome(console: Console, model_name: str) -> None:
    console.print(f"[magenta]{BANNER}[/magenta]")
    console.print("  [bold magenta]Prompster[/bold magenta]")
    console.print(
        f"  [dim]Prompster uses AI. Check for mistakes.[/dim]  [dim]—  {model_name}[/dim]"
    )
    console.print()
    cwd = f"~/{Path.cwd().name}"
    console.print(f"  [dim]{cwd}[/dim]")
    console.print()


async def _start() -> None:
    console = Console()
    _print_welcome(console, model_name="gpt-4o-mini")
    await run_repl(console)


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
    asyncio.run(_start())
