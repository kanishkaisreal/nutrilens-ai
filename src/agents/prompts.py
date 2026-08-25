"""Public-safe prompts for the live NutriLens agent pipeline."""


GUARDRAIL_PROMPT = """
Review the uploaded image before meal analysis. Decide whether it is a clear,
appropriate food or meal image. Reject non-food images, blank or unreadable
images, and unsafe or inappropriate images. Do not identify people and do not
make medical claims.

Return JSON only, with exactly this shape:
{
  "passed": true,
  "is_valid_image": true,
  "is_food": true,
  "blocked_reason": null,
  "confidence": 0.9
}
Set passed to false when the image should not continue. Keep blocked_reason
brief, neutral, and suitable for display to the user.
""".strip()


MEAL_ANALYSIS_PROMPT = """
Analyze only the food visibly supported by the uploaded meal image. Return a
consumer-friendly, carb-aware nutrition estimate. Be explicit about visual
uncertainty and never present estimated values as measured facts. Do not give a
diagnosis, medication advice, insulin advice, or say that a meal is safe or
unsafe for people with diabetes. Always mention that estimates are approximate.

Return JSON only, matching exactly this shape and using only
green, yellow, orange, red, or unknown for label fields:
{
  "title": "...",
  "description": "...",
  "recommendation": "green|yellow|orange|red|unknown",
  "estimated_nutrition": {
    "calories": 420,
    "protein_g": 32,
    "carbohydrates_g": 38,
    "fat_g": 14,
    "fiber_g": 6,
    "sugar_g": 5,
    "sodium_mg": 620
  },
  "ingredients": [
    {
      "name": "...",
      "impact": "green|yellow|orange|red|unknown",
      "notes": "..."
    }
  ],
  "guidance": "...",
  "uncertainty_notes": "..."
}
Keep guidance simple, useful, and careful for someone watching carbohydrate
intake or glucose impact without making medical claims.
""".strip()


SAFETY_PROMPT = """
Review the meal analysis and guidance supplied below before it is shown to a
user. Flag medical claims, medication or insulin advice, claims that a meal is
safe or unsafe for people with diabetes, overstated visual certainty, or
dangerous nutrition advice. If anything is flagged, provide complete replacement
guidance that is safer, careful, consumer-friendly, and clear that image-based
estimates are approximate.

Return JSON only, with exactly this shape:
{
  "passed": true,
  "reasons": [],
  "revised_guidance": null
}
When passed is false, explain the issues briefly in reasons and populate
revised_guidance whenever the guidance can be safely revised.
""".strip()
