# app/core/config.py
import os
from pydantic_settings import BaseSettings
from typing import List, Optional
from enum import Enum
import json

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

class Settings(BaseSettings):
    # Environment
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = True
    
    # Server Configuration - ADD THESE
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", 8080))  # Railway provides PORT
    
    # API Keys
    gemini_api_key: str
    
    # Supabase
    supabase_url: str
    supabase_service_key: str
    
    # Application
    app_name: str = "Cliro Notes MLP"
    app_version: str = "1.0.0"
    
    # Security - Como string, luego lo convertimos
    cors_origins: str = "*"
    
    # Rate Limiting
    rate_limit_per_minute: int = 30
    ai_rate_limit_per_hour: int = 100
    
    # Waitlist configuration
    max_languages_per_user: int = 3
    
    # Email verification
    email_verification_required: bool = False
    
    # Database configuration
    database_pool_size: int = 20
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Devuelve CORS origins como lista"""
        # Si está vacío o es "*", retornar todos
        if not self.cors_origins or self.cors_origins == "*":
            return ["*"]
        
        # Intentar parsear como JSON primero
        try:
            origins = json.loads(self.cors_origins)
            if isinstance(origins, list):
                return origins
        except json.JSONDecodeError:
            pass
        
        # Si no es JSON, separar por comas
        return [origin.strip() for origin in self.cors_origins.split(",")]

settings = Settings()