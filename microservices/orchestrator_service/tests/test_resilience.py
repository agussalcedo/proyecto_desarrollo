"""
Tests unitarios del Circuit Breaker.

Se usa un reloj falso para avanzar el tiempo sin esperar de verdad.
"""
import pytest

from orchestrator_service.clients.resilience import (
    CircuitBreaker,
    CircuitOpenError,
    CircuitState,
)


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def _breaker(threshold: int = 3, recovery: float = 10.0):
    clock = FakeClock()
    breaker = CircuitBreaker(failure_threshold=threshold, recovery_timeout=recovery, clock=clock)
    return breaker, clock


def _fallar(breaker: CircuitBreaker, veces: int) -> None:
    for _ in range(veces):
        breaker.before_call()
        breaker.record_failure()


class TestCircuitBreaker:

    def test_arranca_cerrado_y_deja_pasar_llamadas(self):
        breaker, _ = _breaker()

        breaker.before_call()

        assert breaker.state is CircuitState.CLOSED

    def test_se_abre_al_llegar_al_umbral_de_fallos(self):
        breaker, _ = _breaker(threshold=3)

        _fallar(breaker, 2)
        assert breaker.state is CircuitState.CLOSED

        _fallar(breaker, 1)
        assert breaker.state is CircuitState.OPEN

    def test_un_exito_reinicia_el_contador_de_fallos(self):
        breaker, _ = _breaker(threshold=3)

        _fallar(breaker, 2)
        breaker.before_call()
        breaker.record_success()
        _fallar(breaker, 2)

        assert breaker.state is CircuitState.CLOSED

    def test_circuito_abierto_rechaza_las_llamadas(self):
        breaker, _ = _breaker(threshold=1)
        _fallar(breaker, 1)

        with pytest.raises(CircuitOpenError):
            breaker.before_call()

    def test_pasado_el_tiempo_deja_un_solo_intento_de_prueba(self):
        breaker, clock = _breaker(threshold=1, recovery=10.0)
        _fallar(breaker, 1)

        clock.now = 9.0
        with pytest.raises(CircuitOpenError):
            breaker.before_call()

        clock.now = 10.0
        breaker.before_call()  # intento de prueba
        assert breaker.state is CircuitState.HALF_OPEN

        with pytest.raises(CircuitOpenError):
            breaker.before_call()  # el segundo no pasa mientras el primero sigue en curso

    def test_intento_de_prueba_exitoso_cierra_el_circuito(self):
        breaker, clock = _breaker(threshold=1, recovery=10.0)
        _fallar(breaker, 1)
        clock.now = 10.0

        breaker.before_call()
        breaker.record_success()

        assert breaker.state is CircuitState.CLOSED
        breaker.before_call()  # vuelve a dejar pasar

    def test_intento_de_prueba_fallido_reabre_el_circuito(self):
        breaker, clock = _breaker(threshold=1, recovery=10.0)
        _fallar(breaker, 1)
        clock.now = 10.0

        breaker.before_call()
        breaker.record_failure()

        assert breaker.state is CircuitState.OPEN
        with pytest.raises(CircuitOpenError):
            breaker.before_call()

        # El tiempo de recuperación se cuenta de nuevo desde la reapertura.
        clock.now = 20.0
        breaker.before_call()
        assert breaker.state is CircuitState.HALF_OPEN

    def test_abort_libera_el_intento_de_prueba(self):
        breaker, clock = _breaker(threshold=1, recovery=10.0)
        _fallar(breaker, 1)
        clock.now = 10.0

        breaker.before_call()
        breaker.abort()

        breaker.before_call()  # puede volver a probar
        assert breaker.state is CircuitState.HALF_OPEN

    def test_un_pedido_que_termina_tarde_no_cierra_un_circuito_abierto(self):
        breaker, _ = _breaker(threshold=1)
        _fallar(breaker, 1)

        breaker.record_success()

        assert breaker.state is CircuitState.OPEN

    def test_rechaza_configuracion_invalida(self):
        with pytest.raises(ValueError):
            CircuitBreaker(failure_threshold=0)
        with pytest.raises(ValueError):
            CircuitBreaker(recovery_timeout=-1)
