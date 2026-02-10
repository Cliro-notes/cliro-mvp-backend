from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.routers import auth, ai
from app.core.config import settings
import logging
from datetime import datetime

import os
import logging

# Add startup logging
logging.info(f"Starting app with PORT={os.getenv('PORT')}")
logging.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")

# Configuración de logging
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title=settings.app_name,
    description="Backend para Cliro Notes - Extensión de Chrome",
    version="1.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Rate Limiter global
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS Configuration usando la lista convertida
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(auth.router, prefix="/api/auth")
app.include_router(ai.router, prefix="/api/ai")

@app.get("/")
@limiter.limit("30/minute")
async def root(request: Request):
    """Endpoint raíz"""
    return {
        "message": "Bienvenido a Cliro Notes API",
        "version": settings.app_version,
        "environment": settings.environment.value,
        "docs": "/docs" if settings.debug else None,
        "endpoints": {
            "auth": "/api/auth",
            "ai": "/api/ai"
        }
    }

@app.get("/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    """Health check para monitoreo"""
    from app.db import db_manager
    try:
        # Verificar conexión a Supabase
        db_manager.test_connection()
        return {
            "status": "healthy",
            "database": "connected",
            "environment": settings.environment.value,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e) if settings.debug else "connection_error",
            "timestamp": datetime.utcnow().isoformat()
        }
        
if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings
    
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=False,
        workers=1
    )