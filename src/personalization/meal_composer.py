"""Deterministic meal-composition prototype based on ingredient functions."""

from src.personalization.ingredient_roles import (
    infer_roles_for_ingredient,
    normalize_ingredient_name,
    suggest_functional_substitutions,
)
from src.personalization.schemas import (
    AvailableIngredient,
    IngredientRole,
    IngredientRoleEstimate,
    MealComposerRequest,
    MealComposerSuggestion,
    SubstitutionCandidate,
)


def _estimate_available(ingredient: AvailableIngredient) -> IngredientRoleEstimate:
    inferred = infer_roles_for_ingredient(ingredient.name)
    roles: list[IngredientRole] = []
    for role in [*ingredient.roles, *inferred.roles]:
        if role not in roles and (role != "unknown" or not roles):
            roles.append(role)
    if len(roles) > 1 and "unknown" in roles:
        roles.remove("unknown")
    return IngredientRoleEstimate(
        ingredient=ingredient.name,
        roles=roles or ["unknown"],
        carb_impact=(
            ingredient.carb_impact
            if ingredient.carb_impact != "unknown"
            else inferred.carb_impact
        ),
        notes=inferred.notes,
    )


def _names_with_role(
    estimates: list[IngredientRoleEstimate], role: IngredientRole
) -> list[str]:
    return [estimate.ingredient for estimate in estimates if role in estimate.roles]


def _first_distinct(values: list[str], excluded: set[str] | None = None) -> str | None:
    excluded = excluded or set()
    return next(
        (value for value in values if normalize_ingredient_name(value) not in excluded),
        None,
    )


def _join_foods(values: list[str]) -> str:
    if not values:
        return ""
    if len(values) == 1:
        return values[0]
    if len(values) == 2:
        return f"{values[0]} and {values[1]}"
    return f"{', '.join(values[:-1])}, and {values[-1]}"


def _primary_protein(estimates: list[IngredientRoleEstimate]) -> str | None:
    dairy = {
        normalize_ingredient_name(name)
        for name in _names_with_role(estimates, "dairy")
    }
    return _first_distinct(_names_with_role(estimates, "protein"), dairy)


def _compose_title(estimates: list[IngredientRoleEstimate]) -> str:
    protein = _primary_protein(estimates)
    vegetable = _first_distinct(
        _names_with_role(estimates, "non_starchy_vegetable")
    )
    starch = _first_distinct(_names_with_role(estimates, "starch"))
    parts = [part for part in (protein, vegetable, starch) if part]
    if not parts:
        return "Carb-aware meal idea"
    return f"Carb-aware {' '.join(parts)} bowl"


def _compose_carb_watch(estimates: list[IngredientRoleEstimate]) -> str:
    starch = _first_distinct(_names_with_role(estimates, "starch"))
    protein = _primary_protein(estimates)
    vegetable = _first_distinct(
        _names_with_role(estimates, "non_starchy_vegetable")
    )
    balance = _join_foods([name for name in (vegetable, protein) if name])
    if starch:
        suggestion = (
            f" Consider a smaller {starch} portion and add more {balance} for balance."
            if balance
            else f" Consider the {starch} portion in the context of the full meal."
        )
        return f"{starch.capitalize()} is the main likely carb source.{suggestion}"

    moderate = next(
        (
            estimate.ingredient
            for estimate in estimates
            if estimate.carb_impact in {"moderate", "higher"}
        ),
        None,
    )
    if moderate:
        return (
            f"{moderate.capitalize()} may contribute carbohydrates. Portion size "
            "and preparation can change the overall estimate."
        )
    return (
        "No obvious starch was identified by the small role map. Actual carbohydrate "
        "content still depends on ingredients and portions."
    )


def _compose_preparation(estimates: list[IngredientRoleEstimate]) -> str:
    starch = _first_distinct(_names_with_role(estimates, "starch"))
    protein = _primary_protein(estimates)
    vegetable = _first_distinct(
        _names_with_role(estimates, "non_starchy_vegetable")
    )
    aromatic = _first_distinct(_names_with_role(estimates, "aromatic"))
    dairy = _first_distinct(_names_with_role(estimates, "dairy"))
    acid = _first_distinct(
        _names_with_role(estimates, "acid"),
        {normalize_ingredient_name(dairy)} if dairy else None,
    )

    main = [name for name in (protein, vegetable, aromatic) if name]
    if starch:
        opening = f"Toss a smaller {starch} portion"
        if main:
            opening += f" with {_join_foods(main)}"
    elif main:
        opening = f"Combine {_join_foods(main)} in a simple bowl"
    else:
        opening = "Combine the available ingredients in a simple bowl"

    if dairy and acid:
        return f"{opening}, then add a {dairy} and {acid} sauce for acidity."
    if acid:
        return f"{opening}, then finish with {acid} for acidity."
    return f"{opening}. Adjust seasoning and portions to preference."


def _profile_substitutions(
    request: MealComposerRequest, selected_names: list[str]
) -> list[SubstitutionCandidate]:
    if request.personal_profile is None:
        return []
    substitutions = []
    for avoided in request.personal_profile.avoided_ingredients:
        substitutions.extend(
            suggest_functional_substitutions(avoided, selected_names)
        )
    return substitutions


def compose_meal(request: MealComposerRequest) -> MealComposerSuggestion:
    """Build a deterministic meal idea without a model call or data storage."""
    avoided = {
        normalize_ingredient_name(name)
        for name in (
            request.personal_profile.avoided_ingredients
            if request.personal_profile is not None
            else []
        )
    }
    selected = [
        ingredient
        for ingredient in request.available_ingredients
        if normalize_ingredient_name(ingredient.name) not in avoided
    ]
    estimates = [_estimate_available(ingredient) for ingredient in selected]
    selected_names = [ingredient.name for ingredient in selected]

    return MealComposerSuggestion(
        title=_compose_title(estimates),
        selected_ingredients=selected_names,
        substitutions=_profile_substitutions(request, selected_names),
        carb_watch=_compose_carb_watch(estimates),
        preparation_idea=_compose_preparation(estimates),
    )
