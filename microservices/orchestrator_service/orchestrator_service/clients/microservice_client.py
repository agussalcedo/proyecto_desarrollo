"""
Cliente HTTP - Infrastructure Layer
Encapsula la comunicación con otros microservicios del sistema, con
reintentos (Retry) y corte de circuito (Circuit Breaker).
"""
import asyncio
import logging
import random
from typing import Any, Awaitable, Callable, Optional

import httpx

from orchestrator_service.clients.resilience import CircuitBreaker

logger = logging.getLogger(__name__)


def _is_service_failure(error: Exception) -> bool:
    """El servicio no respondió bien: red caída, timeout o error 5xx."""
    if isinstance(error, httpx.TransportError):
        return True
    return isinstance(error, httpx.HTTPStatusError) and error.response.status_code >= 500


def _is_retryable(error: Exception, idempotent: bool) -> bool:
    """
    Qué errores se reintentan:
      - Pedidos idempotentes (GET): errores de red, timeouts y 5xx.
      - Pedidos que modifican datos (POST): solo si el pedido nunca llegó al
        servidor (no se pudo conectar). Reintentar un POST que sí llegó podría
        duplicar la operación.
      - Los 4xx nunca se reintentan: el pedido está mal y fallaría igual.
    """
    if isinstance(error, httpx.TransportError):
        if idempotent:
            return True
        return isinstance(error, (httpx.ConnectError, httpx.ConnectTimeout))
    if isinstance(error, httpx.HTTPStatusError):
        return idempotent and error.response.status_code >= 500
    return False


def _describe(error: Exception) -> str:
    if isinstance(error, httpx.HTTPStatusError):
        return f"HTTP {error.response.status_code}"
    return error.__class__.__name__


class MicroserviceClient:
    """
    Cliente genérico para invocar endpoints de otros microservicios.
    Cumple el mismo rol que un Repository, pero contra una API externa
    en vez de contra una base de datos.

    Cada llamada pasa por dos protecciones:
      1. Circuit Breaker: si el servicio viene fallando, se rechaza al instante.
      2. Retry: ante un fallo pasajero se reintenta con espera exponencial
         (backoff * 1, 2, 4... hasta `max_backoff_seconds`, más un poco de jitter).
    El breaker cuenta una llamada como fallida solo cuando se agotaron los reintentos.
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 5.0,
        max_attempts: int = 3,
        backoff_seconds: float = 0.2,
        max_backoff_seconds: float = 2.0,
        jitter: float = 0.1,
        breaker: Optional[CircuitBreaker] = None,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
        transport: Optional[httpx.AsyncBaseTransport] = None,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts debe ser al menos 1")

        self._base_url = base_url
        self._timeout = timeout
        self._max_attempts = max_attempts
        self._backoff_seconds = backoff_seconds
        self._max_backoff_seconds = max_backoff_seconds
        self._jitter = jitter
        self._breaker = breaker or CircuitBreaker()
        self._sleep = sleep
        self._transport = transport

    @property
    def breaker(self) -> CircuitBreaker:
        return self._breaker

    async def get(self, path: str, params: Optional[dict] = None) -> Any:
        return await self._request("GET", path, idempotent=True, params=params)

    async def post(self, path: str, json: Optional[dict] = None) -> Any:
        return await self._request("POST", path, idempotent=False, json=json)

    async def _request(self, method: str, path: str, idempotent: bool, **kwargs: Any) -> Any:
        # Lanza CircuitOpenError si el circuito está abierto.
        self._breaker.before_call()

        try:
            data = await self._send_with_retries(method, path, idempotent, kwargs)
        except Exception as error:
            if _is_service_failure(error):
                self._breaker.record_failure()
            elif isinstance(error, httpx.HTTPStatusError):
                # Un 4xx significa que el servicio está vivo y respondió.
                self._breaker.record_success()
            else:
                self._breaker.abort()
            raise
        except BaseException:
            # Cancelación: no se sabe cómo habría terminado.
            self._breaker.abort()
            raise

        self._breaker.record_success()
        return data

    async def _send_with_retries(self, method: str, path: str, idempotent: bool, kwargs: dict) -> Any:
        attempt = 1
        while True:
            try:
                return await self._send_once(method, path, kwargs)
            except Exception as error:
                if attempt >= self._max_attempts or not _is_retryable(error, idempotent):
                    raise
                delay = self._delay_before_retry(attempt)
                logger.warning(
                    "%s %s falló (%s). Reintento %d/%d en %.2fs",
                    method, path, _describe(error), attempt, self._max_attempts - 1, delay,
                )
                await self._sleep(delay)
                attempt += 1

    def _delay_before_retry(self, attempt: int) -> float:
        delay = min(self._backoff_seconds * (2 ** (attempt - 1)), self._max_backoff_seconds)
        return delay + random.uniform(0, delay * self._jitter)

    async def _send_once(self, method: str, path: str, kwargs: dict) -> Any:
        async with httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            transport=self._transport,
        ) as client:
            response = await client.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()
