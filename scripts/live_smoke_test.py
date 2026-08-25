"""Run one public-safe live NutriLens pipeline smoke test."""

import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_DIRECTORY = PROJECT_ROOT / "examples" / "sample_images"
SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agents.pipeline import analyze_meal_image  # noqa: E402


def _first_sample_image() -> Path | None:
    if not SAMPLE_DIRECTORY.is_dir():
        return None
    return next(
        (
            path
            for path in sorted(SAMPLE_DIRECTORY.iterdir())
            if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
        ),
        None,
    )


def _print_safe_summary(result: dict[str, Any]) -> None:
    metadata = result.get("metadata") or {}
    meal = result.get("meal_analysis") or {}
    nutrition = meal.get("estimated_nutrition") or {}
    safety = result.get("safety") or {}

    print(f"status: {result.get('status')}")
    print(f"message: {result.get('message')}")
    print(f"metadata.demo_mode: {metadata.get('demo_mode')}")
    if meal:
        print(f"meal.title: {meal.get('title')}")
        print(f"meal.recommendation: {meal.get('recommendation')}")
        print(f"nutrition.calories: {nutrition.get('calories')}")
        print(f"nutrition.carbohydrates_g: {nutrition.get('carbohydrates_g')}")
        print(f"nutrition.protein_g: {nutrition.get('protein_g')}")
    if safety:
        print(f"safety.passed: {safety.get('passed')}")
    print(f"metadata.latency_seconds: {metadata.get('latency_seconds')}")


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env")
    os.environ["DEMO_MODE"] = "false"

    if not os.getenv("OPENAI_API_KEY", "").strip():
        print("OPENAI_API_KEY is missing; live smoke test was not run.")
        return 1

    image_path = _first_sample_image()
    if image_path is None:
        print("No supported public sample image was found.")
        return 1

    try:
        result = analyze_meal_image(str(image_path))
    except Exception:
        print("Live smoke test failed before a structured result was returned.")
        return 1

    _print_safe_summary(result)
    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
