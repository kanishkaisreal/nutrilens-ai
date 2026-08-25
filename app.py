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

INGREDIENT_IMPACT_LABELS = {
    "green": "Lower / balanced",
    "yellow": "Moderate",
    "orange": "Higher",
    "red": "Caution",
    "unknown": "Unknown",
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
:root {
  color-scheme: dark;
  --ck-page: #050505;
  --ck-surface: rgba(255, 255, 255, 0.06);
  --ck-surface-raised: rgba(255, 255, 255, 0.09);
  --ck-border: rgba(255, 255, 255, 0.12);
  --ck-border-soft: rgba(255, 255, 255, 0.08);
  --ck-text: #f5f5f7;
  --ck-muted: #a1a1aa;
  --ck-green: #30d158;
  --ck-yellow: #ffd60a;
  --ck-orange: #ff9f0a;
  --ck-red: #ff453a;
  --ck-blue: #0a84ff;
}
html { scroll-behavior: smooth; background: var(--ck-page); }
body {
  background:
    radial-gradient(circle at 18% -10%, rgba(48, 209, 88, 0.11), transparent 32rem),
    radial-gradient(circle at 92% 18%, rgba(10, 132, 255, 0.08), transparent 28rem),
    var(--ck-page) !important;
}
.gradio-container {
  --body-background-fill: transparent;
  --background-fill-primary: #0b0b0c;
  --background-fill-secondary: #121214;
  --block-background-fill: var(--ck-surface);
  --block-border-color: var(--ck-border);
  --block-label-background-fill: transparent;
  --body-text-color: var(--ck-text);
  --body-text-color-subdued: var(--ck-muted);
  --input-background-fill: #0b0b0d;
  --input-border-color: var(--ck-border);
  --button-primary-background-fill: var(--ck-green);
  --button-primary-background-fill-hover: #3ee36a;
  --button-primary-text-color: #031006;
  max-width: 1100px !important;
  width: 100% !important;
  min-height: 100vh !important;
  margin: 0 auto !important;
  padding: 0 22px 52px !important;
  background:
    radial-gradient(circle at 18% -10%, rgba(48, 209, 88, 0.11), transparent 32rem),
    radial-gradient(circle at 92% 18%, rgba(10, 132, 255, 0.08), transparent 28rem),
    var(--ck-page) !important;
  box-shadow: 0 0 0 100vmax var(--ck-page);
  clip-path: inset(0 -100vmax);
  color: var(--ck-text) !important;
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", sans-serif !important;
  -webkit-font-smoothing: antialiased;
}
.gradio-container,
.gradio-container *,
.gradio-container *::before,
.gradio-container *::after { box-sizing: border-box; }
.gradio-container main {
  width: 100% !important;
  min-width: 0 !important;
  margin: 0 !important;
  padding: 0 !important;
}
#hero {
  max-width: 820px;
  margin: 0 auto;
  padding: clamp(54px, 9vw, 100px) 16px clamp(34px, 6vw, 62px);
  text-align: center;
}
#hero .hero-eyebrow {
  margin: 0 0 18px;
  color: var(--ck-green);
  font-size: 0.76rem;
  font-weight: 750;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}
