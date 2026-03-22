import asyncio

import rich_click as click
from dotenv import load_dotenv
from rich.console import Console

from prompster.cli.commands.repl import print_welcome, run_repl
from prompster.llm import MODELS, default_model_key

load_dotenv(override=True)


async def _start() -> None:
    console = Console()
    model_key = default_model_key()
    model_label = MODELS[model_key].label
    print_welcome(console, model_name=model_label)
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
