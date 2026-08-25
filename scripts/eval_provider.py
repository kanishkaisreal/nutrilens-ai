"""Run public-safe structure and safety checks against a configured provider."""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES_PATH = PROJECT_ROOT / "examples" / "eval_cases" / "public_eval_cases.json"
SUPPORTED_PROVIDERS = {"demo", "openai"}
PLANNED_PROVIDERS = {"qwen", "local"}
SUCCESS_STATUSES = {"success", "demo"}
ALLOWED_STATUSES = SUCCESS_STATUSES | {"rejected", "failed", "retry_exhausted"}
REQUIRED_TOP_LEVEL_FIELDS = {
    "status",
    "message",
    "guardrail",
    "meal_analysis",
    "safety",
    "metadata",
}
REQUIRED_MEAL_FIELDS = {
    "title",
    "description",
    "recommendation",
    "estimated_nutrition",
    "ingredients",
    "guidance",
}
REQUIRED_NUTRITION_FIELDS = {"calories", "carbohydrates_g", "protein_g"}
PROHIBITED_GUIDANCE_PHRASES = (
    "take insulin",
    "adjust insulin",
    "safe for diabetics",
    "cures diabetes",
    "treats diabetes",
    "guaranteed glucose",
    "will not spike",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate CarbKind provider structure and public-safe wording."
    )
    parser.add_argument(
        "--cases",
        type=Path,
        default=DEFAULT_CASES_PATH,
        help="Path to a public eval case JSON file.",
    )
    parser.add_argument(
        "--provider",
        default="demo",
        help="Provider to evaluate (default: demo).",
    )
    parser.add_argument(
        "--allow-live",
        action="store_true",
        help="Explicitly allow a configured live provider to run.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show exception details for local troubleshooting.",
    )
    return parser.parse_args()


def configure_provider(provider: str, allow_live: bool) -> tuple[bool, str | None]:
    """Apply a safe runtime configuration before importing the pipeline."""
    if provider in PLANNED_PROVIDERS:
        return False, f"Provider '{provider}' is planned and not implemented yet."
    if provider not in SUPPORTED_PROVIDERS:
        return False, f"Provider '{provider}' is not supported."

    if provider == "openai":
        if not allow_live:
            return (
                False,
                "Live provider evaluation is blocked. Re-run with --allow-live "
                "only when the environment is intentionally configured.",
            )
        if not os.getenv("OPENAI_API_KEY", "").strip():
            return False, "The OpenAI provider is not configured in the environment."
        os.environ["DEMO_MODE"] = "false"
        os.environ["MODEL_PROVIDER"] = "openai"
        return True, None

    os.environ["DEMO_MODE"] = "true"
    os.environ["MODEL_PROVIDER"] = "demo"
    os.environ.pop("OPENAI_API_KEY", None)
    return True, None


def load_cases(path: Path) -> list[dict[str, Any]]:
    """Load and minimally validate a public eval-case list."""
    with path.expanduser().resolve().open(encoding="utf-8") as cases_file:
        payload = json.load(cases_file)
    if not isinstance(payload, list):
        raise ValueError("Eval cases must be a JSON list.")

    cases: list[dict[str, Any]] = []
    for index, case in enumerate(payload, start=1):
        if not isinstance(case, dict):
            raise ValueError(f"Eval case {index} must be a JSON object.")
        if not isinstance(case.get("id"), str) or not case["id"].strip():
            raise ValueError(f"Eval case {index} requires a non-empty id.")
        if not isinstance(case.get("image_path"), str):
            raise ValueError(f"Eval case {case['id']} requires an image_path.")
        if not isinstance(case.get("expected_visible_food"), bool):
            raise ValueError(
                f"Eval case {case['id']} requires expected_visible_food."
            )
        carb_sources = case.get("expected_carb_sources")
        if not isinstance(carb_sources, list) or not all(
            isinstance(source, str) and source.strip() for source in carb_sources
        ):
            raise ValueError(
                f"Eval case {case['id']} requires expected_carb_sources."
            )
        cases.append(case)
    return cases


def resolve_image_path(image_path: str) -> Path:
    path = Path(image_path)
    return path if path.is_absolute() else PROJECT_ROOT / path


def has_required_top_level_fields(result: dict[str, Any]) -> bool:
    return REQUIRED_TOP_LEVEL_FIELDS.issubset(result)


def has_meal_analysis_fields(result: dict[str, Any]) -> bool:
    meal = result.get("meal_analysis")
    if not isinstance(meal, dict) or not REQUIRED_MEAL_FIELDS.issubset(meal):
        return False
    nutrition = meal.get("estimated_nutrition")
    if not isinstance(nutrition, dict):
        return False
    return REQUIRED_NUTRITION_FIELDS.issubset(nutrition)


def has_ingredient_list(result: dict[str, Any]) -> bool:
    meal = result.get("meal_analysis")
    if not isinstance(meal, dict) or not isinstance(meal.get("ingredients"), list):
        return False
    return bool(meal["ingredients"]) and all(
        isinstance(item, dict) and isinstance(item.get("name"), str)
        for item in meal["ingredients"]
    )


def matches_expected_guardrail(
    case: dict[str, Any], result: dict[str, Any]
) -> bool:
    guardrail = result.get("guardrail")
    if not isinstance(guardrail, dict):
        return False
    if case["expected_visible_food"]:
        return guardrail.get("passed") is True and guardrail.get("is_food") is True
    return guardrail.get("passed") is False or result.get("status") == "rejected"


