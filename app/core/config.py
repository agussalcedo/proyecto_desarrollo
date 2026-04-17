from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Configuración centralizada de la aplicación usando Pydantic v2.
    Lee las variables desde el archivo .env en la raíz.
    """
    
    # Variables obligatorias (deben estar en tu archivo .env)
    MONGO_URL: str
    MONGO_DB_NAME: str

    # Variables opcionales con valores por defecto
    APP_NAME: str = "ILovePDF Clone API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # Configuración de Pydantic
    model_config = SettingsConfigDict(
        env_file=".env",           # Archivo donde buscar las variables
        env_file_encoding='utf-8', 
        extra="ignore"             # Ignora variables extras en el .env que no estén aquí
    )

# Instanciamos los settings para importarlos en otros archivos
settings = Settings()
