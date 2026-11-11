"""
Resiliencia - Infrastructure Layer
Circuit Breaker para proteger las llamadas entre microservicios.

Estados:
  - CLOSED:    funciona normal. Cuenta los fallos seguidos.
  - OPEN:      se llegó al umbral de fallos. Las llamadas se rechazan al
               instante (CircuitOpenError), sin molestar al servicio caído.
  - HALF_OPEN: pasó el tiempo de recuperación. Se deja pasar UN solo intento
               de prueba: si sale bien se cierra, si falla se vuelve a abrir.
"""
import time
from enum import Enum
from typing import Callable


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitOpenError(Exception):
    """El circuito está abierto: la llamada se rechazó sin intentarla."""

    def __init__(self, retry_in_seconds: float = 0.0) -> None:
        super().__init__(f"Circuito abierto, se vuelve a probar en {retry_in_seconds:.1f}s")
        self.retry_in_seconds = retry_in_seconds


class CircuitBreaker:
    """
    Corta el circuito después de `failure_threshold` fallos seguidos y lo
    vuelve a probar pasados `recovery_timeout` segundos.

    `clock` se puede reemplazar en los tests para no tener que esperar.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if failure_threshold < 1:
            raise ValueError("failure_threshold debe ser al menos 1")
        if recovery_timeout < 0:
            raise ValueError("recovery_timeout no puede ser negativo")

        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._clock = clock

        self._state = CircuitState.CLOSED
        self._failures = 0
        self._opened_at = 0.0
        self._probe_in_flight = False

    @property
    def state(self) -> CircuitState:
        return self._state

    def before_call(self) -> None:
        """Se llama antes de cada pedido. Lanza CircuitOpenError si no se puede."""
        if self._state is CircuitState.CLOSED:
            return

        if self._state is CircuitState.OPEN:
            elapsed = self._clock() - self._opened_at
            if elapsed < self._recovery_timeout:
                raise CircuitOpenError(self._recovery_timeout - elapsed)
            # Pasó el tiempo de recuperación: este pedido es el intento de prueba.
            self._state = CircuitState.HALF_OPEN
            self._probe_in_flight = True
            return

        # HALF_OPEN: solo un intento de prueba a la vez.
        if self._probe_in_flight:
            raise CircuitOpenError(0.0)
        self._probe_in_flight = True

    def record_success(self) -> None:
        # Un pedido que empezó antes de abrirse y termina después no cierra el circuito.
        if self._state is CircuitState.OPEN:
            return
        self._state = CircuitState.CLOSED
        self._failures = 0
        self._probe_in_flight = False

    def record_failure(self) -> None:
        if self._state is CircuitState.OPEN:
            return
        if self._state is CircuitState.HALF_OPEN:
            self._open()
            return
        self._failures += 1
        if self._failures >= self._failure_threshold:
            self._open()

    def abort(self) -> None:
        """
        El pedido terminó sin un resultado claro (cancelado, respuesta ilegible).
        No cuenta como éxito ni como fallo; solo libera el intento de prueba.
        """
        self._probe_in_flight = False

    def _open(self) -> None:
        self._state = CircuitState.OPEN
        self._opened_at = self._clock()
        self._failures = 0
        self._probe_in_flight = False
