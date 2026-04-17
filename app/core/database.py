from motor.motor_asyncio import AsyncIOMotorClient
import os

# URL y nombre de la base de datos
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
DB_NAME = os.getenv("MONGO_DB_NAME", "proyecto_desarrollo")

client = AsyncIOMotorClient(MONGO_URL)
database = client.get_database(DB_NAME)

async def check_db_connection():
    try:
        await client.admin.command("ping")
        print(f"¡Conexión exitosa a la base de datos: {DB_NAME}")
    except Exception as e:
        print(f"Error de conexión: {e}")