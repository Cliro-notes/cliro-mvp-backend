from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.ai import generate_ai_response

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/")
def root():
    return {"message": "API is running"}

@app.get("/ai/")
def response(action: str, payload: str = None, userText: str = None):
    userActionJSON = {
        "action": action,
        "payload": payload,
        "userText": userText
    }
    response_text = generate_ai_response(userActionJSON)
    return {"response": response_text}
