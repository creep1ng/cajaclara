# Configuración con Pydantic
from pydantic import BaseSettings


class Settings(BaseSettings):
    # ...existing code...
    pass

settings = Settings()
