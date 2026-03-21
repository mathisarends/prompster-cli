import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".prompster"
CONFIG_FILE = CONFIG_DIR / "config.json"

MODELS = {
    "claude-sonnet-4-6": {"name": "Sonnet 4.6", "provider": "Anthropic", "description": "Fast & capable"},
    "claude-opus-4-6": {"name": "Opus 4.6", "provider": "Anthropic", "description": "Most intelligent"},
    "gpt-4o": {"name": "GPT-4o", "provider": "OpenAI", "description": "Multimodal flagship"},
    "gpt-4o-mini": {"name": "GPT-4o Mini", "provider": "OpenAI", "description": "Fast & affordable"},
}

DEFAULT_MODEL = "claude-sonnet-4-6"


def _load_config() -> dict:
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return {}


def _save_config(cfg: dict) -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


def get_model() -> str:
    return _load_config().get("model", DEFAULT_MODEL)


def set_model(model_id: str) -> None:
    cfg = _load_config()
    cfg["model"] = model_id
    _save_config(cfg)
