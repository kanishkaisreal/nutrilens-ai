"""Report optional Qwen provider readiness without downloading or inference."""

import argparse
import os
import sys
from importlib.util import find_spec
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MODEL_ID = "Qwen/Qwen2.5-VL-3B-Instruct"
DEFAULT_DEVICE = "auto"
OPTIONAL_MODULES = ("transformers", "accelerate", "PIL", "qwen_vl_utils")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check Qwen provider readiness without model download or inference."
    )
    parser.add_argument(
        "--allow-local-inference",
        action="store_true",
        help="Permit a provider initialization check; no model is loaded or run.",
    )
    return parser.parse_args()


def _enabled(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def main() -> int:
    args = parse_args()
    if args.allow_local_inference:
        os.environ["QWEN_ALLOW_LOCAL_INFERENCE"] = "true"

    configured_allow_local = _enabled(os.getenv("QWEN_ALLOW_LOCAL_INFERENCE"))
    model_id = os.getenv("QWEN_MODEL_ID", DEFAULT_MODEL_ID).strip() or DEFAULT_MODEL_ID
    device = os.getenv("QWEN_DEVICE", DEFAULT_DEVICE).strip() or DEFAULT_DEVICE
    module_status = {
        module: find_spec(module) is not None for module in OPTIONAL_MODULES
    }

    print("Qwen provider readiness check (no download, no inference)")
    print(f"Model ID: {model_id}")
    print(f"Device: {device}")
    print(f"QWEN_ALLOW_LOCAL_INFERENCE: {configured_allow_local}")
    print(f"Explicit local-run flag provided: {args.allow_local_inference}")
    for module, available in module_status.items():
        print(f"Optional module {module}: {'available' if available else 'missing'}")

    if not args.allow_local_inference:
        print("Local initialization skipped. Pass --allow-local-inference explicitly.")
        return 0
    if not all(module_status.values()):
        print(
            "Qwen optional dependencies are not installed. Install them with "
            "pip install -r requirements-qwen.txt."
        )
        print("Full Qwen inference is intentionally not implemented yet.")
        return 1

    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    from src.agents.providers.registry import get_provider
    from src.runtime.config import AppConfig

    provider = get_provider(
        AppConfig(
            demo_mode=False,
            model_provider="qwen",
            qwen_model_id=model_id,
            qwen_allow_local_inference=True,
            qwen_device=device,
        )
    )
    print(f"Provider initialized: {provider.name}")
    print("Full Qwen inference is intentionally not implemented yet.")
    print("No model weights were downloaded and no inference was run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
