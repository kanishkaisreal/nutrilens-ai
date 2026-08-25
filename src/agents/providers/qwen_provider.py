"""Safe optional scaffold for a future local Qwen vision provider."""

from importlib.util import find_spec

from src.agents.providers.base import ProviderResult, ProviderUnavailableError
from src.runtime.config import RuntimeConfig


OPTIONAL_MODULES = ("transformers", "accelerate", "PIL", "qwen_vl_utils")
DISABLED_MESSAGE = (
    "Qwen provider is configured, but local inference is disabled. Set "
    "QWEN_ALLOW_LOCAL_INFERENCE=true only after installing optional dependencies "
    "and accepting the local model download/runtime requirements."
)
MISSING_DEPENDENCIES_MESSAGE = (
    "Qwen optional dependencies are not installed. Install them with pip install "
    "-r requirements-qwen.txt."
)
NOT_IMPLEMENTED_MESSAGE = (
    "Qwen local inference scaffold is present, but full inference is not "
    "implemented yet."
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
            raise ProviderUnavailableError(MISSING_DEPENDENCIES_MESSAGE)

        raise ProviderUnavailableError(NOT_IMPLEMENTED_MESSAGE)
