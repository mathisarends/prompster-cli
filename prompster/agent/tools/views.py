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
        status: str | Callable[[dict[str, Any]], str] | None = None,
    ) -> None:
        self.name = name
        self.description = description
        self.fn = fn
        self._schema_builder = ToolSchemaBuilder(self.fn)
        self.status = status
        if callable(self.status):
            self._validate_status_keys()

    def _validate_status_keys(self) -> None:
        params = set(inspect.signature(self.fn).parameters.keys())

        class _TrackingDict(dict):
            def __init__(self) -> None:
                super().__init__()
                self.accessed: set[str] = set()

            def get(self, key: str, default: Any = None) -> Any:
                self.accessed.add(key)
                return default

            def __getitem__(self, key: str) -> Any:
                self.accessed.add(key)
                return ""

        tracker = _TrackingDict()
        assert callable(self.status)
        self.status(tracker)
        unknown = tracker.accessed - params
        if unknown:
            raise ValueError(
                f"Tool '{self.name}' status references unknown args: {unknown}. "
                f"Available: {params}"
            )

    def render_status(self, args: dict[str, Any]) -> str | None:
        if self.status is None:
            return None
        if callable(self.status):
            return self.status(args)
        return self.status

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
