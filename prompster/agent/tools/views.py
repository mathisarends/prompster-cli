from dataclasses import dataclass
from typing import Any, Protocol

from prompster.mcp.views import MCPToolCallResult


class MCPToolCaller(Protocol):
	async def call_tool(
		self, tool_name: str, arguments: dict[str, Any] | None
	) -> MCPToolCallResult: ...


@dataclass
class RegisteredTool:
	name: str
	description: str
	parameters: dict
	fn: Any


@dataclass
class RegisteredMCPTool:
	name: str
	description: str
	parameters: dict[str, Any]
	server: MCPToolCaller
