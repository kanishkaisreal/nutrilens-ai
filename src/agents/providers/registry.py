"""Provider selection for the CarbKind AI analysis pipeline."""

from src.agents.providers.base import MealAnalysisProvider
from src.agents.providers.demo_provider import DemoProvider
from src.agents.providers.openai_provider import OpenAIProvider
from src.runtime.config import RuntimeConfig


def get_provider(config: RuntimeConfig) -> MealAnalysisProvider:
    """Return the configured provider or reject an unsupported backend."""
    if config.demo_mode or config.model_provider == "demo":
        return DemoProvider()
    if config.model_provider == "openai":
        return OpenAIProvider(config)

    # TODO: Add QwenProvider after provider contract and eval harness are stable.
    raise ValueError(f"Unsupported model provider: {config.model_provider}")
