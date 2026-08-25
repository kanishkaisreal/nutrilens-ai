"""Public response models for the NutriLens AI pipeline."""

from typing import Literal

from pydantic import BaseModel, Field


RecommendationLabel = Literal["green", "yellow", "orange", "red", "unknown"]
IngredientImpact = Literal["green", "yellow", "orange", "red", "unknown"]
PipelineStatus = Literal["success", "rejected", "failed", "retry_exhausted", "demo"]


class NutritionEstimate(BaseModel):
    """Approximate nutrition inferred from a meal image."""

    calories: float | None
    protein_g: float | None
    carbohydrates_g: float | None
    fat_g: float | None
    fiber_g: float | None = None
    sugar_g: float | None = None
    sodium_mg: float | None = None


class IngredientEstimate(BaseModel):
    """A visually estimated ingredient and its dietary impact."""

    name: str
    impact: IngredientImpact
    notes: str | None = None


class GuardrailResult(BaseModel):
    """Input validation completed before meal analysis."""

    passed: bool
    is_valid_image: bool
    is_food: bool
    blocked_reason: str | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)


class MealAnalysisResult(BaseModel):
    """The primary user-facing meal analysis."""

    title: str
    description: str
    recommendation: RecommendationLabel
    estimated_nutrition: NutritionEstimate
    ingredients: list[IngredientEstimate]
    guidance: str
    uncertainty_notes: str | None = None


class SafetyResult(BaseModel):
    """Safety review of generated user-facing guidance."""

    passed: bool
    reasons: list[str] = Field(default_factory=list)
    revised_guidance: str | None = None


class PipelineMetadata(BaseModel):
    """Operational metadata attached to a pipeline response."""

    demo_mode: bool = False
    latency_seconds: float | None = None
    model_names: dict[str, str] = Field(default_factory=dict)
    prompt_versions: dict[str, str] = Field(default_factory=dict)


class NutriLensResponse(BaseModel):
    """Top-level response returned by NutriLens AI."""

    status: PipelineStatus
    message: str
    guardrail: GuardrailResult | None = None
    meal_analysis: MealAnalysisResult | None = None
    safety: SafetyResult | None = None
    metadata: PipelineMetadata = Field(default_factory=PipelineMetadata)
