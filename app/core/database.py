"""
Database Configuration - Infrastructure Layer
"""
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

# Inicialización del cliente asíncrono utilizando la URL de conexión del entorno
client = AsyncIOMotorClient(settings.MONGO_URL)

# Instancia de la base de datos especificada en la configuración
database = client[settings.MONGO_DB_NAME]

async def check_db_connection():
    """
    Verifica la integridad de la conexión con el servidor MongoDB.
    Realiza una operación de 'ping' para validar la autenticación y disponibilidad.
    """
    try:
        # Ejecución de comando de administración para validar estado
        await client.admin.command('ping')
        print("Status: MongoDB connection established successfully.")
        print(f"Database: {settings.MONGO_DB_NAME}")
    except Exception as e:
        print(f"Status: MongoDB connection failed.")
        print(f"Error Detail: {e}")
        # Se recomienda capturar la excepción en el flujo principal para manejo de errores