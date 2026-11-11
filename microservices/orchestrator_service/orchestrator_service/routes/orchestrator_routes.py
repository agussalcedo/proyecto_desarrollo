"""
Rutas HTTP - Presentation Layer (Controller MVC)
"""
from fastapi import APIRouter
from orchestrator_service.services.orchestrator_service import get_orchestrator_service
from orchestrator_service.schemas.orchestrator_schema import (
    OrchestratorStatusResponse,
    ServiceHealthResponse,
)

router = APIRouter(prefix="/orchestrator", tags=["Orquestador"])
_service = get_orchestrator_service()


@router.get("/status", response_model=OrchestratorStatusResponse)
async def get_status():
    """
    Verifica el estado del orquestador y de los microservicios de los que depende.
    El estado de cada dependencia es "ready", "not_ready", "unreachable" o "circuit_open".
    """
    document_service_status = await _service.check_document_service_health()
    dependency = ServiceHealthResponse(service="document_service", status=document_service_status)

    return OrchestratorStatusResponse(orchestrator="online", dependencies=[dependency])
