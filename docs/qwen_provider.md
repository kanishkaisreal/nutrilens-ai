# Optional Qwen Provider

CarbKind AI includes a safe provider scaffold for experimenting with an open-source vision-language model without changing the public response contract. The target model is `Qwen/Qwen2.5-VL-3B-Instruct`, selected as a smaller first local-provider experiment.

The provider is optional. Demo mode remains the default. The app will not download or run Qwen unless local inference is explicitly enabled in a future task.

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

This task adds the provider scaffold, not full Qwen inference. The current scaffold does not load model weights or run inference, even when the readiness flag is provided. A future local runner must preserve explicit opt-in, avoid automatic downloads in normal app flow, and return results through the same validated safety contract as other providers.
