import gradio as gr
import base64
import json
import mimetypes
import re
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

# ---------------- MODEL ----------------
model = init_chat_model(
    "gemini-2.5-flash",
    model_provider="google_genai"
)

# The model is instructed to return STRICT JSON so the UI can render
# structured flashcards instead of a raw markdown blob.
system_prompt = """
You are a helpful professional chef.

1. Identify the main ingredients visible in the image.
2. Suggest exactly 3 recipes that can be made using those ingredients.
3. For each recipe provide: a title, an estimated cooking time, a list of
   ingredients (with quantities if reasonable), and clear step-by-step
   instructions.

Respond with ONLY valid JSON, no markdown fences, no commentary, in
exactly this shape:

{
  "recipes": [
    {
      "title": "Recipe name",
      "time": "e.g. 25 mins",
      "ingredients": ["ingredient 1", "ingredient 2"],
      "steps": ["step 1", "step 2", "step 3"]
    },
    { ... },
    { ... }
  ]
}
"""

LOADING_HTML = """
<div class="loading-wrap">
    <div class="loading-spinner"></div>
    <p>🍳 Cooking your recipes...</p>
</div>
"""

PLACEHOLDER_HTML = """
<div class="placeholder-wrap">
    <p>🌿 Upload a photo of your ingredients and click <b>Generate Recipes</b><br>
    to see your personalized recipe cards appear here.</p>
</div>
"""

ERROR_TEMPLATE = """
<div class="placeholder-wrap">
    <p>⚠️ {message}</p>
</div>
"""


def _extract_json(raw_text):
    """Model occasionally wraps JSON in code fences — strip those if present."""
    text = raw_text.strip()
    text = re.sub(r"^```(json)?", "", text.strip(), flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text.strip()).strip()
    return json.loads(text)


def _render_cards(data):
    recipes = data.get("recipes", [])[:3]
    cards_html = []

    for idx, recipe in enumerate(recipes):
        title = recipe.get("title", f"Recipe {idx + 1}")
        time = recipe.get("time", "")
        ingredients = recipe.get("ingredients", [])
        steps = recipe.get("steps", [])

        ingredients_html = "".join(
            f"<li style='color:#1f3015 !important;'>{ing}</li>" for ing in ingredients
        )
        steps_html = "".join(
            f"<li style='color:#1f3015 !important; font-weight:600;'>{step}</li>" for step in steps
        )
        time_badge = f"<span class='time-badge'>⏱ {time}</span>" if time else ""

        card = f"""
        <div class="recipe-card" id="card-{idx}">
            <button class="card-header" onclick="this.closest('.recipe-card').classList.toggle('open'); var c=this.querySelector('.chevron'); c.style.transform = this.closest('.recipe-card').classList.contains('open') ? 'rotate(180deg)' : 'rotate(0deg)';">
                <span class="card-title">🍽️ {title}</span>
                <span class="card-meta">{time_badge}<span class="chevron">⌄</span></span>
            </button>
            <div class="card-body">
                <div class="card-body-inner">
                    <h4 style="color:#1f3015 !important;">Ingredients</h4>
                    <ul class="ingredient-list">{ingredients_html}</ul>
                    <h4 style="color:#1f3015 !important;">Steps</h4>
                    <ol class="steps-list">{steps_html}</ol>
                </div>
            </div>
        </div>
        """
        cards_html.append(card)

    return f"<div class='cards-wrap'>{''.join(cards_html)}</div>"


