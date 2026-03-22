from llmify import ChatOpenAI
from prompt_toolkit import PromptSession
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import InMemoryHistory
from rich.console import Console

from prompster.agent import Agent, Tools
from prompster.agent.views import ToolCallEvent

COMMANDS: dict[str, str] = {
    "/help": "Show available commands",
    "/reset": "Reset the conversation history",
    "/exit": "Exit Prompster",
}


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
            console.print(f"[dim]⚙ {event.status or event.tool_name}…[/dim]")
        else:
            console.print(event, end="")
    console.print("\n")


async def run_repl(console: Console) -> None:
    tools = Tools()

    @tools.tool(description="Returns the current time.", status="Aktuelle Zeit abrufen")
    async def get_current_time() -> str:
        from datetime import datetime

        return datetime.now().strftime("%H:%M:%S")

    llm = ChatOpenAI(model="gpt-4o-mini")

    agent = Agent(
        instructions="You are a helpful assistant.",
        llm=llm,
        tools=tools,
    )

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
