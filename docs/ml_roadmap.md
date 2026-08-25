# CarbKind AI ML Roadmap

This roadmap describes how CarbKind AI can evolve from a structured multimodal prototype into an extensible, evaluable, and optionally personalized food-understanding system. Items described as planned are future experiments, not current capabilities.

## Current pipeline

The current application follows a safety-gated flow:

```text
image → input guardrail → meal analysis → safety review → consumer result card
```

Demo mode returns a deterministic sample response without analyzing the uploaded image. Live mode uses a multimodal model pipeline to review the input, estimate a meal, and review the resulting language before display. Outputs are validated against structured schemas rather than passed directly from a model to the interface.

User images are not logged by default. The application uses a temporary image during a request and removes it afterward.

## Structured output contract

Structured schemas provide a stable contract between model output and the rest of the product. They support:

- predictable application rendering;
- explicit safety review and uncertainty fields;
- repeatable evaluation across model versions;
- consistent comparison and swapping of providers;
- future retrieval and personalization features.

As the system evolves, schema changes should remain versioned, validated, and separate from provider-specific response formats.

## Provider abstraction

The pipeline now selects backends through a small provider contract while keeping schema validation and public response construction provider-neutral. This foundation allows the same input, safety contract, and future evaluation suite to run against several backends:

- **Demo provider:** deterministic local response for interface testing.
- **OpenAI provider:** the current live multimodal path.
- **Qwen or another open-source VLM provider:** a planned experiment for portability and model comparison; it is not currently implemented.
- **Local or lightweight provider:** a future option for lower-latency, lower-cost, or privacy-sensitive use cases where model quality is sufficient.

Provider selection should not change the consumer-facing safety contract. Comparisons should use the same public evaluation dimensions and clearly disclose material capability differences.

## Evaluation roadmap

The evaluation suite should measure both model behavior and product usefulness:

- input guardrail correctness;
- nutrition-range plausibility;
- ingredient plausibility;
- main carbohydrate-source identification;
- safe and appropriately qualified wording;
- end-to-end latency;
- user-facing clarity and mode comprehension.

Nutrition plausibility is not the same as clinical accuracy. Evaluation should reward calibrated uncertainty and avoid treating a single image estimate as ground truth when portion size or ingredients are ambiguous.

## Personalization roadmap

### Stage 1: retrieval-based personalization

With explicit consent, store selected meal examples and embed their images, ingredient lists, and meal summaries. Retrieve similar prior meals at inference time and use them as context for careful estimate adjustments. This creates an auditable baseline before any user-specific training.

### Stage 2: user meal profile

Aggregate consented history into an editable profile of:

- common ingredients;
- common portion patterns;
- frequent cuisines;
- usual carbohydrate sources;
- preferred substitutions.

The profile should preserve source links to the meals that informed it, distinguish observed patterns from inferred preferences, and support export and deletion.

### Stage 3: fine-tuning or adapters

Only evaluate fine-tuning or lightweight adapters with explicit user consent and a small, curated dataset. Compare every approach against the retrieval baseline, measure whether it improves relevant estimates, and guard against overfitting to a limited set of meals.

## Safety roadmap

- Review consumer language for medical-safety boundaries.
- Improve uncertainty calibration and surface ambiguity clearly.
- Continue prohibiting medication and dosing advice.
- Do not predict glucose response without appropriate user data, validation, and careful clinical framing.
- Keep disclaimers visible without using them as a substitute for safe model behavior.
- Make retention, consent, export, and deletion controls explicit before introducing meal memory.

The technical objective is a system that becomes more useful through structure, evaluation, and user control—not through unsupported certainty.
