"""Consumer-friendly Gradio demo for CarbKind AI."""

from html import escape
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

import gradio as gr
from PIL import Image

from src.agents.pipeline import analyze_meal_image
from src.runtime.config import load_config


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
    "green": "🟢 Lower-carb / balanced",
    "yellow": "🟡 Moderate carb",
    "orange": "🟠 Higher carb",
    "red": "🔴 Very high carb / caution",
    "unknown": "⚪ Unknown",
}

INGREDIENT_IMPACT_BADGES = {
    "green": "🟢 Lower",
    "yellow": "🟡 Moderate",
    "orange": "🟠 Higher",
    "red": "🔴 Highest",
    "unknown": "⚪ Unknown",
}

CARB_DESCRIPTIONS = {
    "green": "lower in carbohydrates or balanced",
    "yellow": "moderate in carbohydrates",
    "orange": "higher in carbohydrates",
    "red": "very high in carbohydrates",
    "unknown": "uncertain in carbohydrate content",
}

CARB_KEYWORDS = (
    "rice",
    "pasta",
    "noodle",
    "bread",
    "tortilla",
    "potato",
    "grain",
    "oat",
    "quinoa",
    "bean",
    "fruit",
)

SAMPLE_IMAGE_DIRECTORY = Path("examples") / "sample_images"
SUPPORTED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

APP_CSS = """
.gradio-container {
  max-width: 1080px !important;
  margin: 0 auto !important;
  background: #f5f5f7 !important;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif !important;
}
#hero { max-width: 720px; margin: 0 auto 24px; padding: 34px 18px 8px; text-align: center; }
#hero h1 {
  margin: 0 0 8px; color: #1d1d1f; font-size: clamp(2rem, 6vw, 3.4rem);
  letter-spacing: -0.045em; line-height: 1.05;
}
#hero .hero-subtitle { margin: 0; color: #6e6e73; font-size: clamp(1.05rem, 2.6vw, 1.35rem); }
#hero .hero-safety {
  display: inline-block; margin-top: 14px; padding: 7px 12px; border-radius: 999px;
  background: #eaf4ee; color: #37624f; font-size: 0.88rem;
}
.upload-card {
  padding: 18px !important; border: 1px solid rgba(29, 29, 31, 0.08) !important;
  border-radius: 24px !important; background: #fff !important;
  box-shadow: 0 12px 36px rgba(0, 0, 0, 0.06) !important;
}
.upload-card h3 { margin-top: 0; color: #1d1d1f; letter-spacing: -0.02em; }
.demo-note {
  margin-top: 10px; padding: 12px 14px; border-radius: 14px; background: #eef7f2;
  color: #37624f; font-size: 0.88rem; line-height: 1.45;
}
.result-card {
  min-height: 100%; padding: clamp(22px, 4vw, 34px); border-radius: 28px;
  border: 1px solid rgba(29, 29, 31, 0.08); background: #fff;
  box-shadow: 0 16px 46px rgba(0, 0, 0, 0.07); color: #1d1d1f;
}
.result-card h2 {
  margin: 10px 0 8px; font-size: clamp(1.7rem, 4vw, 2.35rem);
  letter-spacing: -0.035em; line-height: 1.12;
}
.result-card .description {
  margin: 0 0 20px; color: #6e6e73; font-size: 1rem; line-height: 1.55;
}
.rating-pill {
  display: inline-flex; padding: 7px 12px; border-radius: 999px;
  font-size: 0.9rem; font-weight: 650;
}
.rating-green { background: #e8f7ee; color: #176a42; }
.rating-yellow { background: #fff5d6; color: #7a5a00; }
.rating-orange { background: #ffecd7; color: #974d00; }
.rating-red { background: #fde8e7; color: #a12b24; }
.rating-unknown { background: #eeeeef; color: #5b5b60; }
.metric-grid {
  display: grid; grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px; margin: 20px 0;
}
.metric { padding: 14px 10px; border-radius: 16px; background: #f7f7f9; text-align: center; }
.metric strong {
  display: block; font-size: clamp(1.15rem, 3vw, 1.5rem); letter-spacing: -0.025em;
}
.metric span { color: #6e6e73; font-size: 0.78rem; }
.insight-box {
  margin-top: 12px; padding: 15px 16px; border-radius: 18px;
  background: #f0f7f3; line-height: 1.5;
}
.insight-box.suggestion { background: #f6f4fb; }
.insight-box strong { display: block; margin-bottom: 4px; }
.estimate-note {
  margin: 18px 0 0; color: #6e6e73; font-size: 0.78rem; line-height: 1.45;
}
.support-note {
  padding: 12px 16px; border-radius: 16px; background: rgba(255, 255, 255, 0.72);
  color: #6e6e73; font-size: 0.9rem;
}
.details-heading { margin: 26px 0 8px; }
@media (max-width: 700px) {
  #hero { padding-top: 20px; }
  .upload-card, .result-card { border-radius: 20px !important; }
  .metric-grid { gap: 7px; }
  .metric { padding: 12px 5px; }
}
"""

