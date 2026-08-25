# Optional Qwen Provider

CarbKind AI includes a safe provider scaffold for experimenting with an open-source vision-language model without changing the public response contract. The target model is `Qwen/Qwen2.5-VL-3B-Instruct`, selected as a smaller first local-provider experiment.

The provider is optional. Demo mode remains the default, and normal application flow does not download model weights, initialize Qwen, or run local inference.

## Optional setup

Activate the existing conda environment and install the separate dependencies:

```bash
conda activate py312
pip install -r requirements-qwen.txt
```

Install the correct PyTorch build for your hardware separately before attempting future inference work. Local VLM inference may require significant RAM or VRAM and may download large model files.

Configure the provider explicitly:

```text
DEMO_MODE=false
MODEL_PROVIDER=qwen
QWEN_MODEL_ID=Qwen/Qwen2.5-VL-3B-Instruct
QWEN_ALLOW_LOCAL_INFERENCE=false
QWEN_DEVICE=auto
```

Run the safe readiness check:

```bash
python scripts/qwen_provider_check.py
```

This reports optional-module availability and configuration without reading a local `.env`, downloading a model, or running inference.

## Explicit local initialization check

The following flag only permits a lightweight provider initialization check when optional dependencies are already present:

```bash
python scripts/qwen_provider_check.py --allow-local-inference
```

The current scaffold still does not load model weights or run inference. A future local runner must preserve explicit opt-in, avoid automatic downloads in normal app flow, and return results through the same validated safety contract as other providers.
