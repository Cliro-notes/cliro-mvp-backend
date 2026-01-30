from supabase import create_client, Client
from app.core.config import settings
from typing import Optional
import logging
import time

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor seguro de conexiones a Supabase"""
    
    _instance: Optional['DatabaseManager'] = None
    _client: Optional[Client] = None
    _last_connection_test: float = 0
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if self._client is None:
            self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa el cliente de Supabase con la Service Key"""
        try:
            self._client = create_client(
                settings.supabase_url,
                settings.supabase_service_key
            )
            
            # Test de conexión
            self.test_connection()
            logger.info("✅ Conexión a Supabase establecida (Service Key)")
            
        except Exception as e:
            logger.error(f"❌ Error crítico conectando a Supabase: {e}")
            raise
    
    def test_connection(self):
        """Prueba la conexión a Supabase"""
        try:
            # Query simple para test
            result = self._client.table("waitlist_users")\
                .select("count", count="exact")\
                .limit(1)\
                .execute()
            
            self._last_connection_test = time.time()
            logger.debug("✅ Test de conexión a Supabase exitoso")
            return True
            
        except Exception as e:
            logger.error(f"❌ Test de conexión fallido: {e}")
            return False
    
    @property
    def client(self) -> Client:
        """Obtiene el cliente de Supabase"""
        # Re-test cada 5 minutos
        if time.time() - self._last_connection_test > 300:
            if not self.test_connection():
                raise ConnectionError("Conexión a Supabase perdida")
        return self._client
    
    def get_table(self, table_name: str):
        """Obtiene referencia a una tabla con logging"""
        logger.debug(f"Accediendo a tabla: {table_name}")
        return self.client.table(table_name)

# Instancia global
db_manager = DatabaseManager()

# Alias para uso simple
supabase = db_manager.client