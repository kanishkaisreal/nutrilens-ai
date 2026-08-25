"""Shared contract for meal-analysis model providers."""

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class ProviderResult:
    """Raw provider output validated by the public pipeline."""

    guardrail: dict[str, Any] | None
    meal_analysis: dict[str, Any] | None
    safety: dict[str, Any] | None
    metadata: dict[str, Any] = field(default_factory=dict)


class MealAnalysisProvider(Protocol):
    """Minimal interface implemented by each multimodal backend."""

    name: str

    def analyze(self, image_path: str) -> ProviderResult:
        """Return raw analysis steps for pipeline validation."""
        ...
