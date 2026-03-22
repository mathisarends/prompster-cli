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
from prompster.agent.views import StreamEvent, ToolCallEvent

logger = logging.getLogger(__name__)


class Agent:
    def __init__(
        self, instructions: str, llm: ChatModel, tools: Tools | None = None
    ) -> None:
        self._llm = llm
        self._system_prompt = instructions
        self.tools = tools or Tools()
        self._history: list[Message] = [SystemMessage(content=instructions)]

    async def run(self, user_input: str) -> AsyncIterator[StreamEvent]:
        self._history.append(UserMessage(content=user_input))
        schema = self.tools.to_schema() or None

        while True:
            response = await self._llm.invoke(self._history, tools=schema)

            if not response.tool_calls:
                break

            self._history.append(
                AssistantMessage(
                    content=response.completion, tool_calls=response.tool_calls
                )
            )

            for call in response.tool_calls:
                tool = self.tools.get(call.function.name)
                yield ToolCallEvent(
                    tool_name=call.function.name,
                    status=tool.status,
                )

                tool_args = json.loads(call.function.arguments)
                result = await self.tools.execute(call.function.name, tool_args)
                self._history.append(
                    ToolResultMessage(tool_call_id=call.id, content=result)
                )

        chunks: list[str] = []
        async for chunk in self._llm.stream(self._history, tools=schema):
            chunks.append(chunk)
            yield chunk

        self._history.append(AssistantMessage(content="".join(chunks)))

    def reset(self) -> None:
        self._history = [SystemMessage(content=self._system_prompt)]
