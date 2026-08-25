"""Public, storage-free personalization and meal-composition prototypes."""

from src.personalization.ingredient_roles import (
    infer_roles_for_ingredient,
    normalize_ingredient_name,
    suggest_functional_substitutions,
)
from src.personalization.meal_composer import compose_meal
from src.personalization.schemas import (
    AvailableIngredient,
    CarbImpact,
    IngredientRole,
    IngredientRoleEstimate,
    MealComposerRequest,
    MealComposerSuggestion,
    MealMemoryItem,
    PersonalMealProfile,
    PreferenceSignal,
    SubstitutionCandidate,
)

__all__ = [
    "AvailableIngredient",
    "CarbImpact",
    "IngredientRole",
    "IngredientRoleEstimate",
    "MealComposerRequest",
    "MealComposerSuggestion",
    "MealMemoryItem",
    "PersonalMealProfile",
    "PreferenceSignal",
    "SubstitutionCandidate",
    "compose_meal",
    "infer_roles_for_ingredient",
    "normalize_ingredient_name",
    "suggest_functional_substitutions",
]
