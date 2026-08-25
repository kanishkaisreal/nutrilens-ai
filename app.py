"""Gradio demo for the NutriLens AI response contract."""

from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

import gradio as gr
from PIL import Image

from src.agents.pipeline import analyze_meal_image


NUTRITION_LABELS = {
    "calories": ("Calories", "kcal"),
    "protein_g": ("Protein", "g"),
    "carbohydrates_g": ("Carbohydrates", "g"),
    "fat_g": ("Fat", "g"),
    "fiber_g": ("Fiber", "g"),
    "sugar_g": ("Sugar", "g"),
    "sodium_mg": ("Sodium", "mg"),
}


def _format_response(
    response: dict[str, Any],
) -> tuple[str, list[list[str]], list[list[str]], str, dict[str, Any]]:
    status = str(response.get("status", "failed"))
    message = str(response.get("message", "Analysis could not be completed."))

    if status in {"failed", "rejected", "retry_exhausted"}:
        summary = f"### Analysis {status.replace('_', ' ').title()}\n\n{message}"
        return summary, [], [], "Safety review not available.", response

    meal = response.get("meal_analysis") or {}
    summary_lines = [
        f"## {meal.get('title', 'Meal analysis')}",
        f"**Recommendation:** {str(meal.get('recommendation', 'unknown')).title()}",
        str(meal.get("description", "")),
        f"**Guidance:** {meal.get('guidance', '')}",
    ]
    if meal.get("uncertainty_notes"):
        summary_lines.append(f"**Uncertainty:** {meal['uncertainty_notes']}")

    nutrition = meal.get("estimated_nutrition") or {}
    nutrition_rows = []
    for field, (label, unit) in NUTRITION_LABELS.items():
        value = nutrition.get(field)
        estimate = "Not estimated" if value is None else f"{value:g} {unit}"
        nutrition_rows.append([label, estimate])

    ingredient_rows = [
        [
            str(ingredient.get("name", "")),
            str(ingredient.get("impact", "unknown")).title(),
            str(ingredient.get("notes") or ""),
        ]
        for ingredient in meal.get("ingredients", [])
    ]

    safety = response.get("safety") or {}
    safety_label = "Passed" if safety.get("passed") else "Needs review"
    safety_lines = [f"**Safety status:** {safety_label}"]
    if safety.get("reasons"):
        safety_lines.append("**Reasons:** " + "; ".join(safety["reasons"]))
    if safety.get("revised_guidance"):
        safety_lines.append(f"**Revised guidance:** {safety['revised_guidance']}")

    return (
        "\n\n".join(summary_lines),
        nutrition_rows,
        ingredient_rows,
        "\n\n".join(safety_lines),
        response,
    )


def analyze_meal(
    image: Image.Image | None,
) -> tuple[str, list[list[str]], list[list[str]], str, dict[str, Any]]:
    """Save the uploaded image temporarily and render the demo response."""
    if image is None:
        return _format_response(analyze_meal_image(""))

    temporary_path: Path | None = None
    try:
        with NamedTemporaryFile(suffix=".png", delete=False) as temporary_file:
            temporary_path = Path(temporary_file.name)
        image.save(temporary_path, format="PNG")
        response = analyze_meal_image(str(temporary_path))
    except (OSError, ValueError):
        response = analyze_meal_image("")
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return _format_response(response)


with gr.Blocks(title="NutriLens AI") as demo:
    gr.Markdown("# NutriLens AI")
    gr.Markdown(
        "Upload a meal image to get a structured, safety-reviewed nutrition "
        "estimate. The current pipeline returns a deterministic demo response."
    )
    gr.Markdown(
        "**Safety note:** Nutrition estimates are approximate and are not medical advice."
    )

    meal_image = gr.Image(type="pil", label="Meal image")
    analyze_button = gr.Button("Analyze", variant="primary")
    summary = gr.Markdown()

    with gr.Row():
        nutrition_table = gr.Dataframe(
            headers=["Nutrient", "Estimate"],
            label="Estimated nutrition",
            interactive=False,
        )
        ingredient_table = gr.Dataframe(
            headers=["Ingredient", "Impact", "Notes"],
            label="Estimated ingredients",
            interactive=False,
        )

    safety_status = gr.Markdown()
    raw_json = gr.JSON(label="Raw response")

    analyze_button.click(
        fn=analyze_meal,
        inputs=meal_image,
        outputs=[summary, nutrition_table, ingredient_table, safety_status, raw_json],
    )


if __name__ == "__main__":
    demo.launch()
