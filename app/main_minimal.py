from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import List
import uvicorn

app = FastAPI(title="Cliro Notes - Minimal")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelo simple para waitlist
class WaitlistUser(BaseModel):
    email: EmailStr
    name: str
    interest_reason: str
    preferred_languages: List[str]

@app.get("/")
def root():
    return {"message": "API funcionando", "status": "ok"}

@app.post("/waitlist/join")
async def join_waitlist(user: WaitlistUser):
    return {
        "success": True,
        "message": "Registro exitoso",
        "user_id": 1,
        "waitlist_position": 1
    }

@app.get("/ai/process")
async def process_ai(
    action: str,
    text: str,
    tone: str = None,
    language: str = None
):
    return {
        "success": True,
        "result": f"Procesado: {action} - {text[:50]}...",
        "action": action
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)