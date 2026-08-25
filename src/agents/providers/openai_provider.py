"""OpenAI-backed implementation of the three-step analysis flow."""

from src.agents.openai_client import call_vision_json_model
from src.agents.prompts import (
    GUARDRAIL_PROMPT,
    MEAL_ANALYSIS_PROMPT,
    SAFETY_PROMPT,
)
from src.agents.providers.base import ProviderResult
from src.agents.schemas import GuardrailResult, MealAnalysisResult
from src.runtime.config import RuntimeConfig


PROMPT_VERSIONS = {
    "guardrail": "v1",
    "meal_analysis": "v1",
    "safety": "v1",
}


class OpenAIProvider:
    """Run guardrail, analysis, and safety steps through the live backend."""

    name = "openai"

    def __init__(self, config: RuntimeConfig) -> None:
        self._config = config

    def _metadata(self) -> dict:
        return {
            "demo_mode": False,
            "model_names": {
                "guardrail": self._config.guardrail_model,
                "meal_analysis": self._config.meal_model,
                "safety": self._config.safety_model,
            },
            "prompt_versions": PROMPT_VERSIONS,
        }

    def analyze(self, image_path: str) -> ProviderResult:
        guardrail = call_vision_json_model(
            image_path,
            GUARDRAIL_PROMPT,
            self._config.guardrail_model,
        )
        validated_guardrail = GuardrailResult.model_validate(guardrail)
        if not validated_guardrail.passed:
            return ProviderResult(
                guardrail=guardrail,
                meal_analysis=None,
                safety=None,
                metadata=self._metadata(),
            )

        meal_analysis = call_vision_json_model(
            image_path,
            MEAL_ANALYSIS_PROMPT,
            self._config.meal_model,
        )
        validated_meal = MealAnalysisResult.model_validate(meal_analysis)
        safety_review_prompt = (
            f"{SAFETY_PROMPT}\n\nMeal analysis to review:\n"
            f"{validated_meal.model_dump_json(indent=2)}"
        )
        safety = call_vision_json_model(
            image_path,
            safety_review_prompt,
            self._config.safety_model,
        )
        return ProviderResult(
            guardrail=guardrail,
            meal_analysis=meal_analysis,
            safety=safety,
            metadata=self._metadata(),
        )
