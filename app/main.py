from fastapi import FastAPI
import os

app = FastAPI()

print(f"🚀 Environment check:")
print(f"   PORT: {os.getenv('PORT')}")
print(f"   PWD: {os.getcwd()}")

@app.get("/")
async def root():
    return {"status": "ok", "service": "cliro-notes"}

@app.get("/health")
async def health():
    return {"status": "healthy"}