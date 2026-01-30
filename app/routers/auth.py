from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import datetime

from app.schemas.auth import (
    WaitlistUserCreate, 
    WaitlistUserResponse, 
    WaitlistStats,
    PublicConfig
)
from app.services.auth_service import auth_service
from app.core.constants import SUPPORTED_LANGUAGES, INTEREST_REASONS, REWRITE_TONES
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["auth"])

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)

@router.post("/waitlist/join", 
             response_model=WaitlistUserResponse,
             status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def join_waitlist(request: Request, user_data: WaitlistUserCreate):
    """
    Únete a la waitlist de Cliro Notes
    """
    try:
        result = await auth_service.join_waitlist(user_data)
        
        status_code = status.HTTP_201_CREATED if result["success"] else status.HTTP_200_OK
        return JSONResponse(
            content=result,
            status_code=status_code
        )
        
    except Exception as e:
        logger.error(f"Error en /waitlist/join: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "success": False,
                "message": "Error interno del servidor",
                "error": str(e) if settings.debug else "contact_support"
            }
        )

@router.get("/waitlist/stats", response_model=WaitlistStats)
async def get_waitlist_stats():
    """
    Estadísticas públicas de la waitlist
    """
    try:
        stats = await auth_service.get_waitlist_stats()
        return stats
    except Exception as e:
        logger.error(f"Error obteniendo stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error obteniendo estadísticas"
        )

@router.get("/waitlist/check-email/{email}")
async def check_email_exists(email: str):
    """
    Verifica si un email está registrado
    """
    try:
        from app.core.security import security
        # Validar formato primero
        if not security.validate_email(email):
            return {
                "exists": False,
                "valid": False,
                "message": "Formato de email inválido"
            }
        
        user = await auth_service.get_user_by_email(email)
        return {
            "exists": user is not None,
            "valid": True,
            "message": "Email ya registrado" if user else "Email disponible",
            "position": await auth_service.calculate_waitlist_position(user["id"]) if user else None
        }
    except Exception as e:
        logger.error(f"Error verificando email: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error verificando email"
        )

@router.get("/config/public", response_model=PublicConfig)
async def get_public_config():
    """
    Configuración pública para frontend
    """
    return {
        "supported_languages": [
            {"code": lang, "name": SUPPORTED_LANGUAGES[lang]["name"]}
            for lang in SUPPORTED_LANGUAGES
        ],
        "interest_reasons": INTEREST_REASONS,
        "rewrite_tones": REWRITE_TONES,
        "max_languages": settings.max_languages_per_user,
        "version": settings.app_version
    }

@router.get("/health/db")
async def database_health():
    """
    Health check específico para base de datos
    """
    from app.db import db_manager
    try:
        is_healthy = db_manager.test_connection()
        return {
            "database": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {
            "database": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }