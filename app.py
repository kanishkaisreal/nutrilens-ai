"""Polished Gradio demo for the NutriLens AI response contract."""

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

RECOMMENDATION_BADGES = {
    "green": "🟢 Green",
    "yellow": "🟡 Yellow",
    "orange": "🟠 Orange",
    "red": "🔴 Red",
    "unknown": "⚪ Unknown",
}

UIOutput = tuple[
    str,
    str,
    str,
    str,
    list[list[str]],
    list[list[str]],
    dict[str, Any],
]


def recommendation_badge(label: str | None) -> str:
    """Return a readable recommendation label with a status emoji."""
    normalized_label = str(label or "unknown").lower()
    return RECOMMENDATION_BADGES.get(normalized_label, RECOMMENDATION_BADGES["unknown"])


def format_nutrition_table(meal_analysis: dict[str, Any]) -> list[list[str]]:
    """Format available nutrition estimates for a Gradio table."""
    nutrition = meal_analysis.get("estimated_nutrition") or {}
    rows: list[list[str]] = []

    for field, (label, unit) in NUTRITION_LABELS.items():
        value = nutrition.get(field)
        if value is None:
            continue
        formatted_value = f"{value:g}" if isinstance(value, (int, float)) else str(value)
        rows.append([label, f"{formatted_value} {unit}"])

    return rows


def format_ingredients_table(meal_analysis: dict[str, Any]) -> list[list[str]]:
    """Format estimated ingredients for a Gradio table."""
    return [
        [
            str(ingredient.get("name", "")),
            recommendation_badge(ingredient.get("impact")),
            str(ingredient.get("notes") or ""),
        ]
        for ingredient in meal_analysis.get("ingredients", [])
    ]


def format_summary_markdown(result: dict[str, Any]) -> str:
    """Build the primary meal summary or a clear error state."""
    status = str(result.get("status", "failed"))
    message = str(result.get("message", "Analysis could not be completed."))

    if status == "rejected":
        return f"## Request rejected\n\n{message}"
    if status in {"failed", "retry_exhausted"}:
        return f"## Analysis unavailable\n\n{message}"

    meal_analysis = result.get("meal_analysis") or {}
    lines = [
        f"## {meal_analysis.get('title', 'Meal analysis')}",
        str(meal_analysis.get("description", "")),
        f"**Guidance:** {meal_analysis.get('guidance', '')}",
    ]
    if meal_analysis.get("uncertainty_notes"):
        lines.append(f"**Uncertainty:** {meal_analysis['uncertainty_notes']}")
    return "\n\n".join(lines)


def format_safety_markdown(result: dict[str, Any]) -> str:
    """Summarize safety and guardrail details when available."""
    status = str(result.get("status", "failed"))
    safety = result.get("safety") or {}
    guardrail = result.get("guardrail") or {}

    if status in {"failed", "retry_exhausted"}:
        return "### Safety status\n\nSafety review was not completed."

    if safety.get("passed"):
        lines = ["### ✅ Safety check passed"]
    elif safety:
        lines = ["### ⚠️ Safety review flagged this output"]
    else:
        lines = ["### Safety status\n\nSafety review was not available."]

    if status == "rejected" and guardrail:
        blocked_reason = guardrail.get("blocked_reason")
        guardrail_detail = blocked_reason or "Input did not pass validation."
        lines.append(f"**Guardrail:** {guardrail_detail}")
    if safety.get("reasons"):
        lines.append("**Reasons:** " + "; ".join(safety["reasons"]))
    if safety.get("revised_guidance"):
        lines.append(f"**Revised guidance:** {safety['revised_guidance']}")

    return "\n\n".join(lines)


