from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, date, timedelta
from app.db import db_manager
from app.schemas.auth import WaitlistUserCreate
from app.core.security import security
import logging
import hashlib
import uuid

logger = logging.getLogger(__name__)

class AuthService:
    """Servicio robusto para waitlist"""
    
    def __init__(self):
        self.supabase = db_manager.get_table("waitlist_users")
    
    async def join_waitlist(self, user_data: WaitlistUserCreate) -> Dict[str, Any]:
        """
        Registra usuario con validaciones robustas
        """
        try:
            # 1. Validar email
            if not security.validate_email(user_data.email):
                return {
                    "success": False,
                    "message": "Formato de email inválido",
                    "error": "invalid_email"
                }
            
            # 2. Verificar si existe
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user:
                position = await self.calculate_waitlist_position(existing_user["id"])
                return {
                    "success": False,
                    "message": "Este email ya está registrado",
                    "waitlist_position": position,
                    "error": "email_exists"
                }
            
            # 3. Sanitizar datos
            sanitized_data = {
                "email": user_data.email.lower().strip(),
                "name": security.sanitize_input(user_data.name, 100),
                "interest_reason": user_data.interest_reason,
                "preferred_languages": user_data.preferred_languages,
                "created_at": datetime.utcnow().isoformat(),
                "verification_token": self._generate_verification_token(user_data.email),
                "is_verified": False  # Para futuro
            }
            
            # 4. Insertar en BD
            response = self.supabase.insert(sanitized_data).execute()
            
            if not response.data:
                raise Exception("Error al insertar en base de datos")
            
            user_id = response.data[0]["id"]
            
            # 5. Calcular posición
            position = await self.calculate_waitlist_position(user_id)
            
            # 6. Registrar en analytics (para futuro)
            await self._log_signup_analytics(user_id, user_data.interest_reason)
            
            return {
                "success": True,
                "message": "¡Te has unido a la waitlist exitosamente! Te contactaremos pronto.",
                "user_id": user_id,
                "waitlist_position": position,
                "estimated_access": self._calculate_estimated_access(position),
                "verification_sent": False  # Para cuando implementemos email
            }
            
        except Exception as e:
            logger.error(f"Error en waitlist: {email} - {str(e)}", exc_info=True)
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Busca usuario por email"""
        try:
            response = self.supabase.select("*")\
                .eq("email", email.lower())\
                .execute()
            
            return response.data[0] if response.data else None
        except Exception as e:
            logger.error(f"Error buscando usuario: {e}")
            return None
    
    async def calculate_waitlist_position(self, user_id: int) -> int:
        """Calcula posición real en waitlist"""
        try:
            # Contar usuarios registrados ANTES de este
            response = self.supabase.select("id", count="exact")\
                .lt("id", user_id)\
                .execute()
            
            return (response.count or 0) + 1
        except:
            return 0
    
    def _calculate_estimated_access(self, position: int) -> str:
        """Calcula fecha estimada"""
        # Estimación más realista
        if position <= 100:
            return "Inmediato"
        elif position <= 500:
            days = (position - 100) // 10  # 10 usuarios por día
            access_date = date.today() + timedelta(days=max(1, days))
            return access_date.strftime("%d/%m/%Y")
        else:
            weeks = (position - 500) // 100  # 100 usuarios por semana
            access_date = date.today() + timedelta(weeks=max(1, weeks))
            return access_date.strftime("%d/%m/%Y")
    
    async def get_waitlist_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas completas"""
        try:
            # Total usuarios
            total_resp = self.supabase.select("id", count="exact").execute()
            total_users = total_resp.count or 0
            
            # Hoy
            today = date.today().isoformat()
            today_resp = self.supabase.select("id", count="exact")\
                .gte("created_at", f"{today}T00:00:00")\
                .lte("created_at", f"{today}T23:59:59")\
                .execute()
            today_signups = today_resp.count or 0
            
            # Idiomas más populares
            langs_resp = self.supabase.select("preferred_languages").execute()
            lang_count = {}
            for user in langs_resp.data:
                for lang in user.get("preferred_languages", []):
                    lang_count[lang] = lang_count.get(lang, 0) + 1
            
            top_langs = [
                {"language": lang, "count": count}
                for lang, count in sorted(lang_count.items(), key=lambda x: x[1], reverse=True)[:5]
            ]
            
            # Razones más populares
            reasons_resp = self.supabase.select("interest_reason").execute()
            reason_count = {}
            for user in reasons_resp.data:
                reason = user.get("interest_reason")
                reason_count[reason] = reason_count.get(reason, 0) + 1
            
            top_reasons = [
                {"reason": reason, "count": count}
                for reason, count in sorted(reason_count.items(), key=lambda x: x[1], reverse=True)[:5]
            ]
            
            return {
                "total_users": total_users,
                "today_signups": today_signups,
                "top_languages": top_langs,
                "top_reasons": top_reasons,
                "updated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo stats: {e}")
            return {
                "total_users": 0,
                "today_signups": 0,
                "top_languages": [],
                "top_reasons": [],
                "updated_at": datetime.utcnow().isoformat()
            }
    
    def _generate_verification_token(self, email: str) -> str:
        """Genera token único para verificación"""
        salt = str(uuid.uuid4())
        hash_input = f"{email}{salt}{datetime.utcnow().timestamp()}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:32]
    
    async def _log_signup_analytics(self, user_id: int, interest_reason: str):
        """Log para analytics (puedes expandir esto)"""
        logger.info(f"📝 Nuevo signup: ID={user_id}, Reason={interest_reason}")

# Instancia singleton
auth_service = AuthService()