"""Show the public rule-based meal-composition prototype without API calls."""

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.personalization.meal_composer import compose_meal  # noqa: E402
from src.personalization.schemas import (  # noqa: E402
    AvailableIngredient,
    MealComposerRequest,
)


def main() -> None:
    request = MealComposerRequest(
        available_ingredients=[
            AvailableIngredient(name="pasta"),
            AvailableIngredient(name="greek yogurt"),
            AvailableIngredient(name="garlic"),
            AvailableIngredient(name="spinach"),
            AvailableIngredient(name="vinegar"),
            AvailableIngredient(name="chicken"),
        ],
        goal="carb-aware balanced meal",
    )
    suggestion = compose_meal(request)

    print(f"Title: {suggestion.title}")
    print(f"Selected ingredients: {', '.join(suggestion.selected_ingredients)}")
    if suggestion.substitutions:
        print("Substitutions:")
        for substitution in suggestion.substitutions:
            print(
                f"- {substitution.replace} → {substitution.with_ingredient} "
                f"({substitution.shared_role}): {substitution.reason}"
            )
    else:
        print("Substitutions: None needed for this request.")
    print(f"Carb watch: {suggestion.carb_watch}")
    print(f"Preparation idea: {suggestion.preparation_idea}")
    print(f"Safety note: {suggestion.safety_note}")


if __name__ == "__main__":
    main()