# ---------------- CORE FUNCTION ----------------
def identify_ingredients(image_path):
    if image_path is None:
        return ERROR_TEMPLATE.format(message="Please upload an image first.")

    mime_type, _ = mimetypes.guess_type(image_path)

    with open(image_path, "rb") as file:
        raw_binary = file.read()
        base64_bytes = base64.b64encode(raw_binary)
        image_base64 = base64_bytes.decode("utf-8")

    message = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Analyze the image and generate recipes."
                },
                {
                    "type": "image",
                    "source_type": "base64",
                    "data": image_base64,
                    "mime_type": mime_type
                }
            ]
        }
    ]

    response = model.invoke(message)

    try:
        data = _extract_json(response.text)
        return _render_cards(data)
    except (json.JSONDecodeError, AttributeError, TypeError):
        # Fallback: show the raw response so nothing is silently lost.
        safe_text = response.text.replace("<", "&lt;").replace(">", "&gt;")
        return (
            "<div class='cards-wrap'><div class='recipe-card open'>"
            "<div class='card-header'><span class='card-title'>"
            "⚠️ Could not parse structured recipes</span></div>"
            f"<div class='card-body open-static'><div class='card-body-inner'>"
            f"<pre style='white-space:pre-wrap;'>{safe_text}</pre>"
            "</div></div></div></div>"
        )


def set_loading():
    return LOADING_HTML


# ---------------- THEME ----------------
theme = gr.themes.Soft(
    primary_hue=gr.themes.Color(
        c50="#eef3ea", c100="#d9e3d1", c200="#b9caa9", c300="#99b182",
        c400="#7c9a68", c500="#62804f", c600="#4d6a3e", c700="#3c5630",
        c800="#2e4424", c900="#22341b", c950="#162512",
    ),
    neutral_hue="stone",
    font=[gr.themes.GoogleFont("Inter"), "ui-sans-serif", "system-ui", "sans-serif"],
).set(
    body_background_fill="#1f2e1b",
    body_background_fill_dark="#1f2e1b",
    block_background_fill="transparent",
    block_border_width="0px",
    block_shadow="none",
    block_label_text_color="#e8e9df",
    input_background_fill="#28391f",
    input_border_color="#3c5630",
    button_primary_background_fill="#7c9a68",
    button_primary_background_fill_hover="#92b07c",
    button_primary_text_color="#1f2e1b",
    button_large_radius="14px",
)

