import logging
from collections.abc import Callable
from typing import Any

from prompster.agent.tools.views import Tool

logger = logging.getLogger(__name__)


class Tools:
    def __init__(self) -> None:
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def tool(self, name: str, description: str, status: str | None = None) -> Callable:
        def decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
            self.register(Tool(name=name, description=description, fn=fn, status=status))
            return fn
        return decorator

    async def execute(self, name: str, args: dict) -> str:
        tool = self._tools.get(name)
        if tool is None:
            raise ValueError(f"Unknown tool '{name}'. Available: {list(self._tools)}")
        try:
            return await tool.execute(args)
        except Exception as e:
            logger.exception("Tool '%s' raised an exception", name)
            return f"Error: {e}"

    def to_schema(self) -> list[dict]:
        return [t.to_schema() for t in self._tools.values()]