#hero h1 {
  margin: 0;
  color: var(--ck-text);
  font-size: clamp(3rem, 9vw, 5.7rem);
  font-weight: 740;
  letter-spacing: -0.065em;
  line-height: 0.96;
}
#hero .hero-subtitle {
  margin: 20px 0 0;
  color: var(--ck-text);
  font-size: clamp(1.35rem, 3vw, 2rem);
  font-weight: 580;
  letter-spacing: -0.025em;
}
#hero .hero-description {
  max-width: 660px;
  margin: 16px auto 0;
  color: var(--ck-muted);
  font-size: clamp(1rem, 2vw, 1.12rem);
  line-height: 1.6;
}
#hero .hero-safety {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  margin-top: 22px;
  padding: 8px 13px;
  border: 1px solid var(--ck-border-soft);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.04);
  color: #c7c7cc;
  font-size: 0.84rem;
}
.app-grid, .details-grid {
  gap: 18px !important;
  align-items: stretch !important;
}
.upload-card {
  overflow: hidden;
  padding: clamp(18px, 3vw, 26px) !important;
  border: 1px solid var(--ck-border) !important;
  border-radius: 30px !important;
  background: var(--ck-surface) !important;
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.34) !important;
  backdrop-filter: blur(24px);
  -webkit-backdrop-filter: blur(24px);
  transition: transform 220ms ease, border-color 220ms ease, background 220ms ease;
}
.upload-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.18) !important;
  background: rgba(255, 255, 255, 0.075) !important;
}
.panel-heading { margin: 0 0 16px; }
.panel-heading span {
  display: block;
  margin-bottom: 5px;
  color: var(--ck-muted);
  font-size: 0.76rem;
  font-weight: 720;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.panel-heading h2 {
  margin: 0;
  color: var(--ck-text);
  font-size: 1.32rem;
  letter-spacing: -0.025em;
}
#meal-image {
  overflow: hidden;
  border: 1px solid var(--ck-border) !important;
  border-radius: 22px !important;
  background: rgba(0, 0, 0, 0.28) !important;
}
#meal-image .wrap, #meal-image .image-container {
  background: transparent !important;
}
#analyze-button {
  min-height: 52px !important;
  margin-top: 5px;
  border: 0 !important;
  border-radius: 16px !important;
  background: linear-gradient(180deg, #3adb64 0%, var(--ck-green) 100%) !important;
  box-shadow: 0 10px 28px rgba(48, 209, 88, 0.2) !important;
  color: #031006 !important;
  font-size: 1rem !important;
  font-weight: 760 !important;
  transition: transform 180ms ease, box-shadow 180ms ease, filter 180ms ease;
}
#analyze-button:hover {
  transform: translateY(-1px);
  filter: brightness(1.06);
  box-shadow: 0 14px 34px rgba(48, 209, 88, 0.28) !important;
}
#analyze-button:active { transform: translateY(0) scale(0.99); }
.mode-banner {
  display: flex;
  align-items: center;
  gap: 15px;
  max-width: 920px;
  margin: -28px auto 30px;
  padding: 16px 18px;
  border: 1px solid rgba(255, 214, 10, 0.24);
  border-radius: 20px;
  background: rgba(255, 214, 10, 0.075);
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.22);
}
.mode-banner.live {
  border-color: rgba(48, 209, 88, 0.24);
  background: rgba(48, 209, 88, 0.075);
}
.mode-banner.warning {
  border-color: rgba(255, 159, 10, 0.24);
  background: rgba(255, 159, 10, 0.075);
}
.mode-banner-copy { min-width: 0; }
.mode-banner h2 { margin: 0 0 3px; color: var(--ck-text); font-size: 1rem; }
.mode-banner p {
  margin: 0;
  color: #c7c7cc;
  font-size: 0.88rem;
  line-height: 1.5;
}
.mode-pill {
  flex: 0 0 auto;
  padding: 5px 9px;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 740;
  white-space: nowrap;
}
.mode-demo { background: rgba(255, 214, 10, 0.14); color: var(--ck-yellow); }
.mode-live { background: rgba(48, 209, 88, 0.14); color: var(--ck-green); }
.mode-warning { background: rgba(255, 159, 10, 0.14); color: var(--ck-orange); }
.upload-mode-note {
  margin-top: 12px;
  padding: 13px 14px;
  border: 1px solid var(--ck-border-soft);
  border-radius: 17px;
  background: rgba(255, 255, 255, 0.035);
  color: var(--ck-muted);
  font-size: 0.82rem;
  line-height: 1.48;
}
.upload-mode-note strong { color: var(--ck-text); }
.result-card {
  min-height: 100%;
  padding: clamp(24px, 4.5vw, 40px);
  border: 1px solid var(--ck-border);
  border-radius: 32px;
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.105), rgba(255, 255, 255, 0.045));
  box-shadow: 0 28px 80px rgba(0, 0, 0, 0.42);
  color: var(--ck-text);
  backdrop-filter: blur(28px);
  -webkit-backdrop-filter: blur(28px);
  transition: transform 240ms ease, border-color 240ms ease;
}
.result-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255, 255, 255, 0.18);
}
.result-card h2 {
  margin: 16px 0 9px;
  color: var(--ck-text);
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 680;
  letter-spacing: -0.05em;
  line-height: 1.03;
}
.result-card .description {
  margin: 0 0 22px;
  color: var(--ck-muted);
  font-size: 1rem;
  line-height: 1.55;
}
.result-context {
  margin: 12px 0 -5px;
  padding: 10px 12px;
  border-radius: 13px;
  font-size: 0.82rem;
  font-weight: 680;
  line-height: 1.4;
}
.demo-context {
  border: 1px solid rgba(255, 214, 10, 0.18);
  background: rgba(255, 214, 10, 0.085);
  color: #ffe45c;
}
.live-context {
  border: 1px solid rgba(48, 209, 88, 0.16);
  background: rgba(48, 209, 88, 0.075);
  color: #7be695;
}
.rating-pill {
  display: inline-flex;
  align-items: center;
  padding: 7px 11px;
  border: 1px solid transparent;
  border-radius: 999px;
  font-size: 0.82rem;
  font-weight: 720;
}
.rating-green { border-color: rgba(48, 209, 88, 0.2); background: rgba(48, 209, 88, 0.13); color: #65e883; }
.rating-yellow { border-color: rgba(255, 214, 10, 0.2); background: rgba(255, 214, 10, 0.12); color: var(--ck-yellow); }
.rating-orange { border-color: rgba(255, 159, 10, 0.2); background: rgba(255, 159, 10, 0.12); color: var(--ck-orange); }
.rating-red { border-color: rgba(255, 69, 58, 0.2); background: rgba(255, 69, 58, 0.12); color: #ff6961; }
.rating-unknown { border-color: var(--ck-border); background: rgba(255, 255, 255, 0.07); color: #d1d1d6; }
.metric-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 9px;
  margin: 22px 0;
}
.metric {
  padding: 16px 8px;
  border: 1px solid var(--ck-border-soft);
  border-radius: 18px;
  background: rgba(0, 0, 0, 0.22);
  text-align: center;
}
.metric strong {
  display: block;
  color: var(--ck-text);
  font-size: clamp(1.18rem, 3vw, 1.5rem);
  font-weight: 670;
  letter-spacing: -0.03em;
}
.metric span {
  display: block;
  margin-top: 4px;
  color: var(--ck-muted);
  font-size: 0.72rem;
  font-weight: 650;
  letter-spacing: 0.045em;
  text-transform: uppercase;
}
.insight-box {
  margin-top: 11px;
  padding: 16px 17px;
  border: 1px solid rgba(48, 209, 88, 0.12);
  border-radius: 19px;
  background: rgba(48, 209, 88, 0.075);
  color: #dedee3;
  line-height: 1.52;
}
.insight-box.suggestion {
  border-color: rgba(10, 132, 255, 0.13);
  background: rgba(10, 132, 255, 0.075);
}
.insight-box strong {
  display: block;
  margin-bottom: 5px;
  color: var(--ck-text);
  font-size: 0.82rem;
  letter-spacing: 0.02em;
}
.estimate-note {
  margin: 20px 0 0;
  color: #85858d;
  font-size: 0.76rem;
  line-height: 1.5;
}
.state-card { display: flex; min-height: 420px; flex-direction: column; justify-content: center; }
.support-note {
  margin-top: 10px;
  padding: 11px 15px;
  border: 1px solid var(--ck-border-soft);
  border-radius: 15px;
  background: rgba(255, 255, 255, 0.035);
  color: var(--ck-muted);
  font-size: 0.78rem;
  line-height: 1.45;
}
.section-heading { margin: clamp(34px, 6vw, 58px) 0 15px; }
.section-heading span {
  color: var(--ck-green);
  font-size: 0.72rem;
  font-weight: 720;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}
.section-heading h2 {
  margin: 6px 0 0;
  color: var(--ck-text);
  font-size: clamp(1.45rem, 3vw, 2rem);
  letter-spacing: -0.035em;
}
.detail-card {
  overflow: hidden;
  height: 100%;
  border: 1px solid var(--ck-border);
  border-radius: 22px;
  background: var(--ck-surface);
}
.detail-card h3 {
  margin: 0;
  padding: 17px 19px;
  border-bottom: 1px solid var(--ck-border-soft);
  color: var(--ck-text);
  font-size: 0.95rem;
}
.table-scroll { max-width: 100%; overflow-x: auto; scrollbar-color: #3a3a3c transparent; }
.dark-data-table {
  width: 100%;
  min-width: 360px;
  border-collapse: collapse;
  background: transparent;
  color: var(--ck-text);
  font-size: 0.87rem;
}
.dark-data-table th, .dark-data-table td {
  padding: 13px 17px;
  border-bottom: 1px solid var(--ck-border-soft);
  text-align: left;
  vertical-align: top;
}
.dark-data-table th {
  background: rgba(255, 255, 255, 0.055);
  color: #d1d1d6;
  font-size: 0.72rem;
  font-weight: 720;
  letter-spacing: 0.055em;
  text-transform: uppercase;
}
.dark-data-table td { background: rgba(0, 0, 0, 0.12); color: #b7b7bf; line-height: 1.45; }
.dark-data-table tbody tr:last-child td { border-bottom: 0; }
.dark-data-table tbody tr:hover td { background: rgba(255, 255, 255, 0.045); }
.dark-data-table tbody tr:focus-within td { background: rgba(48, 209, 88, 0.07); }
.dark-data-table td:first-child { color: var(--ck-text); font-weight: 620; }
.impact { display: inline-flex; align-items: center; gap: 7px; color: #d1d1d6; font-weight: 620; white-space: nowrap; }
.impact-dot { width: 8px; height: 8px; flex: 0 0 8px; border-radius: 50%; background: #8e8e93; box-shadow: 0 0 0 3px rgba(142, 142, 147, 0.12); }
.impact-green .impact-dot { background: var(--ck-green); box-shadow: 0 0 0 3px rgba(48, 209, 88, 0.13); }
.impact-yellow .impact-dot { background: var(--ck-yellow); box-shadow: 0 0 0 3px rgba(255, 214, 10, 0.13); }
.impact-orange .impact-dot { background: var(--ck-orange); box-shadow: 0 0 0 3px rgba(255, 159, 10, 0.13); }
.impact-red .impact-dot { background: var(--ck-red); box-shadow: 0 0 0 3px rgba(255, 69, 58, 0.13); }
.table-empty { margin: 0; padding: 22px 19px; color: var(--ck-muted); font-size: 0.87rem; }
.advanced-panel {
  margin-top: 18px !important;
  overflow: hidden;
  border: 1px solid var(--ck-border-soft) !important;
  border-radius: 18px !important;
  background: rgba(255, 255, 255, 0.025) !important;
  color: var(--ck-muted) !important;
}
.gradio-container .prose h1,
.gradio-container .prose h2,
.gradio-container .prose h3,
.gradio-container label { color: var(--ck-text) !important; }
.gradio-container .prose, .gradio-container p { color: inherit; }
.gradio-container footer { display: none !important; }
@media (max-width: 760px) {
  .gradio-container {
    width: 100vw !important;
    max-width: 100vw !important;
    overflow-x: hidden !important;
    padding: 0 14px 36px !important;
  }
  .gradio-container > * { max-width: 100% !important; }
  #hero { width: 100%; max-width: 100%; padding-top: 44px; }
  #hero .hero-subtitle, #hero .hero-description { overflow-wrap: anywhere; }
  .app-grid, .details-grid {
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) !important;
    width: 100% !important;
    max-width: 100% !important;
  }
  .app-grid > *, .details-grid > * {
    min-width: 0 !important;
    width: 100% !important;
    max-width: 100% !important;
  }
  .upload-card, .result-card {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    border-radius: 24px !important;
  }
  .result-card { min-height: auto; }
  .state-card { min-height: 310px; }
}
@media (max-width: 430px) {
  #hero h1 { font-size: 3.15rem; }
  .metric-grid { gap: 6px; }
  .metric { padding: 14px 4px; border-radius: 15px; }
  .metric strong { font-size: 1.05rem; }
  .mode-banner { align-items: flex-start; flex-direction: column; margin-top: -20px; }
  .dark-data-table th, .dark-data-table td { padding: 12px 14px; }
}
@media (prefers-reduced-motion: reduce) {
  html { scroll-behavior: auto; }
  *, *::before, *::after { transition-duration: 0.01ms !important; }
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
    str,
    str,
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


def runtime_mode_banner() -> str:
    """Return a prominent explanation of the configured analysis mode."""
    config = load_config()
    if config.demo_mode:
        label = "Demo Mode"
        pill_class = "mode-demo"
        banner_class = "demo"
        detail = (
            "This is a fixed sample response. Your uploaded image is used only to "
            "preview the interface. Turn off DEMO_MODE to analyze real images."
        )
    elif not config.openai_api_key:
        label = "Live Mode"
        pill_class = "mode-warning"
        banner_class = "warning"
        detail = (
            "Your uploaded image is analyzed by the configured model pipeline. "
            "Add an API key before analyzing a meal."
        )
    else:
        label = "Live Mode"
        pill_class = "mode-live"
        banner_class = "live"
        detail = "Your uploaded image is analyzed by the configured model pipeline."

    return (
        f'<aside class="mode-banner {banner_class}" aria-label="Application mode">'
        f'<span class="mode-pill {pill_class}">{label}</span>'
        '<div class="mode-banner-copy">'
        f"<h2>{label}</h2><p>{detail}</p>"
        "</div></aside>"
    )


def runtime_upload_note() -> str:
    """Explain how the uploaded image is handled in the current mode."""
    if load_config().demo_mode:
        detail = (
            "Demo mode is currently active. You can upload or choose a sample image "
            "to preview the interface, but the response is a fixed sample meal."
        )
    else:
        detail = "Live mode analyzes the uploaded image using the configured model pipeline."
    return f'<div class="upload-mode-note"><strong>Mode:</strong> {detail}</div>'


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
    return f"This meal appears {carb_description}{carb_amount}.{source_sentence}"


def format_consumer_summary(result: dict[str, Any]) -> str:
    """Build the primary consumer-facing result card."""
    status = str(result.get("status", "failed"))
    message = escape(str(result.get("message", "Analysis could not be completed.")))

    if status == "rejected":
        return (
            '<article class="result-card state-card">'
            '<span class="rating-pill rating-orange">Photo not analyzed</span>'
            "<h2>Please try another meal photo</h2>"
            f'<p class="description">{message}</p>'
            '<p class="estimate-note">No nutrition guidance was generated.</p>'
            "</article>"
        )
    if status in {"failed", "retry_exhausted"}:
        return (
            '<article class="result-card state-card">'
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
    is_demo = bool((result.get("metadata") or {}).get("demo_mode"))
    result_context = (
        '<div class="result-context demo-context">'
        "Sample result, not analysis of your uploaded image."
        "</div>"
        if is_demo
        else '<div class="result-context live-context">Estimated from your uploaded image.</div>'
    )

    estimate_note = (
        "Nutrition values are part of this fixed sample response."
        if is_demo
        else "Nutrition values are estimated from an image."
    )
    if uncertainty:
        estimate_note = f"{estimate_note} {uncertainty}"

    return f"""
<article class="result-card">
  <span class="rating-pill rating-{rating_class}">{badge}</span>
  {result_context}
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
                impact if impact in INGREDIENT_IMPACT_LABELS else "unknown",
                str(ingredient.get("notes") or ""),
            ]
        )
    return rows


def _render_dark_table(
    *, title: str, headers: tuple[str, ...], rows: list[list[str]], empty_text: str
) -> str:
    """Render escaped table content without relying on dataframe theme internals."""
    safe_title = escape(title)
    if not rows:
        return (
            '<section class="detail-card">'
            f"<h3>{safe_title}</h3>"
            f'<p class="table-empty">{escape(empty_text)}</p>'
            "</section>"
        )
    headings = "".join(
        f'<th scope="col">{escape(header)}</th>' for header in headers
    )
    body = "".join(
        "<tr>"
        + "".join(f"<td>{escape(str(value))}</td>" for value in row)
        + "</tr>"
        for row in rows
    )
    return (
        '<section class="detail-card">'
        f"<h3>{safe_title}</h3>"
        f'<div class="table-scroll" role="region" aria-label="{safe_title}">'
        '<table class="dark-data-table">'
        f"<thead><tr>{headings}</tr></thead><tbody>{body}</tbody>"
        "</table></div></section>"
    )


def render_nutrition_html(rows: list[list[str]]) -> str:
    """Render nutrition rows as a readable dark-theme table."""
    return _render_dark_table(
        title="Nutrition details",
        headers=("Metric", "Estimate"),
        rows=rows,
        empty_text="No nutrition details yet.",
    )


def render_ingredients_html(rows: list[list[str]]) -> str:
    """Render escaped ingredient rows with allowlisted impact indicators."""
    if not rows:
        return _render_dark_table(
            title="Estimated ingredients",
            headers=("Ingredient", "Impact", "Notes"),
            rows=[],
            empty_text="No ingredient details yet.",
        )

    rendered_rows: list[str] = []
    for row in rows:
        name = row[0] if len(row) > 0 else ""
        raw_impact = str(row[1] if len(row) > 1 else "unknown").lower()
        impact = raw_impact if raw_impact in INGREDIENT_IMPACT_LABELS else "unknown"
        notes = row[2] if len(row) > 2 else ""
        rendered_rows.append(
            "<tr>"
            f"<td>{escape(str(name))}</td>"
            f'<td><span class="impact impact-{impact}"><span class="impact-dot" '
            f'aria-hidden="true"></span>{escape(INGREDIENT_IMPACT_LABELS[impact])}</span></td>'
            f"<td>{escape(str(notes))}</td>"
            "</tr>"
        )

    headings = "".join(
        f'<th scope="col">{escape(header)}</th>'
        for header in ("Ingredient", "Impact", "Notes")
    )
    return (
        '<section class="detail-card"><h3>Estimated ingredients</h3>'
        '<div class="table-scroll" role="region" aria-label="Estimated ingredients">'
        '<table class="dark-data-table">'
        f"<thead><tr>{headings}</tr></thead><tbody>{''.join(rendered_rows)}</tbody>"
        "</table></div></section>"
    )


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
        render_nutrition_html(format_nutrition_table(meal_analysis)),
        render_ingredients_html(format_ingredients_table(meal_analysis)),
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
          <p class="hero-eyebrow">Food-photo clarity</p>
          <h1>CarbKind AI</h1>
          <p class="hero-subtitle">Snap a meal. Understand the carbs.</p>
          <p class="hero-description">
            A simple food-photo assistant for approximate nutrition, carb awareness,
            and portion guidance.
          </p>
          <span class="hero-safety">✦ Approximate estimates only. Not medical advice.</span>
        </section>
        """
    )
    gr.HTML(runtime_mode_banner())

    with gr.Row(equal_height=False, elem_classes=["app-grid"]):
        with gr.Column(scale=2, min_width=290, elem_classes=["upload-card"]):
            gr.HTML(
                '<div class="panel-heading"><span>Step one</span>'
                "<h2>Add your meal photo</h2></div>"
            )
            meal_image = gr.Image(
                type="pil", label="Meal photo", height=330, elem_id="meal-image"
            )
            analyze_button = gr.Button(
                "Analyze Meal", variant="primary", elem_id="analyze-button"
            )
            sample_images = find_sample_images()
            if sample_images:
                gr.Examples(
                    examples=[[sample_image] for sample_image in sample_images],
                    inputs=[meal_image],
                    label="Or try a sample meal",
                )
            gr.HTML(runtime_upload_note())

        with gr.Column(scale=3, min_width=320):
            consumer_summary = gr.HTML(INITIAL_RESULT_CARD)
            support_note = gr.HTML(
                '<div class="support-note">Add a photo to see an approximate result.</div>'
            )

    gr.HTML(
        '<div class="section-heading"><span>Explore the estimate</span>'
        "<h2>Meal details</h2></div>"
    )
    with gr.Row(equal_height=False, elem_classes=["details-grid"]):
        with gr.Column(scale=2):
            nutrition_table = gr.HTML(render_nutrition_html([]))
        with gr.Column(scale=3):
            ingredient_table = gr.HTML(render_ingredients_html([]))

    with gr.Accordion(
        "Advanced: structured response",
        open=False,
        elem_classes=["advanced-panel"],
    ):
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