# ---------------- CUSTOM CSS ----------------
custom_css = """
:root {
    --sage-dark: #1f2e1b;
    --sage-panel: #28391f;
    --sage-border: #3c5630;
    --cream: #f6f1e7;
    --cream-soft: #e8e3d6;
    --card-bg: #fbf8f2;
    --card-text: #2e4424;
}

body, .gradio-container {
    background: var(--sage-dark) !important;
}

.gradio-container {
    max-width: 1080px !important;
    margin: 0 auto !important;
}

#app-header {
    text-align: center;
    padding: 40px 16px 10px 16px;
}

#app-header h1 {
    font-size: 2.3rem;
    font-weight: 800;
    color: var(--cream) !important;
    letter-spacing: -0.5px;
    margin-bottom: 6px;
}

#app-header p {
    font-size: 1.02rem;
    color: var(--cream-soft) !important;
    font-weight: 400;
    opacity: 0.85;
}

#left-panel {
    background: var(--sage-panel);
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 8px 28px rgba(0,0,0,0.25);
    border: 1px solid var(--sage-border);
}

#left-panel h4 {
    color: var(--cream) !important;
    font-weight: 600 !important;
    margin-bottom: 10px;
}

#generate-btn {
    margin-top: 14px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.2px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    box-shadow: 0 6px 18px rgba(124, 154, 104, 0.35);
}

#generate-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(124, 154, 104, 0.45);
}

.upload-hint {
    color: #b9c6ad;
    font-size: 0.85rem;
    margin-top: 8px;
}

#right-panel {
    background: var(--sage-panel);
    border-radius: 20px;
    padding: 22px;
    box-shadow: 0 8px 28px rgba(0,0,0,0.25);
    border: 1px solid var(--sage-border);
    min-height: 460px;
}

#right-panel h4 {
    color: var(--cream) !important;
    font-weight: 600 !important;
    margin-bottom: 14px;
}

/* ---------- Recipe Cards ---------- */
.cards-wrap {
    display: flex;
    flex-direction: column;
    gap: 14px;
}

.recipe-card {
    background: var(--card-bg);
    border-radius: 16px;
    box-shadow: 0 3px 14px rgba(0,0,0,0.15);
    overflow: hidden;
    transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.recipe-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 22px rgba(0,0,0,0.22);
}

.card-header {
    width: 100%;
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: transparent;
    border: none;
    cursor: pointer;
    padding: 16px 20px;
    text-align: left;
    font-family: inherit;
}

.card-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--card-text);
}

.card-meta {
    display: flex;
    align-items: center;
    gap: 10px;
}

.time-badge {
    font-size: 0.8rem;
    color: #4d6a3e;
    background: #e3ead9;
    padding: 3px 10px;
    border-radius: 999px;
    font-weight: 600;
}

.chevron {
    font-size: 1.1rem;
    color: #62804f;
    transition: transform 0.3s ease;
    display: inline-block;
}

.card-body {
    display: grid;
    grid-template-rows: 0fr;
    transition: grid-template-rows 0.35s ease;
}

.card-body.open-static {
    grid-template-rows: 1fr;
}

.recipe-card.open .card-body {
    grid-template-rows: 1fr;
}

.card-body-inner {
    overflow: hidden;
    min-height: 0;
    padding: 0 20px;
}

.recipe-card.open .card-body-inner {
    padding: 0 20px 20px 20px;
}

.card-body h4 {
    color: #2e4424 !important;
    font-weight: 700;
    font-size: 0.92rem;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    margin-top: 14px;
    margin-bottom: 8px;
    opacity: 1;
}

.ingredient-list, .steps-list {
    padding-left: 20px;
    margin: 0 0 6px 0;
}

.ingredient-list li, .steps-list li {
    color: #243a1b !important;
    line-height: 1.6;
    margin-bottom: 5px;
    font-size: 0.95rem;
}

.steps-list li {
    font-weight: 600;
}

/* ---------- Loading / Placeholder ---------- */
.loading-wrap, .placeholder-wrap {
    text-align: center;
    padding: 90px 24px;
    color: var(--cream-soft);
}

.loading-wrap p {
    font-size: 1.05rem;
    margin-top: 18px;
    color: var(--cream);
}

.loading-spinner {
    width: 38px;
    height: 38px;
    margin: 0 auto;
    border: 4px solid rgba(246, 241, 231, 0.25);
    border-top-color: var(--cream);
    border-radius: 50%;
    animation: spin 0.9s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.placeholder-wrap p {
    font-size: 0.98rem;
    line-height: 1.7;
    opacity: 0.85;
}

footer {
    display: none !important;
}

/* ---------- Responsive ---------- */
@media (max-width: 768px) {
    #app-header h1 {
        font-size: 1.7rem;
    }
    #left-panel, #right-panel {
        padding: 16px;
    }
    .card-title {
        font-size: 0.95rem;
    }
}
"""

# ---------------- UI ----------------
with gr.Blocks(theme=theme, css=custom_css, title="AI Recipe Generator") as demo:

    with gr.Column(elem_id="app-header"):
        gr.Markdown(
            """
            # 🌿 AI Recipe Generator
            Snap a photo of your ingredients and get 3 personalized recipes — instantly.
            """
        )

    with gr.Row(equal_height=False):
        with gr.Column(scale=1, elem_id="left-panel"):
            gr.Markdown("#### 📷 Upload Ingredients")
            image_input = gr.Image(
                type="filepath",
                show_label=False,
                height=280,
            )
            btn = gr.Button(
                "✨ Generate Recipes",
                variant="primary",
                elem_id="generate-btn",
                size="lg",
            )
            gr.Markdown(
                "<p class='upload-hint'>Tip: clear, well-lit photos give the best results.</p>"
            )

        with gr.Column(scale=2, elem_id="right-panel"):
            gr.Markdown("#### 👩‍🍳 Your Recipes")
            output = gr.HTML(value=PLACEHOLDER_HTML)

    btn.click(fn=set_loading, outputs=output).then(
        fn=identify_ingredients,
        inputs=image_input,
        outputs=output,
    )

demo.launch()