INITIAL_RESULT_CARD = """
<article class="result-card">
  <span class="rating-pill rating-unknown">Ready when you are</span>
  <h2>Your meal, made easier to understand</h2>
  <p class="description">Add a meal photo or choose a sample, then select Analyze Meal.</p>
  <div class="insight-box">
    <strong>What you will see</strong>
    A clear nutrition estimate, carb-focused context, and one practical portion idea.
  </div>
  <p class="estimate-note">Results are approximate and are not medical advice.</p>
</article>
"""

UIOutput = tuple[
    str,
    list[list[str]],
    list[list[str]],
    str,
    dict[str, Any],
]


def find_sample_images(directory: Path = SAMPLE_IMAGE_DIRECTORY) -> list[str]:
    """Return supported sample-image paths, or an empty list if none exist."""
    if not directory.is_dir():
        return []

    return [
        path.as_posix()
        for path in sorted(directory.iterdir())
        if path.is_file() and path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
    ]


def runtime_mode_note() -> str:
    """Return a non-technical description of the configured analysis mode."""
    config = load_config()
    if config.demo_mode:
        heading = "Demo mode is active."
        detail = (
            "The interface uses a sample structured meal analysis and does not "
            "make an API request."
        )
    elif not config.openai_api_key:
        heading = "Live mode needs configuration."
        detail = "Add an API key or switch back to demo mode before analyzing a meal."
    else:
        heading = "Live analysis is active."
        detail = "Your photo will be checked, analyzed, and safety-reviewed."

    return (
        '<div class="demo-note">'
        f"<strong>{heading}</strong><br>"
        f"{detail}"
        "</div>"
    )


def recommendation_badge(label: str | None) -> str:
    """Return a careful carb-oriented meal rating."""
    normalized_label = str(label or "unknown").lower()
    return RECOMMENDATION_BADGES.get(normalized_label, RECOMMENDATION_BADGES["unknown"])


def _format_number(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:g}"
    return str(value) if value is not None else "—"


def format_primary_metrics(meal_analysis: dict[str, Any]) -> str:
    """Build the three primary nutrition metrics shown on the result card."""
    nutrition = meal_analysis.get("estimated_nutrition") or {}
    metrics = (
        ("Calories", nutrition.get("calories"), "kcal"),
        ("Carbs", nutrition.get("carbohydrates_g"), "g"),
        ("Protein", nutrition.get("protein_g"), "g"),
    )
    return "".join(
        (
            '<div class="metric">'
            f"<strong>{escape(_format_number(value))} {unit}</strong>"
            f"<span>{label}</span>"
            "</div>"
        )
        for label, value, unit in metrics
    )


def _main_carb_source(meal_analysis: dict[str, Any]) -> str | None:
    for ingredient in meal_analysis.get("ingredients", []):
        name = str(ingredient.get("name", "")).strip()
        if any(keyword in name.lower() for keyword in CARB_KEYWORDS):
            return name
    return None


