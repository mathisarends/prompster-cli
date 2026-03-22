import json
import logging
from collections.abc import AsyncIterator

from llmify import ChatModel
from llmify.messages import (
    AssistantMessage,
    Message,
    SystemMessage,
    ToolResultMessage,
    UserMessage,
)

from prompster.agent.tools import Tools

logger = logging.getLogger(__name__)


class Agent:
    def __init__(
        self,
        instructions: str,
        llm: ChatModel,
    ) -> None:
        self._llm = llm
        self._system_prompt = instructions
        self._history: list[Message] = [SystemMessage(content=instructions)]
        self._mcp_ready = False
        self.tools = Tools()

    async def stream(self, user_input: str) -> AsyncIterator[str]:
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
                AssistantMessage(
                    content=response.completion, tool_calls=response.tool_calls
                )
            )

            for call in response.tool_calls:
                tool_args = json.loads(call.function.arguments)
                logger.debug(
                    "Calling tool '%s' with args: %s", call.function.name, tool_args
                )
                result = await self.tools.execute(call.function.name, tool_args)
                self._history.append(
                    ToolResultMessage(tool_call_id=call.id, content=result)
                )

    def reset(self) -> None:
        self._history = [SystemMessage(content=self._system_prompt)]
