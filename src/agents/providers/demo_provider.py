"""Deterministic provider used for the public demo experience."""

import json
from pathlib import Path
from typing import Any

from src.agents.providers.base import ProviderResult


DEMO_OUTPUT_PATH = (
    Path(__file__).resolve().parents[3]
    / "examples"
    / "sample_outputs"
    / "demo_meal_output.json"
)


def _optional_mapping(payload: dict[str, Any], field: str) -> dict[str, Any] | None:
    value = payload.get(field)
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError(f"Demo field '{field}' must be an object.")
    return value


class DemoProvider:
    """Load the fixed sample result without making a model request."""

    name = "demo"

    def analyze(self, image_path: str) -> ProviderResult:
        del image_path  # The fixed demo response never analyzes the uploaded image.
        with DEMO_OUTPUT_PATH.open(encoding="utf-8") as demo_file:
            payload = json.load(demo_file)
        if not isinstance(payload, dict):
            raise ValueError("Demo response must be a JSON object.")

        metadata = _optional_mapping(payload, "metadata") or {}
        return ProviderResult(
            guardrail=_optional_mapping(payload, "guardrail"),
            meal_analysis=_optional_mapping(payload, "meal_analysis"),
            safety=_optional_mapping(payload, "safety"),
            metadata={**metadata, "demo_mode": True},
        )