def format_carb_watch(meal_analysis: dict[str, Any]) -> str:
    """Create non-medical carb context from the structured estimate."""
    nutrition = meal_analysis.get("estimated_nutrition") or {}
    recommendation = str(meal_analysis.get("recommendation", "unknown")).lower()
    carb_description = CARB_DESCRIPTIONS.get(
        recommendation, CARB_DESCRIPTIONS["unknown"]
    )
    carbs = nutrition.get("carbohydrates_g")
    carb_amount = (
        f", with about {_format_number(carbs)} g estimated"
        if carbs is not None
        else ""
    )
    source = _main_carb_source(meal_analysis)
    source_sentence = (
        f" {source} appears to be the main carb source."
        if source
        else " The main carb source is uncertain from the photo."
    )
    portion_target = source.lower() if source else "starchy foods"
    return (
        f"This meal appears {carb_description}{carb_amount}.{source_sentence} "
        "If you are watching carbohydrate intake or glucose response, consider a "
        f"smaller portion of {portion_target} or add more non-starchy vegetables."
    )


def format_consumer_summary(result: dict[str, Any]) -> str:
    """Build the primary consumer-facing result card."""
    status = str(result.get("status", "failed"))
    message = escape(str(result.get("message", "Analysis could not be completed.")))

    if status == "rejected":
        return (
            '<article class="result-card">'
            '<span class="rating-pill rating-orange">Photo not analyzed</span>'
            "<h2>Please try another meal photo</h2>"
            f'<p class="description">{message}</p>'
            '<p class="estimate-note">No nutrition guidance was generated.</p>'
            "</article>"
        )
    if status in {"failed", "retry_exhausted"}:
        return (
            '<article class="result-card">'
            '<span class="rating-pill rating-red">Analysis unavailable</span>'
            "<h2>We could not show a result</h2>"
            f'<p class="description">{message}</p>'
            '<p class="estimate-note">Please try again with a clear meal photo.</p>'
            "</article>"
        )

    meal_analysis = result.get("meal_analysis") or {}
    recommendation = str(meal_analysis.get("recommendation", "unknown")).lower()
    rating_class = (
        recommendation if recommendation in RECOMMENDATION_BADGES else "unknown"
    )
    badge = escape(recommendation_badge(recommendation))
    title = escape(str(meal_analysis.get("title", "Meal summary")))
    description = escape(str(meal_analysis.get("description", "")))
    carb_watch = escape(format_carb_watch(meal_analysis))
    guidance = escape(str(meal_analysis.get("guidance", "")))
    uncertainty = escape(str(meal_analysis.get("uncertainty_notes") or ""))

    estimate_note = "Nutrition values are estimated from an image."
    if uncertainty:
        estimate_note = f"{estimate_note} {uncertainty}"

    return f"""
<article class="result-card">
  <span class="rating-pill rating-{rating_class}">{badge}</span>
  <h2>{title}</h2>
  <p class="description">{description}</p>
  <div class="metric-grid">{format_primary_metrics(meal_analysis)}</div>
  <div class="insight-box">
    <strong>Carb watch</strong>
    {carb_watch}
  </div>
  <div class="insight-box suggestion">
    <strong>Simple suggestion</strong>
    {guidance}
  </div>
  <p class="estimate-note">{estimate_note} Not medical advice.</p>
</article>
"""


def format_nutrition_table(meal_analysis: dict[str, Any]) -> list[list[str]]:
    """Format available nutrition estimates for a simple details table."""
    nutrition = meal_analysis.get("estimated_nutrition") or {}
    rows: list[list[str]] = []

    for field, (label, unit) in NUTRITION_LABELS.items():
        value = nutrition.get(field)
        if value is not None:
            rows.append([label, f"{_format_number(value)} {unit}"])
    return rows


def format_ingredients_table(meal_analysis: dict[str, Any]) -> list[list[str]]:
    """Format estimated ingredients without technical field names."""
    rows: list[list[str]] = []
    for ingredient in meal_analysis.get("ingredients", []):
        impact = str(ingredient.get("impact", "unknown")).lower()
        rows.append(
            [
                str(ingredient.get("name", "")),
                INGREDIENT_IMPACT_BADGES.get(
                    impact, INGREDIENT_IMPACT_BADGES["unknown"]
                ),
                str(ingredient.get("notes") or ""),
            ]
        )
    return rows


