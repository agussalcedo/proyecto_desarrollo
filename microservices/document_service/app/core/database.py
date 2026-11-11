"""
Database Configuration - Infrastructure Layer
"""
import asyncio

from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

# Tiempo máximo de espera del ping. Sin este límite, Motor tarda hasta 30 s en
# rendirse cuando Mongo está caído, y un health check no puede colgarse así.
DB_PING_TIMEOUT_SECONDS = 2.0

# Inicialización del cliente asíncrono utilizando la URL de conexión del entorno
client = AsyncIOMotorClient(settings.MONGO_URL)

# Instancia de la base de datos especificada en la configuración
database = client[settings.MONGO_DB_NAME]

async def ping_database() -> bool:
    """
    Comprueba en silencio (sin imprimir nada) si MongoDB responde.
    Pensada para los health checks, que se ejecutan muy seguido.
    """
    try:
        await asyncio.wait_for(
            client.admin.command("ping"),
            timeout=DB_PING_TIMEOUT_SECONDS,
        )
        return True
    except Exception:
        return False

async def check_db_connection() -> bool:
    """
    Verifica la integridad de la conexión con el servidor MongoDB.
    Realiza una operación de 'ping' para validar la autenticación y disponibilidad.
    """
    try:
        # Ejecución de comando de administración para validar estado
        await client.admin.command('ping')
        print("Status: MongoDB connection established successfully.")
        print(f"Database: {settings.MONGO_DB_NAME}")
        return True
    except Exception as e:
        print(f"Status: MongoDB connection failed.")
        print(f"Error Detail: {e}")
        return False
