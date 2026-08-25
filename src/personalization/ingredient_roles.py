"""Small, interpretable ingredient-role and substitution prototype."""

import re

from src.personalization.schemas import (
    CarbImpact,
    IngredientRole,
    IngredientRoleEstimate,
    SubstitutionCandidate,
)


# This transparent map is intentionally small and is not a nutrition database.
ROLE_INGREDIENTS: dict[IngredientRole, tuple[str, ...]] = {
    "protein": (
        "chicken",
        "eggs",
        "tofu",
        "paneer",
        "greek yogurt",
        "lentils",
    ),
    "starch": ("rice", "pasta", "bread", "potato", "tortilla", "oats"),
    "fiber_vegetable": (
        "spinach",
        "cucumber",
        "broccoli",
        "cauliflower",
        "mixed greens",
        "zucchini",
    ),
    "non_starchy_vegetable": (
        "spinach",
        "cucumber",
        "broccoli",
        "cauliflower",
        "mixed greens",
        "zucchini",
    ),
    "fruit": ("berries", "apple", "orange"),
    "fat": ("olive oil", "avocado", "nuts", "seeds"),
    "acid": (
        "lemon",
        "lime",
        "vinegar",
        "tamarind",
        "unsweetened yogurt",
        "greek yogurt",
        "yogurt",
    ),
    "sweetener": ("sugar", "honey", "syrup"),
    "aromatic": ("garlic", "onion", "ginger"),
    "herb_spice": ("basil", "cilantro", "parsley", "cumin", "pepper"),
    "sauce": ("tomato sauce", "pesto", "tahini"),
    "dairy": ("milk", "cheese", "paneer", "greek yogurt", "yogurt"),
    "legume": ("lentils", "beans", "chickpeas"),
    "unknown": (),
}


def normalize_ingredient_name(name: str) -> str:
    """Normalize spacing and punctuation for transparent rule matching."""
    normalized = re.sub(r"[^a-z0-9]+", " ", str(name).strip().lower())
    return " ".join(normalized.split())


def _contains_ingredient(normalized_name: str, known_ingredient: str) -> bool:
    return f" {known_ingredient} " in f" {normalized_name} "


def _carb_impact_for_roles(roles: list[IngredientRole]) -> CarbImpact:
    if "starch" in roles or "sweetener" in roles:
        return "higher"
    if any(role in roles for role in ("fruit", "dairy", "legume")):
        return "moderate"
    if roles and roles != ["unknown"]:
        return "lower"
    return "unknown"


def infer_roles_for_ingredient(name: str) -> IngredientRoleEstimate:
    """Infer functional roles using only the public prototype taxonomy."""
    normalized = normalize_ingredient_name(name)
    roles: list[IngredientRole] = []
    for role, known_ingredients in ROLE_INGREDIENTS.items():
        if any(
            _contains_ingredient(normalized, ingredient)
            for ingredient in known_ingredients
        ):
            roles.append(role)

    if not roles:
        roles = ["unknown"]
        notes = "No match in the small prototype role map."
    else:
        notes = "Matched by the small, interpretable prototype role map."
    return IngredientRoleEstimate(
        ingredient=name,
        roles=roles,
        carb_impact=_carb_impact_for_roles(roles),
        notes=notes,
    )


def suggest_functional_substitutions(
    missing_ingredient: str,
    available_ingredients: list[str],
) -> list[SubstitutionCandidate]:
    """Suggest available ingredients that share a known functional role."""
    missing = infer_roles_for_ingredient(missing_ingredient)
    known_missing_roles = [role for role in missing.roles if role != "unknown"]
    if not known_missing_roles:
        return []

    normalized_missing = normalize_ingredient_name(missing_ingredient)
    suggestions: list[SubstitutionCandidate] = []
    seen: set[str] = set()
    for available in available_ingredients:
        normalized_available = normalize_ingredient_name(available)
        if not normalized_available or normalized_available == normalized_missing:
            continue
        candidate = infer_roles_for_ingredient(available)
        shared_role = next(
            (role for role in known_missing_roles if role in candidate.roles),
            None,
        )
        if shared_role is None or normalized_available in seen:
            continue
        seen.add(normalized_available)
        readable_role = shared_role.replace("_", " ")
        suggestions.append(
            SubstitutionCandidate(
                replace=missing_ingredient,
                with_ingredient=available,
                shared_role=shared_role,
                reason=(
                    f"Both ingredients can provide a {readable_role} role in "
                    "this prototype."
                ),
                carb_effect=candidate.carb_impact,
            )
        )
    return suggestions
