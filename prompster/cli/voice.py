import asyncio
import sys

from rich.console import Console
from rich.live import Live
from rich.text import Text
from transcriptify import OpenAIWhisper
from transcriptify.audio.adapters.mic import MicrophoneAudioDevice


async def push_to_talk(console: Console) -> str | None:
    loop = asyncio.get_event_loop()
    stop = asyncio.Event()

    async def _wait_enter() -> None:
        await loop.run_in_executor(None, sys.stdin.readline)
        stop.set()

    enter_task = asyncio.create_task(_wait_enter())

    async with MicrophoneAudioDevice(sample_rate=16_000) as mic:
        start = loop.time()

        with Live(console=console, refresh_per_second=4, transient=True) as live:
            while not stop.is_set():
                elapsed = int(loop.time() - start)
                m, s = divmod(elapsed, 60)
                bar_len = min(elapsed, 20)
                bar = "\u2588" * bar_len + "\u2591" * (20 - bar_len)
                live.update(
                    Text(
                        f"  \u25cf REC  {m}:{s:02d}  {bar}  \u2014 Enter to stop",
                        style="bold red",
                    )
                )
                await asyncio.sleep(0.25)

        # Stop the mic stream so record() finishes collecting
        await mic._queue.put(None)
        audio = await mic.record(seconds=0)  # collects everything already buffered

    await enter_task

    if not audio.data:
        console.print("  [dim]No audio captured.[/dim]\n")
        return None

    console.print("  [dim]Transcribing\u2026[/dim]")
    whisper = OpenAIWhisper()
    result = await whisper.transcribe(audio)
    console.print()
    return result.text
