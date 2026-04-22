"""
Aplicación FastAPI punto de entrada
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import settings
from app.core.database import check_db_connection
from app.routes.document_routes import router as document_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Gestiona el ciclo de vida de la aplicacion.
    Verifica la conexion con la base de datos al iniciar.
    """
    # Lógica de inicio (Startup)
    db_status = await check_db_connection()
    if not db_status:
        print("LOG: No se pudo conectar a la base de datos no relacional.")
    else:
        print("LOG: Conexion exitosa con la base de datos.")
    
    yield  # La aplicacion funciona aqui
    
    # Lógica de cierre (Shutdown)
    print("LOG: Cerrando recursos de la aplicacion.")

# --- PERSONALIZACIÓN DE SWAGGER ---
app = FastAPI(
    title="Proyecto Desarrollo de Software",
    description="API Profesional para la extracción y persistencia de documentos PDF. ",
    version=settings.APP_VERSION,
    contact={
        "name": "Panas sistemas",
        "url": "https://github.com/agussalcedo/proyecto_desarrollo",
    },
    lifespan=lifespan
)

# Registro de las rutas de documentos
app.include_router(document_router)

@app.get("/", tags=["Estado del Sistema"])
def root():
    """Endpoint de informacion general del proyecto"""
    return {
        "project": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "online"
    }

@app.get("/health", tags=["Estado del Sistema"])
def health_check():
    """Verificacion basica de estado del servicio"""
    return {"status": "healthy"}