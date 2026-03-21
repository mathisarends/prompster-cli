import logging
from typing import Any, Callable

from prompster.mcp.views import MCPToolDefinition
from prompster.agent.tools.views import (
    MCPToolCaller,
    RegisteredMCPTool,
    RegisteredTool,
)

logger = logging.getLogger(__name__)

Tool = Callable[..., Any]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, RegisteredTool] = {}
        self._mcp_tools: dict[str, RegisteredMCPTool] = {}

    def has(self, name: str) -> bool:
        return name in self._tools or name in self._mcp_tools

    def register(self, name: str, description: str, parameters: dict):
        def decorator(fn: Tool) -> Tool:
            self._tools[name] = RegisteredTool(
                name=name,
                description=description,
                parameters=parameters,
                fn=fn,
            )
            return fn
        return decorator

    def register_mcp(self, tool: MCPToolDefinition, server: MCPToolCaller) -> None:
        self._mcp_tools[tool.name] = RegisteredMCPTool(
            name=tool.name,
            description=tool.description or "",
            parameters={
                "type": "object",
                "properties": tool.inputSchema.properties,
                "required": tool.inputSchema.required,
            },
            server=server,
        )

    async def execute(self, name: str, args: dict) -> str:
        tool = self._tools.get(name)
        if tool is not None:
            try:
                result = await tool.fn(**args)
                return str(result)
            except Exception as e:
                logger.exception("Tool '%s' raised an exception", name)
                return f"Error: {e}"

        mcp_tool = self._mcp_tools.get(name)
        if mcp_tool is not None:
            try:
                result = await mcp_tool.server.call_tool(name, args)
                return result.unwrap()
            except Exception as e:
                logger.exception("MCP tool '%s' raised an exception", name)
                return f"Error: {e}"

        raise ValueError(
            f"Unknown tool '{name}'. Available: {list(self._tools) + list(self._mcp_tools)}"
        )

    def to_schema(self) -> list[dict]:
        local_tools = [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in self._tools.values()
        ]
        mcp_tools = [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.parameters,
                },
            }
            for t in self._mcp_tools.values()
        ]
        return local_tools + mcp_tools