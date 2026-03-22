import inspect
from collections.abc import Callable
from typing import Any

from prompster.agent.tools.schema_builder import ToolSchemaBuilder


class Tool:
    def __init__(
        self,
        name: str,
        description: str,
        fn: Callable[..., Any],
        status: str | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.fn = fn
        self._schema_builder = ToolSchemaBuilder(self.fn)
        self.status = status

    async def execute(self, args: dict[str, Any]) -> str:
        if inspect.iscoroutinefunction(self.fn):
            result = await self.fn(**args)
        else:
            result = self.fn(**args)
        return str(result) if result is not None else ""

    def to_schema(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self._schema_builder.build(),
            },
        }

    def __eq__(self, other: object) -> bool:
        return self.name == other.name if isinstance(other, Tool) else NotImplemented

    def __hash__(self) -> int:
        return hash(self.name)
