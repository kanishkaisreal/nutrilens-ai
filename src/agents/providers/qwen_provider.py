"""Safe optional scaffold for a future local Qwen vision provider."""

from importlib.util import find_spec

from src.agents.providers.base import ProviderResult, ProviderUnavailableError
from src.runtime.config import RuntimeConfig


OPTIONAL_MODULES = ("transformers", "accelerate", "PIL", "qwen_vl_utils")
DISABLED_MESSAGE = (
    "Qwen provider is configured but optional dependencies/model weights are not "
    "installed. Install requirements-qwen.txt and run "
    "scripts/qwen_provider_check.py with explicit local-run flags."
)


class QwenProvider:
    """Represent an opt-in local Qwen backend without automatic model loading."""

    name = "qwen"

    def __init__(self, config: RuntimeConfig) -> None:
        self._config = config

    @staticmethod
    def missing_optional_modules() -> list[str]:
        """Report missing optional modules without importing heavy packages."""
        return [module for module in OPTIONAL_MODULES if find_spec(module) is None]

    def analyze(self, image_path: str) -> ProviderResult:
        """Stop safely until local inference is explicitly enabled and implemented."""
        del image_path  # This scaffold never reads, stores, or prints image data.
        if not self._config.qwen_allow_local_inference:
            raise ProviderUnavailableError(DISABLED_MESSAGE)

        missing_modules = self.missing_optional_modules()
        if missing_modules:
            raise ProviderUnavailableError(
                "Qwen local inference was explicitly enabled, but optional "
                "dependencies are not installed: "
                f"{', '.join(missing_modules)}. Install requirements-qwen.txt."
            )

        raise ProviderUnavailableError(
            "Qwen optional dependencies are available, but this safe scaffold does "
            "not load or download model weights. Prepare the model locally before "
            "adding an explicit inference runner."
        )
