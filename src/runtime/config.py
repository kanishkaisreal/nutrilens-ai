"""Runtime configuration for demo and live CarbKind modes."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


DEFAULT_GUARDRAIL_MODEL = "gpt-5-mini"
DEFAULT_MEAL_MODEL = "gpt-5-mini"
DEFAULT_SAFETY_MODEL = "gpt-5-mini"
DEFAULT_MODEL_PROVIDER = "demo"
DEFAULT_QWEN_MODEL_ID = "Qwen/Qwen2.5-VL-3B-Instruct"
DEFAULT_QWEN_DEVICE = "auto"
SUPPORTED_MODEL_PROVIDERS = frozenset({"demo", "openai", "qwen"})


@dataclass(frozen=True)
class RuntimeConfig:
    """Environment-backed settings used by the analysis pipeline."""

    demo_mode: bool = True
    openai_api_key: str | None = None
    guardrail_model: str = DEFAULT_GUARDRAIL_MODEL
    meal_model: str = DEFAULT_MEAL_MODEL
    safety_model: str = DEFAULT_SAFETY_MODEL
    model_provider: str = DEFAULT_MODEL_PROVIDER
    qwen_model_id: str = DEFAULT_QWEN_MODEL_ID
    qwen_allow_local_inference: bool = False
    qwen_device: str = DEFAULT_QWEN_DEVICE


# Public compatibility name used by provider examples and lightweight scripts.
AppConfig = RuntimeConfig


def _read_demo_mode(value: str | None) -> bool:
    """Default safely to demo mode unless live mode is explicitly requested."""
    if value is None:
        return True
    return value.strip().lower() not in {"0", "false", "no", "off"}


def _read_enabled(value: str | None) -> bool:
    """Require an explicit truthy value for opt-in features."""
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def load_config() -> RuntimeConfig:
    """Load runtime settings without logging secret values."""
    # Explicit process settings take precedence and keep tests isolated from local
    # files. A normal ``python app.py`` launch can still use a local .env file.
    if "DEMO_MODE" not in os.environ:
        load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    requested_demo_mode = _read_demo_mode(os.getenv("DEMO_MODE"))
    model_provider = (
        os.getenv("MODEL_PROVIDER", DEFAULT_MODEL_PROVIDER).strip().lower()
    )
    model_provider = model_provider or DEFAULT_MODEL_PROVIDER
    return RuntimeConfig(
        demo_mode=requested_demo_mode or model_provider == "demo",
        model_provider=model_provider,
        openai_api_key=api_key or None,
        guardrail_model=os.getenv(
            "OPENAI_GUARDRAIL_MODEL", DEFAULT_GUARDRAIL_MODEL
        ).strip()
        or DEFAULT_GUARDRAIL_MODEL,
        meal_model=os.getenv("OPENAI_MEAL_MODEL", DEFAULT_MEAL_MODEL).strip()
        or DEFAULT_MEAL_MODEL,
        safety_model=os.getenv("OPENAI_SAFETY_MODEL", DEFAULT_SAFETY_MODEL).strip()
        or DEFAULT_SAFETY_MODEL,
        qwen_model_id=os.getenv("QWEN_MODEL_ID", DEFAULT_QWEN_MODEL_ID).strip()
        or DEFAULT_QWEN_MODEL_ID,
        qwen_allow_local_inference=_read_enabled(
            os.getenv("QWEN_ALLOW_LOCAL_INFERENCE")
        ),
        qwen_device=os.getenv("QWEN_DEVICE", DEFAULT_QWEN_DEVICE).strip()
        or DEFAULT_QWEN_DEVICE,
    )
