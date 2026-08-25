# CarbKind AI Product Vision

CarbKind AI is a carb-aware food decision assistant. It starts with an intentionally small interaction—add a photo or list available ingredients—but is designed to connect food understanding, practical meal composition, and consented personalization.

## Problem

Meals are often difficult to estimate by sight, especially when they are home-cooked, mixed on one plate, culturally specific, improvised, or adapted to personal taste. A recipe name alone rarely explains what is actually in an individual serving.

For someone paying attention to carbohydrates or glucose impact, useful questions include:

- Which ingredients are likely present?
- Which parts of the meal contribute most of the carbohydrates?
- Would a different portion balance be helpful?
- Could an ingredient be replaced with something that better fits the person's preferences?

CarbKind AI aims to make those questions easier to explore. Its estimates are informational and approximate; the product does not diagnose conditions, treat diabetes, or replace medical advice.

## Product goal

The core experience should remain straightforward:

1. Upload a meal photo.
2. Receive a clear meal summary.
3. Review approximate calories, carbohydrates, and protein.
4. See likely ingredients and the main carbohydrate sources.
5. Read a concise carb-watch note.
6. Consider one practical portion suggestion.

The interface should reduce the effort required to interpret a meal, while being honest about what cannot be known from an image alone.

## The product system

CarbKind connects three complementary capabilities:

- **Photo Analyzer understands what users eat.** It identifies likely ingredients, the main carb source, rough nutrition ranges, and visible uncertainty.
- **Meal Memory stores consented structured food patterns.** It can represent recurring foods, avoided ingredients, cuisine patterns, common carb sources, and confirmed preferences without silently turning observations into rules.
- **Meal Composer helps users decide what to cook next.** It combines available ingredients, time, ingredient roles, and optional goals to suggest one practical meal and useful substitutions.

Together they form a convergence loop:

```text
observe → learn → suggest → cook → observe again
```

A user can begin anywhere: check a plate, compose a meal, or revisit a confirmed pattern. Each useful interaction should reduce future effort while preserving consent, uncertainty, and user control.

## Design principle: consumer first

CarbKind AI is designed for quick understanding rather than technical inspection. The product uses simple language, a polished dark interface, minimal cognitive load, and a clear visual hierarchy inspired by familiar consumer applications. A normal user should be able to understand the key result in seconds.

Structured data remains available to developers, but raw JSON stays behind an advanced control so it does not compete with the primary experience.

## Safety principle

Every result should communicate appropriate limits:

- Nutrition and ingredient estimates are approximate.
- The product does not provide diagnosis or medical advice.
- It does not recommend insulin, medication, or dosing changes.
- It does not label a meal safe or unsafe for a particular person.
- Uncertainty should be visible rather than hidden behind confident wording.

Future personalization should improve relevance without turning uncertain image estimates into medical claims.

## Near-term roadmap

- Maintain a deterministic demo mode for safe, accessible product exploration.
- Improve live multimodal analysis while preserving the structured safety pipeline.
- Introduce a provider abstraction so model backends can be evaluated consistently.
- Continue refining accessibility, responsive behavior, and consumer-facing clarity.
- Publish a public Hugging Face demo with transparent mode and safety messaging.

## Long-term roadmap

- **Personal meal memory:** recognize patterns across meal examples a user chooses to save.
- **User-owned food-photo profile:** learn common cuisines, ingredients, portions, and preferences with explicit consent.
- **Recipe and ingredient factorization:** understand a meal as components and functional roles, not only as a recipe name.
- **Substitution engine:** recommend practical alternatives based on function, cuisine, availability, dietary needs, and carb impact.
- **Personalization and optional fine-tuning:** begin with retrieval and only evaluate training approaches when they add measurable value.
- **Carb-aware meal composer:** turn available ingredients and user preferences into explainable meal ideas with rough nutrition estimates.

The long-term vision is not a one-time calorie lookup. It is an understandable, user-controlled assistant that helps people reason about the meals they actually eat.
