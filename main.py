from llmify import ChatOpenAI
from llmify.messages import UserMessage

from dotenv import load_dotenv
load_dotenv(override=True)


async def main():
    model = ChatOpenAI(model="gpt-4o-mini")

    result = await model.invoke(messages=[
        UserMessage(content="What is the capital of France?")
    ])

    print(result.completion)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
