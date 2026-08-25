"""Demo-mode pipeline entry point for NutriLens AI."""

import json
from pathlib import Path
from time import perf_counter

from pydantic import ValidationError

from src.agents.schemas import NutriLensResponse, PipelineMetadata
from src.runtime.response_contract import build_failed_response, response_to_dict


DEMO_OUTPUT_PATH = (
    Path(__file__).resolve().parents[2]
    / "examples"
    / "sample_outputs"
    / "demo_meal_output.json"
)


def _failed_result(message: str, started_at: float) -> dict:
    metadata = PipelineMetadata(
        demo_mode=True,
        latency_seconds=perf_counter() - started_at,
    )
    return response_to_dict(build_failed_response(message, metadata=metadata))


def analyze_meal_image(image_path: str) -> dict:
    """Return the validated demo response for an existing local image path."""
    started_at = perf_counter()

    if not image_path or not Path(image_path).is_file():
        return _failed_result("Image path is missing or does not exist.", started_at)

    try:
        with DEMO_OUTPUT_PATH.open(encoding="utf-8") as demo_file:
            payload = json.load(demo_file)
        response = NutriLensResponse.model_validate(payload)
    except (OSError, json.JSONDecodeError, ValidationError, TypeError, ValueError):
        return _failed_result("Demo response could not be loaded.", started_at)

    metadata = response.metadata.model_copy(
        update={
            "demo_mode": True,
            "latency_seconds": perf_counter() - started_at,
        }
    )
    response = response.model_copy(update={"metadata": metadata})
    return response_to_dict(response)