def format_support_note(result: dict[str, Any]) -> str:
    """Summarize safety, mode, latency, and rejection details unobtrusively."""
    status = str(result.get("status", "failed"))
    metadata = result.get("metadata") or {}
    safety = result.get("safety") or {}
    guardrail = result.get("guardrail") or {}
    details: list[str] = []

    if safety.get("passed"):
        details.append("✅ Safety check passed")
    elif safety:
        details.append("⚠️ Safety review flagged this output")
    else:
        details.append("Safety review was not completed")

    if status == "rejected" and guardrail:
        reason = guardrail.get("blocked_reason") or "Input did not pass validation."
        details.append(f"Guardrail: {reason}")

    details.append("Demo mode" if metadata.get("demo_mode") else "Live mode")
    latency = metadata.get("latency_seconds")
    if isinstance(latency, (int, float)):
        latency_text = (
            f"{latency * 1000:.1f} ms" if latency < 1 else f"{latency:.2f} seconds"
        )
        details.append(f"{latency_text} response time")

    return "<div class=\"support-note\">" + " &nbsp;•&nbsp; ".join(
        escape(detail) for detail in details
    ) + "</div>"


def _ui_failure(message: str) -> dict[str, Any]:
    result = analyze_meal_image("")
    result["message"] = message
    return result


def _format_ui_output(result: dict[str, Any]) -> UIOutput:
    meal_analysis = result.get("meal_analysis") or {}
    return (
        format_consumer_summary(result),
        format_nutrition_table(meal_analysis),
        format_ingredients_table(meal_analysis),
        format_support_note(result),
        result,
    )


def run_ui_analysis(image: Image.Image | None) -> UIOutput:
    """Analyze an uploaded image and remove its temporary file afterward."""
    if image is None:
        return _format_ui_output(
            _ui_failure("Please add a meal photo before selecting Analyze Meal.")
        )

    temporary_path: Path | None = None
    try:
        with NamedTemporaryFile(suffix=".png", delete=False) as temporary_file:
            temporary_path = Path(temporary_file.name)
        image.save(temporary_path, format="PNG")
        result = analyze_meal_image(str(temporary_path))
    except (OSError, ValueError):
        result = _ui_failure(
            "That image could not be processed. Please try a different meal photo."
        )
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    return _format_ui_output(result)


with gr.Blocks(title="CarbKind AI") as demo:
    gr.HTML(
        """
        <section id="hero">
          <h1>CarbKind AI 🥗</h1>
          <p class="hero-subtitle">Snap a meal. Understand the carbs.</p>
          <span class="hero-safety">Approximate nutrition estimate. Not medical advice.</span>
        </section>
        """
    )

    with gr.Row(equal_height=False):
        with gr.Column(scale=2, min_width=290, elem_classes=["upload-card"]):
            gr.Markdown("### Add your meal photo")
            meal_image = gr.Image(type="pil", label="Meal photo", height=330)
            analyze_button = gr.Button("Analyze Meal", variant="primary")
            sample_images = find_sample_images()
            if sample_images:
                gr.Examples(
                    examples=[[sample_image] for sample_image in sample_images],
                    inputs=[meal_image],
                    label="Or try a sample meal",
                )
            gr.HTML(runtime_mode_note())

        with gr.Column(scale=3, min_width=320):
            consumer_summary = gr.HTML(INITIAL_RESULT_CARD)
            support_note = gr.HTML(
                '<div class="support-note">Add a photo to see an approximate result.</div>'
            )

    gr.Markdown("## Meal details", elem_classes=["details-heading"])
    with gr.Row(equal_height=False):
        with gr.Column(scale=2):
            nutrition_table = gr.Dataframe(
                headers=["Metric", "Estimate"],
                label="Nutrition details",
                interactive=False,
            )
        with gr.Column(scale=3):
            ingredient_table = gr.Dataframe(
                headers=["Ingredient", "Impact", "Notes"],
                label="Estimated ingredients",
                interactive=False,
            )

    with gr.Accordion("Advanced: Raw structured response", open=False):
        raw_json = gr.JSON(label="Raw JSON")

    analyze_button.click(
        fn=run_ui_analysis,
        inputs=meal_image,
        outputs=[
            consumer_summary,
            nutrition_table,
            ingredient_table,
            support_note,
            raw_json,
        ],
    )


if __name__ == "__main__":
    demo.launch(theme=gr.themes.Soft(), css=APP_CSS)
