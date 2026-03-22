from pathlib import Path

import rich_click as click
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console


BANNER = """\

  ██████╗ ██████╗  ██████╗ ███╗   ███╗██████╗ ███████╗████████╗███████╗██████╗
  ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗
  ██████╔╝██████╔╝██║   ██║██╔████╔██║██████╔╝███████╗   ██║   █████╗  ██████╔╝
  ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔═══╝ ╚════██║   ██║   ██╔══╝  ██╔══██╗
  ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║     ███████║   ██║   ███████╗██║  ██║
  ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
"""

COMMANDS: dict[str, str] = {
    "/model":    "Switch the AI model",
    "/help":     "Show available commands",
    "/exit":     "Exit Prompster",
}


def _print_welcome(console: Console) -> None:
    console.print(f"[magenta]{BANNER}[/magenta]")

    console.print("  [bold magenta]Prompster[/bold magenta]")
    console.print(f"  [dim]Prompster uses AI. Check for mistakes.[/dim]  [dim]—  {'gpt-5.4-mini'}[/dim]")
    console.print()

    cwd = f"~/{Path.cwd().name}"
    console.print(f"  [dim]{cwd}[/dim]")
    console.print()


def _print_help(console: Console) -> None:
    console.print()
    console.print("  [bold yellow]Available commands:[/bold yellow]\n")
    for cmd, desc in COMMANDS.items():
        console.print(f"  [bold cyan]{cmd:<20}[/bold cyan] [dim]{desc}[/dim]")
    console.print()


def _repl() -> None:
    console = Console()
    _print_welcome(console)

    session: PromptSession[str] = PromptSession(
        history=InMemoryHistory(),
    )

    while True:
        try:
            user_input = session.prompt(
                HTML('<ansicyan><b>❯</b></ansicyan> '),
                placeholder=HTML(
                    '<style fg="ansidarkgray">Describe a Hitster theme…</style>'
                ),
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
        else:
            console.print(
                f"\n  [red]Unknown command:[/red] [bold white]{user_input}[/bold white]"
                f"  [dim]— type /help for available commands.[/dim]\n"
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