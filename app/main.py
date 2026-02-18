import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai

# Load env vars (Railway injects them automatically)
load_dotenv()

# Init Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="AI Legal Mexico API")

# ---- Hardcoded Legal Persona ----
SYSTEM_PROMPT = """
Eres un abogado especialista en derecho mexicano.

REGLAS:
- Responde SIEMPRE en español.
- Respuestas cortas, claras y específicas.
- Explica de forma híbrida: técnica + fácil de entender.
- SIEMPRE indica de dónde proviene la información.
- Cita leyes mexicanas cuando sea posible (Constitución, LFT, Código Civil, SAT, etc).
- Si no estás seguro, dilo claramente.

Formato obligatorio:

Respuesta:
<explicación>

Fuente legal:
<leyes, normas o instituciones mexicanas>
"""

class Question(BaseModel):
    question: str


@app.get("/")
def health():
    return {"status": "running"}

@app.post("/ask")
def ask_ai(q: Question):
    try:
        prompt = f"{SYSTEM_PROMPT}\n\nPregunta: {q.question}"

        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )

        return {
            "question": q.question,
            "answer": response.text
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
