import asyncio
from pathlib import Path

import rich_click as click
from dotenv import load_dotenv
from llmify import ChatOpenAI
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console

from prompster.agent import Agent, Tools
from prompster.agent.views import ToolCallEvent

load_dotenv(override=True)

BANNER = """\

  ██████╗ ██████╗  ██████╗ ███╗   ███╗██████╗ ███████╗████████╗███████╗██████╗
  ██╔══██╗██╔══██╗██╔═══██╗████╗ ████║██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔══██╗
  ██████╔╝██████╔╝██║   ██║██╔████╔██║██████╔╝███████╗   ██║   █████╗  ██████╔╝
  ██╔═══╝ ██╔══██╗██║   ██║██║╚██╔╝██║██╔═══╝ ╚════██║   ██║   ██╔══╝  ██╔══██╗
  ██║     ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║     ███████║   ██║   ███████╗██║  ██║
  ╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
"""

COMMANDS: dict[str, str] = {
    "/help": "Show available commands",
    "/reset": "Reset the conversation history",
    "/exit": "Exit Prompster",
}


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


def _print_help(console: Console) -> None:
    console.print()
    console.print("  [bold yellow]Available commands:[/bold yellow]\n")
    for cmd, desc in COMMANDS.items():
        console.print(f"  [bold cyan]{cmd:<20}[/bold cyan] [dim]{desc}[/dim]")
    console.print()


async def _handle_message(agent: Agent, user_input: str, console: Console) -> None:
    console.print()
    async for event in agent.run(user_input):
        if isinstance(event, ToolCallEvent):
            console.print(f"  [dim]⚙ {event.tool_name}…[/dim]")
        else:
            console.print(event, end="")
    console.print("\n")


async def _repl() -> None:
    console = Console()

    tools = Tools()

    @tools.tool(name="get_current_time", description="Returns the current time.")
    async def get_current_time() -> str:
        from datetime import datetime

        return datetime.now().strftime("%H:%M:%S")

    llm = ChatOpenAI(model="gpt-4o-mini")

    agent = Agent(
        instructions="You are a helpful assistant.",
        llm=llm,
        tools=tools,
    )

    _print_welcome(console, model_name="gpt-4o-mini")

    session: PromptSession[str] = PromptSession(history=InMemoryHistory())

    while True:
        try:
            user_input = (
                await session.prompt_async(
                    HTML("<ansicyan><b>❯</b></ansicyan> "),
                    placeholder=HTML(
                        '<style fg="ansidarkgray">Describe a Hitster theme…</style>'
                    ),
                )
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
        elif cmd == "/reset":
            agent.reset()
            console.print("\n  [dim]Conversation reset.[/dim]\n")
        else:
            await _handle_message(agent, user_input, console)


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
    asyncio.run(_repl())
