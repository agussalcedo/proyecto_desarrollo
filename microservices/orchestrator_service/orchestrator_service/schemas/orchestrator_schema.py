"""
Esquemas de datos - Model Layer (MVC)
"""
from pydantic import BaseModel
from typing import List


class ServiceHealthResponse(BaseModel):
    service: str
    status: str


class OrchestratorStatusResponse(BaseModel):
    orchestrator: str
    dependencies: List[ServiceHealthResponse]