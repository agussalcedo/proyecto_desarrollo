"""
Rutas HTTP - Presentation Layer (Controller MVC)
"""
from fastapi import APIRouter
from orchestrator_service.services.orchestrator_service import OrchestratorService
from orchestrator_service.schemas.orchestrator_schema import (
    OrchestratorStatusResponse,
    ServiceHealthResponse,
)

router = APIRouter(prefix="/orchestrator", tags=["Orquestador"])
_service = OrchestratorService()


@router.get("/status", response_model=OrchestratorStatusResponse)
async def get_status():
    """
    Verifica el estado del orquestador y de los microservicios de los que depende.
    """
    try:
        health = await _service.check_document_service_health()
        dependency = ServiceHealthResponse(
            service="document_service",
            status=health.get("status", "unknown"),
        )
    except Exception:
        dependency = ServiceHealthResponse(service="document_service", status="unreachable")

    return OrchestratorStatusResponse(orchestrator="online", dependencies=[dependency])