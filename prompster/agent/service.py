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

    @property
    def llm(self) -> ChatModel:
        return self._llm

    @llm.setter
    def llm(self, value: ChatModel) -> None:
        self._llm = value

    async def run(self, user_input: str) -> AsyncIterator[StreamEvent]:
        self._history.append(UserMessage(content=user_input))
        schema = self.tools.to_schema() or None

        while True:
            response = await self._llm.invoke(self._history, tools=schema)

            if not response.tool_calls:
                content = response.completion or ""
                self._history.append(AssistantMessage(content=content))
                yield content
                return

            self._history.append(
                AssistantMessage(content=None, tool_calls=response.tool_calls)
            )

            for call in response.tool_calls:
                tool = self.tools.get(call.function.name)
                tool_args = json.loads(call.function.arguments)
                yield ToolCallEvent(
                    tool_name=call.function.name,
                    status=tool.render_status(tool_args) if tool else None,
                )
                result = await self.tools.execute(call.function.name, tool_args)
                self._history.append(
                    ToolResultMessage(tool_call_id=call.id, content=result)
                )

    def reset(self) -> None:
        self._history = [SystemMessage(content=self._system_prompt)]
