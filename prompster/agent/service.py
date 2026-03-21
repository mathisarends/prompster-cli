from __future__ import annotations

import json
import logging
from collections.abc import AsyncIterator

from llmify import BaseChatModel
from llmify.messages import (
    AssistantMessage,
    Message,
    SystemMessage,
    ToolCall,
    ToolResultMessage,
    UserMessage,
)

from prompster.agent.tools import ToolRegistry
from prompster.mcp import MCPServer

logger = logging.getLogger(__name__)


class Agent:
    def __init__(
        self,
        llm: BaseChatModel,
        system_prompt: str,
        mcp_server: MCPServer | None = None,
    ) -> None:
        self._llm = llm
        self._system_prompt = system_prompt
        self._mcp_server = mcp_server
        self._history: list[Message] = [SystemMessage(content=system_prompt)]
        self._mcp_ready = False
        self.tools = ToolRegistry()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        if self._mcp_server is not None:
            await self._mcp_server.cleanup()

    async def stream(self, user_input: str) -> AsyncIterator[str]:
        await self._ensure_mcp_ready()
        self._history.append(UserMessage(content=user_input))
        return self._loop()

    async def _loop(self) -> AsyncIterator[str]:
        schema = self.tools.to_schema() or None

        while True:
            response = await self._llm.invoke(self._history, tools=schema)

            if not response.tool_calls:
                self._history.append(AssistantMessage(content=response.completion))
                async for chunk in self._llm.stream(self._history):
                    yield chunk
                return

            self._history.append(
                AssistantMessage(content=response.completion, tool_calls=response.tool_calls)
            )

            for call in response.tool_calls:
                tool_args = json.loads(call.function.arguments)
                logger.debug("Calling tool '%s' with args: %s", call.function.name, tool_args)
                result = await self.tools.execute(call.function.name, tool_args)
                self._history.append(ToolResultMessage(tool_call_id=call.id, content=result))

    def reset(self) -> None:
        self._history = [SystemMessage(content=self._system_prompt)]

    async def _ensure_mcp_ready(self) -> None:
        if self._mcp_ready or self._mcp_server is None:
            return
        await self._mcp_server.connect()
        for tool in await self._mcp_server.list_tools():
            self.tools.register_mcp(tool, self._mcp_server)
        self._mcp_ready = True

