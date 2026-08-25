"""Small OpenAI Responses API helpers for image-based JSON calls."""

import base64
import json
from pathlib import Path
from typing import Any

from openai import OpenAI


IMAGE_MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


def encode_image_as_data_url(image_path: str) -> str:
    """Read a local image and return an in-memory base64 data URL."""
    path = Path(image_path)
    mime_type = IMAGE_MIME_TYPES.get(path.suffix.lower(), "image/jpeg")
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def extract_output_text(response: object) -> str:
    """Extract text from an SDK response without assuming one SDK shape."""
    output_text = getattr(response, "output_text", None)
    if isinstance(output_text, str) and output_text.strip():
        return output_text.strip()

    output = getattr(response, "output", None)
    for item in output if isinstance(output, list) else []:
        content = getattr(item, "content", None)
        for block in content if isinstance(content, list) else []:
            text = getattr(block, "text", None)
            if isinstance(text, str) and text.strip():
                return text.strip()

    raise ValueError("The model response did not contain text output.")


def _parse_json_object(output_text: str) -> dict[str, Any]:
    """Parse a JSON object and reject non-object model output."""
    text = output_text.strip()
    if text.startswith("```") and text.endswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError("The model response was not valid JSON.") from exc
    if not isinstance(parsed, dict):
        raise ValueError("The model response must be a JSON object.")
    return parsed


def call_vision_json_model(
    image_path: str,
    prompt: str,
    model: str,
) -> dict[str, Any]:
    """Call a vision-capable model and return its parsed JSON object."""
    client = OpenAI()
    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {
                        "type": "input_image",
                        "image_url": encode_image_as_data_url(image_path),
                        "detail": "auto",
                    },
                ],
            }
        ],
        store=False,
    )
    return _parse_json_object(extract_output_text(response))