def format_run_metadata(result: dict[str, Any]) -> str:
    """Display demo/live mode and measured latency."""
    metadata = result.get("metadata") or {}
    mode = "🧪 Demo mode" if metadata.get("demo_mode") else "⚡ Live mode"
    lines = [f"**Mode:** {mode}"]

    latency = metadata.get("latency_seconds")
    if isinstance(latency, (int, float)):
        latency_text = (
            f"{latency * 1000:.1f} ms" if latency < 1 else f"{latency:.2f} seconds"
        )
        lines.append(f"**Latency:** {latency_text}")

    return "  \n".join(lines)


def _ui_failure(message: str) -> dict[str, Any]:
    """Create a pipeline-shaped failure with a user-friendly UI message."""
    result = analyze_meal_image("")
    result["message"] = message
    return result


def _format_ui_output(result: dict[str, Any]) -> UIOutput:
    """Prepare a structured response for all Gradio output components."""
    status = str(result.get("status", "failed"))
    meal_analysis = result.get("meal_analysis") or {}
    badge = (
        recommendation_badge(meal_analysis.get("recommendation"))
        if status in {"demo", "success"}
        else "Not available"
    )

    return (
        format_summary_markdown(result),
        f"### Recommendation\n\n{badge}",
        format_safety_markdown(result),
        format_run_metadata(result),
        format_nutrition_table(meal_analysis),
        format_ingredients_table(meal_analysis),
        result,
    )


def run_ui_analysis(image: Image.Image | None) -> UIOutput:
    """Analyze an uploaded image and remove its temporary file afterward."""
    if image is None:
        return _format_ui_output(
            _ui_failure("Please upload a meal image before selecting Analyze Meal.")
        )

    temporary_path: Path | None = None
    try:
        with NamedTemporaryFile(suffix=".png", delete=False) as temporary_file:
            temporary_path = Path(temporary_file.name)
        image.save(temporary_path, format="PNG")
        result = analyze_meal_image(str(temporary_path))
    except (OSError, ValueError):
        result = _ui_failure(
            "The uploaded image could not be processed. Please try another image."
        )
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return _format_ui_output(result)


with gr.Blocks(title="NutriLens AI") as demo:
    gr.Markdown("# NutriLens AI 🥗")
    gr.Markdown(
        "Upload a meal image and get a structured, safety-reviewed nutrition estimate."
    )
    gr.Markdown(
        "> **Safety note:** Nutrition estimates are approximate and are not medical advice."
    )

    with gr.Row(equal_height=False):
        with gr.Column(scale=2, min_width=300):
            meal_image = gr.Image(type="pil", label="Meal image", height=360)
            analyze_button = gr.Button("Analyze Meal", variant="primary")
            gr.Markdown("*Demo mode can run without an API key.*")
            gr.Markdown(
                "Demo mode returns a sample structured meal analysis so the app can "
                "be tried without an API key. Live model mode will be added next."
            )

        with gr.Column(scale=3, min_width=360):
            meal_summary = gr.Markdown(
                "## Meal summary\n\nUpload a meal image to view the demo analysis."
            )
            with gr.Row():
                recommendation = gr.Markdown("### Recommendation\n\nNot available")
                run_metadata = gr.Markdown("**Mode:** 🧪 Demo mode")
            safety_status = gr.Markdown(
                "### Safety status\n\nSafety review has not run yet."
            )

    with gr.Row(equal_height=False):
        with gr.Column(scale=2):
            nutrition_table = gr.Dataframe(
                headers=["Metric", "Estimate"],
                label="Nutrition estimate",
                interactive=False,
            )
        with gr.Column(scale=3):
            ingredient_table = gr.Dataframe(
                headers=["Ingredient", "Impact", "Notes"],
                label="Estimated ingredients",
                interactive=False,
            )

    with gr.Accordion("Raw structured response", open=False):
        raw_json = gr.JSON(label="Raw JSON")

    analyze_button.click(
        fn=run_ui_analysis,
        inputs=meal_image,
        outputs=[
            meal_summary,
            recommendation,
            safety_status,
            run_metadata,
            nutrition_table,
            ingredient_table,
            raw_json,
        ],
    )


if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft())
