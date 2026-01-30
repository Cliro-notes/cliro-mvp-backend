from pydantic import BaseModel, EmailStr, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
import re

class WaitlistUserBase(BaseModel):
    """Esquema base para waitlist"""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)
    interest_reason: str = Field(...)
    
    @validator('name')
    def validate_name(cls, v):
        """Valida nombre"""
        v = v.strip()
        if not v or len(v) < 2:
            raise ValueError("Nombre demasiado corto")
        if any(char.isdigit() for char in v):
            raise ValueError("El nombre no puede contener números")
        if not re.match(r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s\-\'\.]+$', v):
            raise ValueError("Nombre contiene caracteres inválidos")
        return v
    
    @validator('interest_reason')
    def validate_interest_reason(cls, v):
        """Valida que la razón sea una de las predefinidas"""
        # Razones válidas directamente en el código para evitar imports
        valid_reasons = [
            "productivity", "writing", "learning", "content", 
            "students", "business", "accessibility", "other"
        ]
        if v not in valid_reasons:
            raise ValueError(f"Razón inválida. Opciones: {', '.join(valid_reasons)}")
        return v

class WaitlistUserCreate(WaitlistUserBase):
    """Esquema para creación con idiomas"""
    preferred_languages: List[str] = Field(..., max_items=3)
    
    @validator('preferred_languages')
    def validate_languages(cls, v):
        """Valida idiomas"""
        valid_languages = ["es", "en", "fr", "de", "it", "pt", "zh", "ja", "ko", "ru", "ar"]
        
        if not v or not isinstance(v, list):
            raise ValueError("Debe seleccionar al menos un idioma")
        
        # Limitar a máximo 3
        v = v[:3]
        
        # Filtrar solo idiomas válidos
        valid_langs = [lang for lang in v if lang in valid_languages]
        
        if not valid_langs:
            raise ValueError("Debe seleccionar al menos un idioma válido")
        
        # Eliminar duplicados
        return list(dict.fromkeys(valid_langs))

class WaitlistUserResponse(BaseModel):
    """Respuesta al registrar en waitlist"""
    success: bool
    message: str
    user_id: Optional[int] = None
    waitlist_position: Optional[int] = None
    estimated_access: Optional[str] = None
    error: Optional[str] = None

class WaitlistStats(BaseModel):
    """Estadísticas"""
    total_users: int
    today_signups: int
    top_languages: List[Dict[str, Any]]
    top_reasons: List[Dict[str, Any]]
    updated_at: str

class PublicConfig(BaseModel):
    """Configuración pública para frontend"""
    supported_languages: List[Dict[str, str]]
    interest_reasons: List[Dict[str, str]]
    rewrite_tones: List[Dict[str, str]]
    max_languages: int
    version: str