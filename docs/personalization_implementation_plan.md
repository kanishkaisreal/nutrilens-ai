# Personalization Implementation Plan

## What exists now

CarbKind AI now includes a small, public code foundation for exploring personalization and recipe factorization:

- Pydantic schemas for a consented personal meal profile and summarized meal memory;
- a transparent ingredient-role map;
- functional substitution rules based on shared ingredient roles;
- a deterministic meal-composer prototype;
- a local demonstration script that uses fixed ingredient names and makes no model calls.

This foundation does not store user data, retain uploaded images, or train a model. The schemas describe possible future data contracts; they do not imply that the current application has persistence or personalization enabled.

## Why start with retrieval and rules before fine-tuning

Small personal datasets are noisy. A collection of 10–50 consented meal photos may be useful for memory and retrieval, but it is unlikely to support robust user-specific fine-tuning by itself. Portions, lighting, recipes, and meal composition can vary even within one person's history.

Rules and retrieval provide an interpretable baseline. A user or developer can inspect which prior meals were retrieved, which ingredient role caused a substitution, and why a suggestion was generated. This makes errors easier to correct and creates a measurable comparison point for any later training experiment.

Fine-tuning should be considered only after a clean, consented dataset exists and retrieval quality has been evaluated. Any trained approach should demonstrate a clear benefit over that baseline without overfitting a small set of meals.

## Future stages

### Stage 1: manual and consented meal memory

Let users deliberately save structured meal summaries, correct ingredient names, and mark which entries may be used for personalization. Keep raw image retention separate and optional.

### Stage 2: retrieval-based personalization

Retrieve similar consented meals and use their ingredients, portion patterns, cuisines, and accepted suggestions as explainable context. Preserve links from profile signals back to their source meals.

### Stage 3: ingredient substitution graph

Expand the role map into a reviewed graph connecting ingredients by function, cuisine, availability, dietary constraints, and approximate carb impact. Keep recommendations contextual rather than universal.

### Stage 4: provider and model comparison

Evaluate whether different multimodal providers produce consistent ingredient decomposition, role assignments, uncertainty language, and substitution inputs under the same schemas.

### Stage 5: optional fine-tuning or adapters

Only evaluate training with explicit consent, sufficient curated examples, strong deletion controls, and a retrieval baseline. Measure generalization and avoid treating a small personal history as complete nutrition evidence.

## Privacy and consent

- Uploads must not be used automatically for training.
- Personalization requires explicit, understandable user consent.
- Export and deletion should be first-class parts of any future product.
- Raw images should not be persisted unless the user has specifically consented.
- Structured memories should distinguish user-provided facts from inferred fields.
- Turning off personalization should not prevent use of the core meal-analysis experience.

The current prototype remains storage-free and operates only on data supplied directly to its in-memory functions.
