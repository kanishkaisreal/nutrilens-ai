"""Runtime configuration for demo and live NutriLens modes."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


DEFAULT_GUARDRAIL_MODEL = "gpt-5-mini"
DEFAULT_MEAL_MODEL = "gpt-5-mini"
DEFAULT_SAFETY_MODEL = "gpt-5-mini"


@dataclass(frozen=True)
class RuntimeConfig:
    """Environment-backed settings used by the analysis pipeline."""

    demo_mode: bool
    openai_api_key: str | None
    guardrail_model: str
    meal_model: str
    safety_model: str


def _read_demo_mode(value: str | None) -> bool:
    """Default safely to demo mode unless live mode is explicitly requested."""
    if value is None:
        return True
    return value.strip().lower() not in {"0", "false", "no", "off"}


def load_config() -> RuntimeConfig:
    """Load runtime settings without logging secret values."""
    # Explicit process settings take precedence and keep tests isolated from local
    # files. A normal ``python app.py`` launch can still use a local .env file.
    if "DEMO_MODE" not in os.environ:
        load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    return RuntimeConfig(
        demo_mode=_read_demo_mode(os.getenv("DEMO_MODE")),
        openai_api_key=api_key or None,
        guardrail_model=os.getenv(
            "OPENAI_GUARDRAIL_MODEL", DEFAULT_GUARDRAIL_MODEL
        ).strip()
        or DEFAULT_GUARDRAIL_MODEL,
        meal_model=os.getenv("OPENAI_MEAL_MODEL", DEFAULT_MEAL_MODEL).strip()
        or DEFAULT_MEAL_MODEL,
        safety_model=os.getenv("OPENAI_SAFETY_MODEL", DEFAULT_SAFETY_MODEL).strip()
        or DEFAULT_SAFETY_MODEL,
    )
