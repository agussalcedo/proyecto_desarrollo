"""
Esquemas de datos - Model Layer (MVC)
"""
from pydantic import BaseModel
from typing import Dict, List


class ServiceHealthResponse(BaseModel):
    service: str
    status: str


class OrchestratorStatusResponse(BaseModel):
    orchestrator: str
    dependencies: List[ServiceHealthResponse]


class LivenessResponse(BaseModel):
    """El proceso está vivo y responde."""
    status: str
    service: str
    version: str
    uptime_seconds: int


class ReadinessResponse(BaseModel):
    """El servicio está listo para atender pedidos (dependencias incluidas)."""
    status: str
    service: str
    version: str
    checks: Dict[str, str]
