import os
from pathlib import Path

import questionary
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

from prompster.agent import Agent
from prompster.agent.views import ToolCallEvent
from prompster.cli.commands.hister_agent import create_agent
from prompster.cli.voice import push_to_talk
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
    "/voice": "Push-to-talk \u2014 record & transcribe (also Ctrl+R)",
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


async def _voice_flow(console: Console) -> str | None:
    try:
        return await push_to_talk(console)
    except Exception as exc:
        console.print(f"\n  [bold red]Voice error:[/bold red] {exc}\n")
        return None


async def run_repl(console: Console) -> None:
    current_model_key = default_model_key()
    agent = create_agent(current_model_key)

    # Ctrl+R triggers push-to-talk
    voice_requested: list[bool] = [False]
    kb = KeyBindings()

    @kb.add("c-r", eager=True)  # Ctrl+R for voice recording
    def _voice_trigger(event: object) -> None:
        voice_requested[0] = True
        buf = event.current_buffer  # type: ignore[attr-defined]
        buf.text = ""
        buf.validate_and_handle()

    session: PromptSession[str] = PromptSession(
        history=InMemoryHistory(), key_bindings=kb
    )

    console.print(
        "  Tell me your [bold magenta]vibe[/bold magenta] — I'll build the deck.\n"
    )

    while True:
        try:
            user_input = (
                await session.prompt_async(
                    HTML("<ansicyan><b>❯</b></ansicyan> "),
                    placeholder=HTML(
                        '<style fg="ansidarkgray">Start typing... (Ctrl+R for voice)</style>'
                    ),
                )
            ).strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n  [bold magenta]Bye![/bold magenta]\n")
            break

        # Handle Ctrl+Space voice trigger
        if voice_requested[0]:
            voice_requested[0] = False
            text = await _voice_flow(console)
            if not text:
                continue
            # Pre-fill prompt so user can review/edit before sending
            user_input = (
                await session.prompt_async(
                    HTML("<ansicyan><b>❯</b></ansicyan> "),
                    default=text,
                )
            ).strip()
            if not user_input:
                continue

        if not user_input:
            continue

        cmd = user_input.lower()

        if cmd in ("/exit", "/quit", "/q"):
            console.print("\n  [bold magenta]Bye![/bold magenta]\n")
            break
        elif cmd == "/help":
            _print_help(console)
        elif cmd in ("/voice", "/v"):
            text = await _voice_flow(console)
            if not text:
                continue
            user_input = (
                await session.prompt_async(
                    HTML("<ansicyan><b>❯</b></ansicyan> "),
                    default=text,
                )
            ).strip()
            if not user_input:
                continue
            await _handle_message(agent, user_input, console)
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
