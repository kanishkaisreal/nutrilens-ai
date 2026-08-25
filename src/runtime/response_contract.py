"""Helpers for constructing consistent CarbKind AI responses."""

from src.agents.schemas import (
    CarbKindResponse,
    GuardrailResult,
    MealAnalysisResult,
    PipelineMetadata,
    SafetyResult,
)


def _metadata_or_default(metadata: PipelineMetadata | None) -> PipelineMetadata:
    return metadata if metadata is not None else PipelineMetadata()


def build_success_response(
    meal_analysis: MealAnalysisResult,
    guardrail: GuardrailResult,
    safety: SafetyResult,
    metadata: PipelineMetadata | None = None,
    message: str = "Meal analysis completed successfully.",
) -> CarbKindResponse:
    """Build a successful live-pipeline response."""
    return CarbKindResponse(
        status="success",
        message=message,
        guardrail=guardrail,
        meal_analysis=meal_analysis,
        safety=safety,
        metadata=_metadata_or_default(metadata),
    )


def build_rejected_response(
    message: str,
    guardrail: GuardrailResult | None = None,
    safety: SafetyResult | None = None,
    metadata: PipelineMetadata | None = None,
) -> CarbKindResponse:
    """Build a response for input or output rejected by a safety gate."""
    return CarbKindResponse(
        status="rejected",
        message=message,
        guardrail=guardrail,
        safety=safety,
        metadata=_metadata_or_default(metadata),
    )


def build_failed_response(
    message: str,
    metadata: PipelineMetadata | None = None,
) -> CarbKindResponse:
    """Build a response for an unrecoverable pipeline error."""
    return CarbKindResponse(
        status="failed",
        message=message,
        metadata=_metadata_or_default(metadata),
    )


def build_demo_response(
    meal_analysis: MealAnalysisResult,
    guardrail: GuardrailResult,
    safety: SafetyResult,
    metadata: PipelineMetadata | None = None,
    message: str = "Demo meal analysis loaded.",
) -> CarbKindResponse:
    """Build a deterministic demo response without a model call."""
    demo_metadata = _metadata_or_default(metadata).model_copy(
        update={"demo_mode": True}
    )
    return CarbKindResponse(
        status="demo",
        message=message,
        guardrail=guardrail,
        meal_analysis=meal_analysis,
        safety=safety,
        metadata=demo_metadata,
    )


def response_to_dict(response: CarbKindResponse) -> dict:
    """Convert a response to a plain dictionary across Pydantic versions."""
    if hasattr(response, "model_dump"):
        return response.model_dump(mode="json")
    return response.dict()
