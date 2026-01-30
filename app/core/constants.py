"""
Constantes y configuraciones estáticas del sistema.
Para datos que cambian raramente, es mejor tenerlos en código.
"""

# Idiomas soportados - MEJOR EN CÓDIGO
SUPPORTED_LANGUAGES = {
    "es": {"code": "es", "name": "Español", "native": "Español"},
    "en": {"code": "en", "name": "English", "native": "English"},
    "fr": {"code": "fr", "name": "French", "native": "Français"},
    "de": {"code": "de", "name": "German", "native": "Deutsch"},
    "it": {"code": "it", "name": "Italian", "native": "Italiano"},
    "pt": {"code": "pt", "name": "Portuguese", "native": "Português"},
    # Podemos agregar más después
}

# Razones de interés predefinidas - EN CÓDIGO (fácil de cambiar)
INTEREST_REASONS = [
    {"id": "productivity", "label": "🚀 Mejora mi productividad"},
    {"id": "writing", "label": "✍️ Mejora mi escritura profesional"},
    {"id": "learning", "label": "🧠 Ayuda a aprender idiomas"},
    {"id": "content", "label": "📝 Creación de contenido"},
    {"id": "students", "label": "🎓 Soy estudiante/investigador"},
    {"id": "business", "label": "💼 Uso empresarial/equipos"},
    {"id": "accessibility", "label": "♿ Mejora accesibilidad"},
    {"id": "other", "label": "❔ Otra razón"}
]

# Tones para reescritura
REWRITE_TONES = [
    {"id": "formal", "label": "🎩 Formal", "description": "Profesional y respetuoso"},
    {"id": "concise", "label": "⚡ Conciso", "description": "Directo y al punto"},
    {"id": "casual", "label": "😊 Casual", "description": "Coloquial y amigable"},
    {"id": "text", "label": "💬 Texto", "description": "Para mensajes rápidos"}
]

# Acciones de IA disponibles
AI_ACTIONS = {
    "summarize": {"id": "summarize", "label": "Resumir", "requires_payload": False},
    "explain": {"id": "explain", "label": "Explicar", "requires_payload": False},
    "rewrite": {"id": "rewrite", "label": "Reescribir", "requires_payload": True},
    "translate": {"id": "translate", "label": "Traducir", "requires_payload": True},
    "xray": {"id": "xray", "label": "Análisis X-Ray", "requires_payload": False}
}