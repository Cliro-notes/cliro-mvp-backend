import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import google.generativeai as genai

# Load ENV
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")

app = FastAPI(title="AI Legal Mexico API")

# ---- Hardcoded System Prompt ----
SYSTEM_PROMPT = """
Eres un abogado especialista en derecho mexicano.

REGLAS DE RESPUESTA:
- Responde SIEMPRE en español.
- Respuestas cortas, claras y específicas.
- Explica de forma híbrida: técnica + fácil de entender.
- SIEMPRE indica de dónde proviene la información.
- Cita leyes mexicanas cuando sea posible (ej: Código Civil Federal, Constitución, LFT, etc).
- Si no estás seguro, dilo claramente.

Formato obligatorio:

Respuesta:
<explicación>

Fuente legal:
<leyes, normas o instituciones mexicanas>
"""

# ---- Request schema ----
class Question(BaseModel):
    question: str


@app.get("/")
def root():
    return {"status": "AI Legal Mexico running"}


@app.post("/ask")
def ask_ai(q: Question):
    try:
        prompt = f"{SYSTEM_PROMPT}\n\nPregunta del usuario: {q.question}"

        response = model.generate_content(prompt)

        return {
            "question": q.question,
            "answer": response.text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
