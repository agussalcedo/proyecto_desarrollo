"""
Cliente HTTP - Infrastructure Layer
Encapsula la comunicación con otros microservicios del sistema.
"""
import httpx
from typing import Any, Optional


class MicroserviceClient:
    """
    Cliente genérico para invocar endpoints de otros microservicios.
    Cumple el mismo rol que un Repository, pero contra una API externa
    en vez de contra una base de datos.
    """

    def __init__(self, base_url: str, timeout: float = 5.0):
        self._base_url = base_url
        self._timeout = timeout

    async def get(self, path: str, params: Optional[dict] = None) -> Any:
        async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
            response = await client.get(path, params=params)
            response.raise_for_status()
            return response.json()

    async def post(self, path: str, json: Optional[dict] = None) -> Any:
        async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
            response = await client.post(path, json=json)
            response.raise_for_status()
            return response.json()