"""Provider-neutral pipeline entry point for CarbKind AI."""

from pathlib import Path
from time import perf_counter

from pydantic import ValidationError

from src.agents.providers.base import (
    MealAnalysisProvider,
    ProviderResult,
    ProviderUnavailableError,
)
from src.agents.providers.registry import get_provider
from src.agents.schemas import (
    GuardrailResult,
    MealAnalysisResult,
    PipelineMetadata,
    SafetyResult,
)
from src.runtime.config import RuntimeConfig, load_config
from src.runtime.response_contract import (
    build_demo_response,
    build_failed_response,
    build_rejected_response,
    build_success_response,
    response_to_dict,
)


def _metadata(
    started_at: float,
    *,
    demo_mode: bool,
    provider_metadata: dict | None = None,
) -> PipelineMetadata:
    values = dict(provider_metadata or {})
    values.update(
        demo_mode=demo_mode,
        latency_seconds=perf_counter() - started_at,
    )
    return PipelineMetadata.model_validate(values)


def _failed_result(
    message: str,
    started_at: float,
    config: RuntimeConfig,
) -> dict:
    metadata = _metadata(started_at, demo_mode=config.demo_mode)
    return response_to_dict(build_failed_response(message, metadata=metadata))


def _validate_provider_result(
    provider: MealAnalysisProvider,
    result: ProviderResult,
    started_at: float,
) -> dict:
    """Validate raw provider payloads and build the public response contract."""
    demo_mode = provider.name == "demo"
    metadata = _metadata(
        started_at,
        demo_mode=demo_mode,
        provider_metadata=result.metadata,
    )

    guardrail = GuardrailResult.model_validate(result.guardrail)
    if demo_mode:
        meal_analysis = MealAnalysisResult.model_validate(result.meal_analysis)
        safety = SafetyResult.model_validate(result.safety)
        return response_to_dict(
            build_demo_response(
                meal_analysis,
                guardrail,
                safety,
                metadata=metadata,
            )
        )

    if not guardrail.passed:
        message = guardrail.blocked_reason or "This image could not be analyzed."
        return response_to_dict(
            build_rejected_response(
                message,
                guardrail=guardrail,
                metadata=metadata,
            )
        )

    meal_analysis = MealAnalysisResult.model_validate(result.meal_analysis)
    safety = SafetyResult.model_validate(result.safety)
    if not safety.passed and safety.revised_guidance:
        meal_analysis = meal_analysis.model_copy(
            update={"guidance": safety.revised_guidance}
        )
    elif not safety.passed:
        return response_to_dict(
            build_rejected_response(
                "The generated guidance did not pass safety review.",
                guardrail=guardrail,
                safety=safety,
                metadata=metadata,
            )
        )

    return response_to_dict(
        build_success_response(
            meal_analysis,
            guardrail,
            safety,
            metadata=metadata,
        )
    )


def _provider_failure_message(provider_name: str) -> str:
    if provider_name == "demo":
        return "Demo response could not be loaded."
    if provider_name == "qwen":
        return "Qwen local analysis is unavailable. Check the optional provider setup."
    return "Live analysis failed. Please try again or use the demo provider."


def analyze_meal_image(image_path: str) -> dict:
    """Analyze an image using the configured model provider."""
    started_at = perf_counter()
    config = load_config()

    if not image_path or not Path(image_path).is_file():
        return _failed_result(
            "Image path is missing or does not exist.", started_at, config
        )

    try:
        provider = get_provider(config)
    except ValueError:
        return _failed_result(
            "The configured model provider is not supported yet.",
            started_at,
            config,
        )

    if provider.name == "openai" and not config.openai_api_key:
        return _failed_result(
            "The OpenAI provider is not configured. Set OPENAI_API_KEY or use "
            "the demo provider.",
            started_at,
            config,
        )

    try:
        provider_result = provider.analyze(image_path)
        return _validate_provider_result(provider, provider_result, started_at)
    except ProviderUnavailableError as exc:
        return _failed_result(str(exc), started_at, config)
    except (OSError, ValidationError, TypeError, ValueError):
        return _failed_result(
            _provider_failure_message(provider.name), started_at, config
        )
    except Exception:
        return _failed_result(
            _provider_failure_message(provider.name),
            started_at,
            config,
        )
