# Personalization and Recipe Factorization

The central idea behind CarbKind AI's longer-term direction is that a meal is more than a recipe label. A useful food assistant should reason about what a meal contains, what each ingredient contributes, what role it plays, and how the result relates to the user's own habits and preferences.

An intuitive representation is:

> **meal = Σ weightᵢ × ingredientᵢ + cooking style + portion context + user preferences + health goal**

The weights describe the relative contribution of ingredients rather than pretending that a photo reveals exact quantities. Cooking style and portion context change the meal; preferences and goals change which suggestions are useful.

## Why recipe names are not enough

People do not always eat standard online recipes. Meals may be home-cooked, improvised, culturally specific, adapted from family recipes, or assembled from whatever is available. Two plates with the same name can contain different ingredients, portions, sauces, and cooking methods.

Recognizing “pasta” or “curry” is therefore only a starting point. The more useful questions are what the particular plate probably contains, which components drive its nutrition, and which changes would still preserve the meal's identity.

## Ingredient decomposition

Given a meal image, a factorized system would attempt to:

- identify likely visible and inferred ingredients;
- estimate the role and relative amount of each ingredient;
- estimate each component's nutrition contribution;
- identify the main carbohydrate sources;
- represent uncertainty when ingredients are hidden or visually ambiguous.

This decomposition creates a bridge between image understanding and practical suggestions. It also makes an estimate easier to explain: a user can see which components contributed to the overall result.

## Functional ingredient roles

Ingredients should be understood by function as well as by name. Lemon, for example, may contribute acid and brightness rather than bulk. A useful substitute should preserve that role when possible:

- lemon → lime;
- lemon → vinegar;
- lemon → yogurt;
- lemon → tamarind.

These alternatives are not interchangeable in every meal. Substitution ranking should consider cuisine, expected carb impact, known allergies or dietary restrictions, availability, and the user's taste history. The system should explain the role being replaced instead of presenting a swap as universally correct.

## Carb-aware substitution

Carb-aware suggestions should focus on practical balance rather than extreme restriction. Examples include:

- reduce the rice portion and increase non-starchy vegetables;
- replace a sugary sauce with a yogurt-and-herb sauce when it fits the dish;
- describe lentils and chickpeas carefully because they contribute fiber and protein as well as carbohydrates;
- suggest pairing carbohydrate foods with protein or fiber rather than simply removing them.

These are general meal-composition ideas, not personalized medical advice or predictions of an individual's glucose response.

## Personalized meal memory

With permission, a set of roughly 10–50 user-owned meal examples could reveal recurring patterns that a generic model misses. The system might learn:

- repeated foods and cuisines;
- usual portions and plate composition;
- commonly used ingredients;
- substitutions the user accepts or rejects;
- which explanations and suggestions are most useful to that user.

Consent must be explicit. Uploads should not be used automatically for training, and a future product should let users inspect, correct, export, and delete stored meal data. Retrieval from consented examples should be the first personalization approach because its sources are easier to inspect than changes embedded in model weights.

## Meal composer concept

A future meal composer could combine:

**Input**

- available ingredients;
- a user goal or carb preference;
- consented food history;
- cuisine preferences;
- dietary constraints.

**Output**

- a practical meal idea;
- ingredient substitutions with reasons;
- a rough carb and nutrition estimate;
- an explanation of how the suggestion fits the stated constraints.

For example, suppose the available ingredients are pasta, yogurt, garlic, spinach, vinegar, and chicken. Instead of requiring a canonical lemon-pasta recipe, the composer could recognize that lemon normally provides acidity, suggest vinegar or yogurt as a context-appropriate substitute, add spinach and chicken for a different protein-and-fiber balance, and reduce the pasta portion for a lower estimated carb load.

The value comes from preserving the function and character of a meal while adapting it to real ingredients and preferences.

## Research opportunities

- **Ingredient-role embeddings:** represent what ingredients do in a dish, not only what they are called.
- **User-preference embeddings:** model accepted flavors, cuisines, textures, and substitutions with user control.
- **Substitution graph:** connect ingredients by functional role, cuisine, nutrition properties, and constraints.
- **Recipe factorization model:** estimate weighted meal components, cooking methods, and portion context.
- **Retrieval plus generation:** ground suggestions in similar consented meals before generating an answer.
- **Constraint-aware meal planning:** compose ideas that satisfy available ingredients and stated preferences.
- **Personalization without heavy fine-tuning:** test transparent retrieval and profiles first.
- **Fine-tuning after a retrieval baseline:** train only when consented evidence shows a meaningful advantage.

Recipe factorization reframes CarbKind AI from a meal-labeling tool into an explainable system for understanding, adapting, and composing the foods people actually eat.
