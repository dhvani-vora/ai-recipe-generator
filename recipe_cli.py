import base64
import mimetypes
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()

image_path = "images/ingredients.jpg"

mime_type, _ = mimetypes.guess_type(image_path)

with open(image_path, "rb") as file:
    raw_binary = file.read()

base64_bytes = base64.b64encode(raw_binary)
image_base64 = base64_bytes.decode("utf-8")

system_prompt = """
You are a helpful chef.
1. Identify the main ingredients in the image.
2. Suggest 3 recipes based on those ingredients.
Be clear and structured.
"""

model = init_chat_model(
    "gemini-2.5-flash",
    model_provider="google_genai"
)

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
                "text": "Describe what you see in this image. Analyze it."
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
print(response.text())
