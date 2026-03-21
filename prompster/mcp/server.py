import abc
import asyncio
import json
import logging
from typing import Any

from pydantic import BaseModel

from prompster.mcp.views import (
    ClientInfo,
    InitializeParams,
    JsonRpcNotification,
    JsonRpcRequest,
    JsonRpcResponse,
    MCPToolCallResult,
    MCPToolDefinition,
    MCPToolsListResult,
)

logger = logging.getLogger(__name__)


class MCPServer(abc.ABC):
    @abc.abstractmethod
    async def connect(self): ...

    @abc.abstractmethod
    async def cleanup(self): ...

    @abc.abstractmethod
    async def list_tools(self) -> list[MCPToolDefinition]: ...

    @abc.abstractmethod
    async def call_tool(self, tool_name: str, arguments: dict[str, Any] | None) -> MCPToolCallResult: ...

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        await self.cleanup()


class MCPServerStdio(MCPServer):
    def __init__(
        self,
        command: str,
        args: list[str] | None = None,
        env: dict[str, str] | None = None,
        cache_tools_list: bool = True,
        allowed_tools: list[str] | None = None,
    ):
        self._command = command
        self._args = args or []
        self._env = env
        self._cache_tools_list = cache_tools_list
        self._allowed_tools: set[str] | None = set(allowed_tools) if allowed_tools is not None else None
        self._process: asyncio.subprocess.Process | None = None
        self._msg_id = 0
        self._tools_cache: list[MCPToolDefinition] | None = None

    async def connect(self) -> None:
        if self._process is not None:
            await self.cleanup()

        self._process = await asyncio.create_subprocess_exec(
            self._command,
            *self._args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=self._env,
        )

        await self._request(
            "initialize",
            InitializeParams(clientInfo=ClientInfo(name="prompster", version="0.1.0")).model_dump(),
        )
        await self._notify("notifications/initialized")

    async def list_tools(self) -> list[MCPToolDefinition]:
        if self._cache_tools_list and self._tools_cache is not None:
            return self._tools_cache

        result = await self._request("tools/list", {})
        tools = MCPToolsListResult.model_validate(result).tools

        if self._allowed_tools is not None:
            tools = [t for t in tools if t.name in self._allowed_tools]

        self._tools_cache = tools
        return tools

    async def call_tool(self, tool_name: str, arguments: dict[str, Any] | None = None) -> MCPToolCallResult:
        result = await self._request("tools/call", {"name": tool_name, "arguments": arguments or {}})
        return MCPToolCallResult.model_validate(result)

    async def cleanup(self) -> None:
        if self._process:
            self._process.terminate()
            await self._process.wait()
            self._process = None
            self._tools_cache = None
            self._msg_id = 0

    def _next_id(self) -> int:
        self._msg_id += 1
        return self._msg_id

    async def _send(self, message: BaseModel) -> None:
        assert self._process and self._process.stdin
        self._process.stdin.write((message.model_dump_json() + "\n").encode())
        await self._process.stdin.drain()

    async def _recv(self) -> JsonRpcResponse:
        assert self._process and self._process.stdout
        while True:
            line = await self._process.stdout.readline()
            if not line:
                stderr_output = await self._process.stderr.read() if self._process.stderr else b""
                raise RuntimeError(f"MCP server process exited unexpectedly.\nSTDERR: {stderr_output.decode()}")
            line = line.strip()
            if not line:
                continue
            try:
                return JsonRpcResponse.model_validate_json(line)
            except (json.JSONDecodeError, ValueError):
                logger.debug("MCP server non-JSON stdout: %s", line.decode())
                continue

    async def _request(self, method: str, params: dict) -> dict:
        msg_id = self._next_id()
        await self._send(JsonRpcRequest(id=msg_id, method=method, params=params))
        while True:
            response = await self._recv()
            if response.id == msg_id:
                return response.unwrap()

    async def _notify(self, method: str, params: dict | None = None) -> None:
        await self._send(JsonRpcNotification(method=method, params=params))