from dataclasses import dataclass
from typing import Literal

from llmify import ChatModel

Provider = Literal["openai", "anthropic"]


@dataclass(frozen=True)
class _ModelInfo:
    key: str
    label: str
    provider: Provider
    model_id: str


MODELS: dict[str, _ModelInfo] = {
    "gpt-5.4": _ModelInfo(
        key="gpt-5.4",
        label="GPT-5.4",
        provider="openai",
        model_id="gpt-5.4",
    ),
    "gpt-5.4-mini": _ModelInfo(
        key="gpt-5.4-mini",
        label="GPT-5.4 Mini",
        provider="openai",
        model_id="gpt-5.4-mini",
    ),
    "claude-opus": _ModelInfo(
        key="claude-opus",
        label="Claude Opus 4.6",
        provider="anthropic",
        model_id="claude-opus-4-6",
    ),
    "claude-sonnet": _ModelInfo(
        key="claude-sonnet",
        label="Claude Sonnet 4.6",
        provider="anthropic",
        model_id="claude-sonnet-4-6",
    ),
    "claude-haiku": _ModelInfo(
        key="claude-haiku",
        label="Claude Haiku 4.5",
        provider="anthropic",
        model_id="claude-haiku-4-5-20251001",
    ),
}

_DEFAULT_MODEL_KEY = "gpt-5.4-mini"


def default_model_key() -> str:
    return _DEFAULT_MODEL_KEY


def create_llm(key: str) -> ChatModel:
    info = MODELS.get(key)
    if info is None:
        available = ", ".join(MODELS)
        raise ValueError(f"Unknown model '{key}'. Available: {available}")

    if info.provider == "openai":
        from llmify import ChatOpenAI

        return ChatOpenAI(model=info.model_id)

    if info.provider == "anthropic":
        from llmify import ChatAnthropic

        return ChatAnthropic(model=info.model_id)

    raise ValueError(f"Unsupported provider: {info.provider}")
