from fastapi import APIRouter, HTTPException, Query, Request
from typing import Optional
from app.services.ai_service import process_ai_action
# from app.core.security import verify_token  # COMENTAR por ahora
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/")
async def process_ai(
    request: Request,  # Agregar request para rate limiting si lo usas
    action: str = Query(..., description="Acción a realizar: summarize, explain, rewrite, translate, xray"),
    userText: str = Query(..., description="Texto a procesar"),
    payload: Optional[str] = Query(None, description="Parámetros adicionales"),
    tone: Optional[str] = Query(None, description="Tono para rewrite: formal, concise, casual, texto"),
    language: Optional[str] = Query(None, description="Idioma para traducción: es, en, fr, de, it, pt"),
    user_id: Optional[str] = Query(None, description="ID del usuario para tracking"),
    token: Optional[str] = Query(None, description="Token de autenticación (opcional por ahora)")
):
    text = userText.strip()
    """
    Endpoint principal para procesamiento de IA
    Compatible con llamadas GET desde la extensión Chrome
    """
    try:
        # Por ahora no validamos token (para MVP)
        # if token:
        #     verify_token(token)
        
        # Construir el request en formato JSON para compatibilidad
        ai_request = {
            "action": action,
            "text": text,
            "payload": payload or tone or language,
            "user_id": user_id,
            "client_ip": request.client.host if request.client else None
        }
        
        logger.info(f"Procesando acción de IA: {action}, caracteres: {len(text)}")
        
        result = await process_ai_action(ai_request)
        return {
            "success": True,
            "result": result,
            "action": action,
            "metadata": {
                "chars_processed": len(text),
                "action_type": action,
                "language": language or "auto"
            }
        }
        
    except Exception as e:
        logger.error(f"Error en proceso de IA: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail={
                "success": False,
                "error": str(e) if settings.debug else "Error en procesamiento",
                "action": action
            }
        )

@router.get("/actions")
async def get_available_actions():
    """
    Devuelve las acciones disponibles para la extensión
    """
    from app.core.constants import AI_ACTIONS, REWRITE_TONES
    return {
        "actions": list(AI_ACTIONS.values()),
        "rewrite_tones": REWRITE_TONES,
        "supported_languages": ["es", "en", "fr", "de", "it", "pt"]
    }

@router.get("/test")
async def test_ai():
    """Endpoint de prueba para IA"""
    return {
        "status": "ok",
        "message": "Servicio de IA funcionando",
        "timestamp": datetime.utcnow().isoformat()
    }