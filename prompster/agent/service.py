import json
import logging

from llmify import BaseChatModel
from llmify.messages import AssistantMessage, SystemMessage, ToolResultMessage, UserMessage

from prompster.agent.tools import ToolRegistry
from prompster.agent.views import AgentResult
from prompster.mcp import MCPServer

logger = logging.getLogger(__name__)



class HitsterAgent:
    def __init__(
        self,
        llm: BaseChatModel,
        system_prompt: str,
        max_iterations: int = 10,
        mcp_server: MCPServer | None = None,
    ) -> None:
        self._llm = llm
        self._system_prompt = system_prompt
        self._max_iterations = max_iterations
        self._mcp_server = mcp_server
        self.tools = ToolRegistry()

    async def _load_mcp_tools(self) -> None:
        if self._mcp_server is None:
            return

        await self._mcp_server.connect()
        mcp_tools = await self._mcp_server.list_tools()
        for tool in mcp_tools:
            self.tools.register_mcp(tool, self._mcp_server)

    async def run(self, task: str) -> AgentResult:
        await self._load_mcp_tools()

        messages = [
            SystemMessage(content=self._system_prompt),
            UserMessage(content=task),
        ]

        try:
            for iteration in range(self._max_iterations):
                logger.debug("Iteration %d", iteration + 1)

                response = await self._llm.invoke(messages, tools=self.tools.to_schema())

                if not response.tool_calls:
                    return AgentResult(
                        message=response.completion,
                        success=True,
                    )

                messages.append(
                    AssistantMessage(
                        content=response.completion,
                        tool_calls=response.tool_calls,
                    )
                )

                for call in response.tool_calls:
                    tool_name = call.function.name
                    tool_args = json.loads(call.function.arguments)

                    logger.debug("Calling tool '%s' with args: %s", tool_name, tool_args)

                    if not self.tools.has(tool_name):
                        result = f"Error: Unknown tool '{tool_name}'."
                    else:
                        result = await self.tools.execute(tool_name, tool_args)

                    messages.append(
                        ToolResultMessage(tool_call_id=call.id, content=result)
                    )

            return AgentResult(
                message="Max iterations reached without a final answer.",
                success=False,
            )
        finally:
            if self._mcp_server is not None:
                await self._mcp_server.cleanup()