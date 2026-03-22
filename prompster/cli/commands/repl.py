import os
from pathlib import Path

import questionary
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

from prompster.agent import Agent
from prompster.agent.views import ToolCallEvent
from prompster.cli.commands.hister_agent import create_agent
from prompster.llm import MODELS, create_llm, default_model_key

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
    "/model": "Switch the LLM model",
    "/reset": "Reset the conversation history",
    "/exit": "Exit Prompster",
}


def _print_help(console: Console) -> None:
    console.print()
    console.print("  [bold yellow]Available commands:[/bold yellow]\n")
    for cmd, desc in COMMANDS.items():
        console.print(f"  [bold cyan]{cmd:<20}[/bold cyan] [dim]{desc}[/dim]")
    console.print()


def print_welcome(console: Console, model_name: str) -> None:
    console.print(f"[magenta]{BANNER}[/magenta]")
    console.print("  [bold magenta]Prompster[/bold magenta]")
    console.print(
        f"  [dim]Prompster uses AI. Check for mistakes.[/dim]  [dim]—  {model_name}[/dim]"
    )
    console.print()
    cwd = f"~/{Path.cwd().name}"
    console.print(f"  [dim]{cwd}[/dim]")
    console.print()


def _model_choices(current_key: str) -> list[questionary.Choice]:
    choices = []
    for key, info in MODELS.items():
        marker = " (active)" if key == current_key else ""
        choices.append(questionary.Choice(f"{info.label}{marker}", value=key))
    return choices


async def _handle_message(agent: Agent, user_input: str, console: Console) -> None:
    chunks: list[str] = []
    had_tools = False
    live: Live | None = None

    async for event in agent.run(user_input):
        if isinstance(event, ToolCallEvent):
            if not had_tools:
                console.print()
            had_tools = True
            console.print(f"[dim]⚙ {event.status or event.tool_name}…[/dim]")
        else:
            if live is None:
                console.print()
                live = Live(
                    console=console, refresh_per_second=20, vertical_overflow="visible"
                )
                live.start()
            chunks.append(event)
            live.update(Markdown("".join(chunks)))

    if live is not None:
        live.stop()
    elif chunks:
        console.print()
        console.print(Markdown("".join(chunks)))
    console.print()


async def run_repl(console: Console) -> None:
    current_model_key = default_model_key()
    agent = create_agent(current_model_key)
    session: PromptSession[str] = PromptSession(history=InMemoryHistory())

    console.print(
        "  Tell me your [bold magenta]vibe[/bold magenta] — I'll build the deck.\n"
    )

    while True:
        try:
            user_input = (
                await session.prompt_async(
                    HTML("<ansicyan><b>❯</b></ansicyan> "),
                    placeholder=HTML(
                        '<style fg="ansidarkgray">Start typing...</style>'
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
        elif cmd == "/model":
            choice = await questionary.select(
                "Model auswählen:",
                choices=_model_choices(current_model_key),
                default=current_model_key,
            ).ask_async()

            if choice is None or choice == current_model_key:
                continue

            current_model_key = choice
            agent.llm = create_llm(current_model_key)
            info = MODELS[current_model_key]
            os.system("cls" if os.name == "nt" else "clear")
            print_welcome(console, model_name=info.label)
            console.print(f"  [bold green]Switched to {info.label}[/bold green]\n")
        elif cmd == "/reset":
            agent.reset()
            console.print("\n  [dim]Conversation reset.[/dim]\n")
        else:
            await _handle_message(agent, user_input, console)
