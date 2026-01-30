import os
from google import genai
from app.core.config import settings
from typing import Dict, Any

client = genai.Client(api_key=settings.gemini_api_key)

async def process_ai_action(request: Dict[str, Any]) -> str:
    """
    Procesa la acción de IA basada en el request
    """
    action = request.get("action", "").lower()
    text = request.get("text", "")
    payload = request.get("payload")
    
    prompt = build_prompt(action, text, payload)
    
    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        
        # Para el MVP, podríamos guardar logs simples
        await log_usage(request, response.text)
        
        return response.text
        
    except Exception as e:
        # Manejo específico de errores de Gemini
        if "quota" in str(e).lower():
            raise Exception("Límite de uso excedido. Por favor, intente más tarde.")
        elif "safety" in str(e).lower():
            raise Exception("El contenido no pudo ser procesado por políticas de seguridad.")
        else:
            raise Exception(f"Error en el procesamiento de IA: {str(e)}")

def build_prompt(action: str, text: str, payload: str = None) -> str:
    """
    Construye el prompt según la acción solicitada
    """
    action_map = {
        "summarize": "summarize",
        "resumir": "summarize",
        "explain": "explain",
        "explicar": "explain",
        "rewrite": "rewrite",
        "reescribir": "rewrite",
        "translate": "translate",
        "traducir": "translate",
        "xray": "analyze",
        "analizar": "analyze"
    }
    
    normalized_action = action_map.get(action.lower(), action)
    
    prompts = {
        "summarize": f"""
        Resume el siguiente texto de manera concisa y clara, preservando los puntos principales.
        
        TEXTO:
        {text}
        
        RESUMEN:
        """,
        
        "explain": f"""
        Explica el siguiente texto de manera simple y clara, como si se lo explicaras a alguien que no está familiarizado con el tema.
        
        TEXTO:
        {text}
        
        EXPLICACIÓN:
        """,
        
        "rewrite": build_rewrite_prompt(text, payload),
        
        "translate": build_translate_prompt(text, payload),
        
        "analyze": build_xray_prompt(text)
    }
    
    return prompts.get(normalized_action, prompts["summarize"])

def build_rewrite_prompt(text: str, tone: str = None) -> str:
    """
    Construye prompt para reescritura según tono
    """
    tone_map = {
        "formal": "formal y profesional",
        "conciso": "concisa y directa",
        "casual": "coloquial y casual",
        "texto": "adaptada para mensajes de texto",
        None: "mejorada manteniendo el significado original"
    }
    
    tone_desc = tone_map.get(tone, tone_map[None])
    
    return f"""
    Reescribe el siguiente texto en un tono {tone_desc}. Mantén el significado original pero mejora la claridad y fluidez.
    
    TEXTO ORIGINAL:
    {text}
    
    TEXTO REESCRITO:
    """

def build_translate_prompt(text: str, language: str = "es") -> str:
    """
    Construye prompt para traducción
    """
    language_map = {
        "es": "español",
        "en": "inglés",
        "fr": "francés",
        "de": "alemán",
        "it": "italiano",
        "pt": "portugués"
    }
    
    target_lang = language_map.get(language.lower(), "español")
    
    return f"""
    Traduce el siguiente texto al {target_lang}. Mantén el tono, estilo y significado original.
    
    TEXTO ORIGINAL:
    {text}
    
    TRADUCCIÓN ({target_lang.upper()}):
    """

def build_xray_prompt(text: str) -> str:
    """
    Construye prompt para análisis X-ray (análisis de errores)
    """
    return f"""
    Analiza el siguiente texto y proporciona un análisis detallado de posibles mejoras en formato JSON:
    
    1. **Errores gramaticales**: Lista de errores con correcciones
    2. **Errores de estilo**: Sugerencias para mejorar claridad y fluidez
    3. **Sugerencias de vocabulario**: Palabras alternativas más precisas
    4. **Puntuación general** (1-10): Con sugerencias de mejora
    
    TEXTO:
    {text}
    
    ANÁLISIS (en formato JSON):
    {{
      "grammar_errors": [],
      "style_errors": [],
      "vocabulary_suggestions": [],
      "overall_score": 0,
      "improvement_suggestions": []
    }}
    """

async def log_usage(request: Dict[str, Any], response: str):
    """
    Guarda logs de uso (simple para MVP)
    """
    # Por ahora solo imprimimos, luego conectaremos a Supabase
    print(f"[AI USAGE] Action: {request.get('action')}, Chars: {len(request.get('text', ''))}")