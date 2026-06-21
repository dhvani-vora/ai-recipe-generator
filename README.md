# AI-Recipe-Generator
## Overview

This project is a command-line AI application that analyzes food images and generates:
- A list of detected ingredients
- Three recipe suggestions based on those ingredients

It uses Google Gemini 2.5 Flash through LangChain to interpret images and generate structured cooking ideas.

---

## Features

- Accepts a local image input
- Converts image to Base64 format for model processing
- Uses a system prompt to define AI behavior as a chef
- Extracts ingredients from the image
- Generates three structured recipe suggestions
- Runs as a lightweight command-line application (CLI)

---

## How It Works

1. The user provides an image path in the code
2. The image is read in binary format
3. It is encoded into Base64
4. A system prompt defines the AI as a helpful chef
5. The image and prompt are sent to Gemini 2.5 Flash via LangChain
6. The model returns:
   - Identified ingredients
   - Three recipe suggestions based on those ingredients

---

## Project Structure
```text
recipe-generator/
│
├── recipe_cli.py
├── images/
│ └── ingredients.jpg
├── .env
├── requirements.txt
└── README.md
```


---

## Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/dhvani-vora/AI-Image-Recipe-Generator.git
cd AI-Image-Recipe-Generator
```


### 2. Create virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate (Windows)
source venv/bin/activate (Mac/Linux)
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add API key

Create a `.env` file in the root directory:

```env
GOOGLE_API_KEY=your_api_key_here
```

---

## How to Run

Run the script using:

```bash
python recipe_cli.py
```

Make sure the image path inside the script points to a valid image file.

---

## Future Improvements

Planned enhancements:

- Web interface using Flask or Gradio
- Image upload via browser
- Camera input support
- Step-by-step cooking instructions generation
- Nutrition analysis of recipes
- Multiple cuisine filtering options

---

## Tech Stack

- Python
- LangChain
- Google Gemini 2.5 Flash
- Base64 encoding
- dotenv

---

## Notes

- This is a learning project built to understand multimodal AI systems
- The system uses prompt engineering to guide multimodal reasoning (image + text input).
- Image interpretation and recipe generation are handled in a single pipeline

---