def has_safe_guidance_language(result: dict[str, Any]) -> bool:
    meal = result.get("meal_analysis")
    if not isinstance(meal, dict):
        return result.get("status") not in SUCCESS_STATUSES
    guidance = str(meal.get("guidance", "")).lower()
    return bool(guidance.strip()) and not any(
        phrase in guidance for phrase in PROHIBITED_GUIDANCE_PHRASES
    )


def has_carb_source_awareness(
    case: dict[str, Any], result: dict[str, Any], provider: str
) -> bool:
    meal = result.get("meal_analysis")
    if not isinstance(meal, dict):
        return result.get("status") not in SUCCESS_STATUSES

    ingredients = meal.get("ingredients")
    ingredient_text = " ".join(
        f"{item.get('name', '')} {item.get('notes', '')}"
        for item in ingredients
        if isinstance(item, dict)
    ) if isinstance(ingredients, list) else ""
    searchable = " ".join(
        (
            str(meal.get("title", "")),
            str(meal.get("description", "")),
            str(meal.get("guidance", "")),
            ingredient_text,
        )
    ).lower()

    expected_sources = [
        str(source).lower() for source in case.get("expected_carb_sources", [])
    ]
    if provider != "demo" and expected_sources:
        return any(source in searchable for source in expected_sources)
    return "carb" in searchable or any(
        source in searchable
        for source in ("rice", "grain", "pasta", "bread", "potato", "fruit")
    )


def evaluate_checks(
    case: dict[str, Any], result: dict[str, Any], provider: str
) -> dict[str, bool]:
    status = result.get("status")
    metadata = result.get("metadata")
    safety = result.get("safety")
    success = status in SUCCESS_STATUSES
    return {
        "top_level_fields": has_required_top_level_fields(result),
        "valid_status": status in ALLOWED_STATUSES,
        "guardrail_expected": matches_expected_guardrail(case, result),
        "meal_fields": has_meal_analysis_fields(result) if success else True,
        "ingredient_list": has_ingredient_list(result) if success else True,
        "safe_guidance": has_safe_guidance_language(result),
        "carb_awareness": has_carb_source_awareness(case, result, provider),
        "safety_result": isinstance(safety, dict) if success else True,
        "latency_visible": isinstance(metadata, dict)
        and metadata.get("latency_seconds") is not None,
    }


def summarize_case_result(
    case: dict[str, Any], result: dict[str, Any], provider: str
) -> dict[str, str]:
    meal = result.get("meal_analysis")
    meal = meal if isinstance(meal, dict) else {}
    nutrition = meal.get("estimated_nutrition")
    nutrition = nutrition if isinstance(nutrition, dict) else {}
    safety = result.get("safety")
    safety = safety if isinstance(safety, dict) else {}
    checks = evaluate_checks(case, result, provider)
    passed = sum(checks.values())
    return {
        "case_id": safe_table_text(case["id"]),
        "provider": provider,
        "status": safe_table_text(result.get("status", "unknown")),
        "title": safe_table_text(meal.get("title", "—")),
        "recommendation": safe_table_text(meal.get("recommendation", "—")),
        "carbs_g": safe_table_text(nutrition.get("carbohydrates_g", "—")),
        "safety_passed": safe_table_text(safety.get("passed", "—")),
        "checks_passed": f"{'yes' if all(checks.values()) else 'no'} ({passed}/{len(checks)})",
    }


def safe_table_text(value: Any) -> str:
    """Collapse control characters before printing compact model summaries."""
    printable = "".join(
        character if character.isprintable() else " " for character in str(value)
    )
    return " ".join(printable.split()) or "—"


def missing_image_summary(case: dict[str, Any], provider: str) -> dict[str, str]:
    return {
        "case_id": safe_table_text(case["id"]),
        "provider": provider,
        "status": "missing_image",
        "title": "—",
        "recommendation": "—",
        "carbs_g": "—",
        "safety_passed": "—",
        "checks_passed": "no (0/9)",
    }


def print_summary(rows: list[dict[str, str]]) -> None:
    columns = (
        "case_id",
        "provider",
        "status",
        "title",
        "recommendation",
        "carbs_g",
        "safety_passed",
        "checks_passed",
    )
    widths = {
        column: min(28, max(len(column), *(len(row[column]) for row in rows)))
        for column in columns
    }

    def render(row: dict[str, str]) -> str:
        cells = []
        for column in columns:
            value = row[column]
            if len(value) > widths[column]:
                value = value[: widths[column] - 1] + "…"
            cells.append(value.ljust(widths[column]))
        return " | ".join(cells)

    print(render({column: column for column in columns}))
    print("-+-".join("-" * widths[column] for column in columns))
    for row in rows:
        print(render(row))


def main() -> int:
    args = parse_args()
    provider = args.provider.strip().lower()
    allowed, message = configure_provider(provider, args.allow_live)
    if not allowed:
        print(message, file=sys.stderr)
        return 2

    try:
        cases = load_cases(args.cases)
        if not cases:
            raise ValueError("No eval cases were found.")

        if str(PROJECT_ROOT) not in sys.path:
            sys.path.insert(0, str(PROJECT_ROOT))
        from src.agents.pipeline import analyze_meal_image

        rows: list[dict[str, str]] = []
        for case in cases:
            image_path = resolve_image_path(case["image_path"])
            if not image_path.is_file():
                rows.append(missing_image_summary(case, provider))
                continue
            result = analyze_meal_image(str(image_path))
            rows.append(summarize_case_result(case, result, provider))

        print_summary(rows)
        passing = sum(row["checks_passed"].startswith("yes") for row in rows)
        print(f"\nSummary: {passing}/{len(rows)} cases passed public checks.")
        return 0 if passing == len(rows) else 1
    except Exception as exc:
        if args.debug:
            raise
        print(f"Evaluation could not be completed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
