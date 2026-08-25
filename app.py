"""Minimal Gradio scaffold for NutriLens AI."""

import gradio as gr


PLACEHOLDER_MESSAGE = (
    "Demo scaffold is ready. The analysis pipeline will be added in the next "
    "development task."
)


def analyze_meal(_image: object) -> str:
    """Return the scaffold response without calling an external service."""
    return PLACEHOLDER_MESSAGE


with gr.Blocks(title="NutriLens AI") as demo:
    gr.Markdown("# NutriLens AI")
    gr.Markdown(
        "Upload a meal image to get a structured, safety-reviewed nutrition "
        "estimate."
    )
    gr.Markdown("**Safety note:** Nutrition estimates are approximate and are not medical advice.")

    meal_image = gr.Image(type="pil", label="Meal image")
    analyze_button = gr.Button("Analyze", variant="primary")
    result = gr.Textbox(label="Analysis", interactive=False)

    analyze_button.click(fn=analyze_meal, inputs=meal_image, outputs=result)


if __name__ == "__main__":
    demo.launch()
