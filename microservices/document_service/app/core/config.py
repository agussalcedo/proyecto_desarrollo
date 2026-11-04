from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Configuración centralizada de la aplicación usando Pydantic v2.
    """
    
    # Variables de Base de Datos
    MONGO_URL: str
    MONGO_DB_NAME: str

    # Nombre del proyecto
    APP_NAME: str = "Proyecto Desarrollo de Software"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Validación de tamaño
    MAX_FILE_SIZE: int = 15 * 1024 * 1024 #Esto equivale a 15Mb
    ALLOWED_EXTENSIONS: list = ["pdf"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8', 
        extra="ignore"
    )

settings = Settings()