from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Cliro MVP Backend"
    debug: bool = True

settings = Settings()
