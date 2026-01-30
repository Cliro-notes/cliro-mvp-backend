import re
import jwt
import secrets
from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# Intentar importar email_validator, con fallback
try:
    from email_validator import validate_email, EmailNotValidError
    HAS_EMAIL_VALIDATOR = True
except ImportError:
    HAS_EMAIL_VALIDATOR = False
    logger.warning("email-validator no instalado. Usando validación básica de email.")
    
    # Función simple de validación como fallback
    def validate_email(email: str, check_deliverability: bool = False) -> bool:
        """Validación básica de email"""
        if not email or "@" not in email:
            return False
        local_part, domain = email.split("@", 1)
        if not local_part or not domain or "." not in domain:
            return False
        return True
    
    class EmailNotValidError(Exception):
        pass

class SecurityService:
    """Servicio de seguridad y validación"""
    
    # Clave secreta para JWT (en producción usar variable de entorno)
    JWT_SECRET_KEY = "cliro_dev_secret_key_change_in_production"  # TODO: Mover a .env
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_HOURS = 24
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Valida formato de email"""
        try:
            if HAS_EMAIL_VALIDATOR:
                validate_email(email, check_deliverability=False)
            else:
                # Validación manual básica
                if not email or "@" not in email:
                    return False
                local_part, domain = email.split("@", 1)
                if not local_part or not domain or "." not in domain:
                    return False
                # Validar caracteres básicos
                email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_regex, email):
                    return False
            return True
        except (EmailNotValidError, ValueError):
            return False
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 5000) -> Optional[str]:
        """Sanitiza y valida input de usuario"""
        if not text or not isinstance(text, str):
            return None
        
        # Trim y limitar longitud
        text = text.strip()
        if len(text) > max_length:
            text = text[:max_length]
        
        # Remover caracteres peligrosos (básico)
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text if text else None
    
    @staticmethod
    def validate_languages(languages: list) -> Tuple[bool, list]:
        """Valida lista de idiomas SIN IMPORTAR constants aquí"""
        # NO importar SUPPORTED_LANGUAGES aquí para evitar circular imports
        BASIC_SUPPORTED_LANGUAGES = ["es", "en", "fr", "de", "it", "pt", "zh", "ja", "ko", "ru", "ar"]
        
        if not languages or not isinstance(languages, list):
            return False, []
        
        # Limitar a máximo permitido
        languages = languages[:3]
        
        # Filtrar solo idiomas válidos
        valid_languages = [
            lang for lang in languages 
            if lang in BASIC_SUPPORTED_LANGUAGES
        ]
        
        # Eliminar duplicados
        valid_languages = list(dict.fromkeys(valid_languages))
        
        return len(valid_languages) > 0, valid_languages
    
    @staticmethod
    def validate_interest_reason(reason_id: str) -> bool:
        """Valida que la razón de interés sea válida SIN IMPORTAR constants"""
        BASIC_INTEREST_REASONS = [
            "productivity", "writing", "learning", "content", 
            "students", "business", "accessibility", "other"
        ]
        return reason_id in BASIC_INTEREST_REASONS
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Crea un JWT token para autenticación"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=SecurityService.JWT_EXPIRATION_HOURS)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, 
            SecurityService.JWT_SECRET_KEY, 
            algorithm=SecurityService.JWT_ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """
        Verifica y decodifica un JWT token.
        Para el MVP, puedes usar esto más adelante.
        """
        try:
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token de autenticación requerido"
                )
            
            # Decodificar el token
            payload = jwt.decode(
                token, 
                SecurityService.JWT_SECRET_KEY, 
                algorithms=[SecurityService.JWT_ALGORITHM]
            )
            
            # Verificar expiración (jwt.decode ya lo hace)
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )
        except Exception as e:
            logger.error(f"Error verificando token: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Error de autenticación"
            )
    
    @staticmethod
    def generate_verification_token() -> str:
        """Genera un token aleatorio para verificación de email"""
        return secrets.token_urlsafe(32)

security = SecurityService()

# Alias para backward compatibility
verify_token = security.verify_token