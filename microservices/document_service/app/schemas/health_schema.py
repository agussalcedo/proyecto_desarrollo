"""
Esquemas de datos - Health checks
"""
from typing import Dict

from pydantic import BaseModel


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
