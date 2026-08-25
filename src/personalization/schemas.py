"""Future-ready schemas for consented meal memory and meal composition."""

from typing import Literal

from pydantic import BaseModel, Field


IngredientRole = Literal[
    "protein",
    "starch",
    "fiber_vegetable",
    "non_starchy_vegetable",
    "fruit",
    "fat",
    "acid",
    "sweetener",
    "aromatic",
    "herb_spice",
    "sauce",
    "dairy",
    "legume",
    "unknown",
]
CarbImpact = Literal["lower", "moderate", "higher", "unknown"]
PreferenceSignal = Literal["likes", "dislikes", "neutral", "unknown"]


class IngredientRoleEstimate(BaseModel):
    """Transparent functional-role estimate for one ingredient."""

    ingredient: str
    roles: list[IngredientRole]
    carb_impact: CarbImpact
    notes: str | None = None


class MealMemoryItem(BaseModel):
    """Summary of one meal explicitly consented for future personalization."""

    meal_id: str
    title: str
    ingredients: list[str]
    ingredient_roles: list[IngredientRoleEstimate] = Field(default_factory=list)
    estimated_carbs_g: float | None = None
    estimated_protein_g: float | None = None
    user_notes: str | None = None
    consented_for_personalization: bool = False


class PersonalMealProfile(BaseModel):
    """Portable profile schema; this module does not persist profile data."""

    profile_id: str
    common_ingredients: list[str] = Field(default_factory=list)
    common_carb_sources: list[str] = Field(default_factory=list)
    preferred_cuisines: list[str] = Field(default_factory=list)
    avoided_ingredients: list[str] = Field(default_factory=list)
    meal_memory: list[MealMemoryItem] = Field(default_factory=list)


class AvailableIngredient(BaseModel):
    """Ingredient available to a deterministic meal-composition request."""

    name: str
    quantity_hint: str | None = None
    roles: list[IngredientRole] = Field(default_factory=list)
    carb_impact: CarbImpact = "unknown"


class SubstitutionCandidate(BaseModel):
    """Interpretable ingredient replacement based on a shared function."""

    replace: str
    with_ingredient: str
    shared_role: IngredientRole
    reason: str
    carb_effect: CarbImpact = "unknown"


class MealComposerRequest(BaseModel):
    """Inputs for the storage-free, rule-based meal composer."""

    available_ingredients: list[AvailableIngredient]
    goal: str = "carb-aware balanced meal"
    cuisine_hint: str | None = None
    personal_profile: PersonalMealProfile | None = None


class MealComposerSuggestion(BaseModel):
    """Deterministic food idea with explicit limits and substitutions."""

    title: str
    selected_ingredients: list[str]
    substitutions: list[SubstitutionCandidate] = Field(default_factory=list)
    carb_watch: str
    preparation_idea: str
    safety_note: str = "Approximate food suggestion only. Not medical advice."
