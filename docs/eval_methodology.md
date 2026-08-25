# CarbKind AI Evaluation Methodology

## Why evaluation matters

CarbKind AI depends on more than a plausible meal title. Each provider needs to return reliable structured data, use appropriately cautious language, and produce a summary that helps a user understand likely carbohydrate sources. A lightweight public harness makes those expectations visible and repeatable as providers evolve.

## What the current public eval checks

The current harness uses only the sample images already published in this repository. It checks:

- completeness of the structured response and meal fields;
- guardrail and result status values;
- presence of calories, carbohydrates, and protein fields;
- an ingredient list with readable names;
- carb-source cues in the meal summary or ingredients;
- guidance for obvious prohibited medical claims;
- presence of the safety result for successful responses;
- visibility of pipeline latency metadata;
- safe demo behavior and explicit opt-in for live evaluation.

The demo provider always returns one fixed sample response, so demo evaluation verifies the response contract, safety wording, and carb-aware fields—not whether each input image was individually recognized. Case-specific image expectations become meaningful when evaluating a live provider.

## What it does not claim

Passing the public checks does not establish:

- exact calorie or macronutrient accuracy;
- clinical validation;
- personalized glucose prediction;
- medical safety certification;
- full nutrition-label accuracy;
- superiority over another provider.

The cases contain descriptive expectations, not nutrition ground truth or benchmark scores.

## Provider comparison roadmap

Future provider comparisons can use the same public response contract while considering:

- structured output validity;
- safety wording;
- carbohydrate-source identification;
- ingredient plausibility;
- latency;
- cost;
- deployment complexity.

The OpenAI provider currently implements the live multimodal path. A Qwen or other open-source provider is planned, as is a local or lightweight provider; neither is implemented yet. Comparisons should disclose configuration and limitations without turning a small smoke set into a performance claim.

## Future eval expansion

Potential additions include:

- a user-owned, explicitly consented meal set;
- more culturally diverse meals;
- mixed home-cooked meals;
- portion-uncertainty cases;
- ingredient-substitution quality;
- personalized recommendation quality.

Any expansion should preserve consent, provenance, deletion controls, and clear separation between product checks and clinical evidence.
