"""Demo and live pipeline entry point for CarbKind AI."""

import json
from pathlib import Path
from time import perf_counter

from pydantic import ValidationError

from src.agents.openai_client import call_vision_json_model
from src.agents.prompts import (
    GUARDRAIL_PROMPT,
    MEAL_ANALYSIS_PROMPT,
    SAFETY_PROMPT,
)
from src.agents.schemas import (
    GuardrailResult,
    MealAnalysisResult,
    NutriLensResponse,
    PipelineMetadata,
    SafetyResult,
)
from src.runtime.config import RuntimeConfig, load_config
from src.runtime.response_contract import (
    build_failed_response,
    build_rejected_response,
    build_success_response,
    response_to_dict,
)


DEMO_OUTPUT_PATH = (
    Path(__file__).resolve().parents[2]
    / "examples"
    / "sample_outputs"
    / "demo_meal_output.json"
)


PROMPT_VERSIONS = {
    "guardrail": "v1",
    "meal_analysis": "v1",
    "safety": "v1",
}


def _metadata(
    config: RuntimeConfig,
    started_at: float,
    *,
    demo_mode: bool,
) -> PipelineMetadata:
    model_names = {}
    prompt_versions = {}
    if not demo_mode:
        model_names = {
            "guardrail": config.guardrail_model,
            "meal_analysis": config.meal_model,
            "safety": config.safety_model,
        }
        prompt_versions = PROMPT_VERSIONS
    return PipelineMetadata(
        demo_mode=demo_mode,
        latency_seconds=perf_counter() - started_at,
        model_names=model_names,
        prompt_versions=prompt_versions,
    )


def _failed_result(
    message: str,
    started_at: float,
    config: RuntimeConfig,
) -> dict:
    metadata = _metadata(config, started_at, demo_mode=config.demo_mode)
    return response_to_dict(build_failed_response(message, metadata=metadata))


def _run_demo_pipeline(started_at: float, config: RuntimeConfig) -> dict:
    """Return the existing deterministic demo response."""
    try:
        with DEMO_OUTPUT_PATH.open(encoding="utf-8") as demo_file:
            payload = json.load(demo_file)
        response = NutriLensResponse.model_validate(payload)
    except (OSError, json.JSONDecodeError, ValidationError, TypeError, ValueError):
        return _failed_result("Demo response could not be loaded.", started_at, config)

    response = response.model_copy(
        update={"metadata": _metadata(config, started_at, demo_mode=True)}
    )
    return response_to_dict(response)


def _run_live_pipeline(
    image_path: str,
    started_at: float,
    config: RuntimeConfig,
) -> dict:
    """Run guardrail, meal analysis, and safety review model calls."""
    guardrail = GuardrailResult.model_validate(
        call_vision_json_model(
            image_path,
            GUARDRAIL_PROMPT,
            config.guardrail_model,
        )
    )
    if not guardrail.passed:
        message = guardrail.blocked_reason or "This image could not be analyzed."
        response = build_rejected_response(
            message,
            guardrail=guardrail,
            metadata=_metadata(config, started_at, demo_mode=False),
        )
        return response_to_dict(response)

    meal_analysis = MealAnalysisResult.model_validate(
        call_vision_json_model(
            image_path,
            MEAL_ANALYSIS_PROMPT,
            config.meal_model,
        )
    )
    safety_review_prompt = (
        f"{SAFETY_PROMPT}\n\nMeal analysis to review:\n"
        f"{meal_analysis.model_dump_json(indent=2)}"
    )
    safety = SafetyResult.model_validate(
        call_vision_json_model(
            image_path,
            safety_review_prompt,
            config.safety_model,
        )
    )
    if not safety.passed and safety.revised_guidance:
        meal_analysis = meal_analysis.model_copy(
            update={"guidance": safety.revised_guidance}
        )
    elif not safety.passed:
        response = build_rejected_response(
            "The generated guidance did not pass safety review.",
            guardrail=guardrail,
            safety=safety,
            metadata=_metadata(config, started_at, demo_mode=False),
        )
        return response_to_dict(response)

    response = build_success_response(
        meal_analysis,
        guardrail,
        safety,
        metadata=_metadata(config, started_at, demo_mode=False),
    )
    return response_to_dict(response)


def analyze_meal_image(image_path: str) -> dict:
    """Analyze an image using the configured deterministic or live pipeline."""
    started_at = perf_counter()
    config = load_config()

    if not image_path or not Path(image_path).is_file():
        return _failed_result(
            "Image path is missing or does not exist.", started_at, config
        )

    if config.demo_mode:
        return _run_demo_pipeline(started_at, config)

    if not config.openai_api_key:
        return _failed_result(
            "Live mode is not configured. Set OPENAI_API_KEY or use demo mode.",
            started_at,
            config,
        )

    try:
        return _run_live_pipeline(image_path, started_at, config)
    except Exception:
        return _failed_result(
            "Live analysis failed. Please try again or use demo mode.",
            started_at,
            config,
        )
