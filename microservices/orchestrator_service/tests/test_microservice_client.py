"""
Tests del MicroserviceClient: Retry + Circuit Breaker.

El servicio remoto se simula con httpx.MockTransport y la espera entre
reintentos con una función falsa, así que los tests son instantáneos y no
dependen de Docker ni de la red.
"""
import httpx
import pytest

from orchestrator_service.clients.microservice_client import MicroserviceClient
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


class Respuestas:
    """
    Servicio remoto simulado. Cada pedido consume la siguiente respuesta de la
    lista (la última se repite). Un entero es un código HTTP; una excepción se lanza.
    """

    def __init__(self, *items) -> None:
        self._items = list(items)
        self.llamadas = 0

    def __call__(self, request: httpx.Request) -> httpx.Response:
        item = self._items[min(self.llamadas, len(self._items) - 1)]
        self.llamadas += 1
        if isinstance(item, Exception):
            raise item
        return httpx.Response(item, json={"codigo": item})


def _cliente(respuestas: Respuestas, **opciones):
    esperas: list = []

    async def espera_falsa(segundos: float) -> None:
        esperas.append(segundos)

    configuracion = dict(
        base_url="http://servicio",
        max_attempts=3,
        backoff_seconds=0.1,
        jitter=0.0,
        breaker=CircuitBreaker(failure_threshold=100),
        sleep=espera_falsa,
        transport=httpx.MockTransport(respuestas),
    )
    configuracion.update(opciones)
    return MicroserviceClient(**configuracion), esperas


class TestRetry:

    @pytest.mark.asyncio
    async def test_reintenta_un_fallo_pasajero_y_termina_bien(self):
        respuestas = Respuestas(503, 503, 200)
        cliente, esperas = _cliente(respuestas)

        resultado = await cliente.get("/health/ready")

        assert resultado == {"codigo": 200}
        assert respuestas.llamadas == 3
        # Espera exponencial: 0.1s y luego 0.2s.
        assert esperas == [pytest.approx(0.1), pytest.approx(0.2)]

    @pytest.mark.asyncio
    async def test_se_rinde_al_agotar_los_intentos(self):
        respuestas = Respuestas(503)
        cliente, _ = _cliente(respuestas)

        with pytest.raises(httpx.HTTPStatusError):
            await cliente.get("/health/ready")

        assert respuestas.llamadas == 3

    @pytest.mark.asyncio
    async def test_reintenta_errores_de_conexion(self):
        respuestas = Respuestas(httpx.ConnectError("sin conexión"), 200)
        cliente, _ = _cliente(respuestas)

        resultado = await cliente.get("/health/ready")

        assert resultado == {"codigo": 200}
        assert respuestas.llamadas == 2

    @pytest.mark.asyncio
    async def test_no_reintenta_errores_4xx(self):
        respuestas = Respuestas(404)
        cliente, esperas = _cliente(respuestas)

        with pytest.raises(httpx.HTTPStatusError):
            await cliente.get("/documents/123")

        assert respuestas.llamadas == 1
        assert esperas == []

    @pytest.mark.asyncio
    async def test_la_espera_no_supera_el_maximo(self):
        respuestas = Respuestas(503)
        cliente, esperas = _cliente(respuestas, max_attempts=5, max_backoff_seconds=0.25)

        with pytest.raises(httpx.HTTPStatusError):
            await cliente.get("/x")

        assert esperas == [pytest.approx(v) for v in (0.1, 0.2, 0.25, 0.25)]

    @pytest.mark.asyncio
    async def test_post_no_se_reintenta_ante_un_error_5xx(self):
        # El pedido llegó al servidor: reintentarlo podría duplicar la operación.
        respuestas = Respuestas(500)
        cliente, _ = _cliente(respuestas)

        with pytest.raises(httpx.HTTPStatusError):
            await cliente.post("/documents", json={"a": 1})

        assert respuestas.llamadas == 1

    @pytest.mark.asyncio
    async def test_post_si_se_reintenta_si_nunca_llego_al_servidor(self):
        respuestas = Respuestas(httpx.ConnectError("sin conexión"), 200)
        cliente, _ = _cliente(respuestas)

        resultado = await cliente.post("/documents", json={"a": 1})

        assert resultado == {"codigo": 200}
        assert respuestas.llamadas == 2


class TestTimeouts:

    def test_el_timeout_de_conexion_es_mas_corto_que_el_de_lectura(self):
        cliente = MicroserviceClient(base_url="http://servicio", timeout=5.0, connect_timeout=2.0)

        assert cliente.timeout.connect == 2.0
        assert cliente.timeout.read == 5.0

    def test_sin_timeout_de_conexion_usa_el_general(self):
        cliente = MicroserviceClient(base_url="http://servicio", timeout=5.0)

        assert cliente.timeout.connect == 5.0

    @pytest.mark.asyncio
    async def test_get_reintenta_un_timeout_de_lectura(self):
        respuestas = Respuestas(httpx.ReadTimeout("lento"), 200)
        cliente, _ = _cliente(respuestas)

        resultado = await cliente.get("/x")

        assert resultado == {"codigo": 200}
        assert respuestas.llamadas == 2

    @pytest.mark.asyncio
    async def test_post_no_se_reintenta_ante_un_timeout_de_lectura(self):
        # El servidor pudo haber recibido el pedido y procesarlo: no se repite.
        respuestas = Respuestas(httpx.ReadTimeout("lento"))
        cliente, _ = _cliente(respuestas)

        with pytest.raises(httpx.ReadTimeout):
            await cliente.post("/documents", json={"a": 1})

        assert respuestas.llamadas == 1

    @pytest.mark.asyncio
    async def test_los_timeouts_cuentan_como_fallo_para_el_circuit_breaker(self):
        respuestas = Respuestas(httpx.ReadTimeout("lento"))
        breaker = CircuitBreaker(failure_threshold=1, clock=FakeClock())
        cliente, _ = _cliente(respuestas, max_attempts=1, breaker=breaker)

        with pytest.raises(httpx.ReadTimeout):
            await cliente.get("/x")

        assert breaker.state is CircuitState.OPEN


class TestCircuitBreakerEnElCliente:

    @pytest.mark.asyncio
    async def test_se_abre_tras_los_fallos_y_deja_de_llamar_al_servicio(self):
        respuestas = Respuestas(httpx.ConnectError("caído"))
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=30.0, clock=FakeClock())
        cliente, _ = _cliente(respuestas, max_attempts=1, breaker=breaker)

        for _ in range(2):
            with pytest.raises(httpx.ConnectError):
                await cliente.get("/x")

        with pytest.raises(CircuitOpenError):
            await cliente.get("/x")

        assert respuestas.llamadas == 2  # la tercera ni siquiera salió
        assert breaker.state is CircuitState.OPEN

    @pytest.mark.asyncio
    async def test_cuenta_un_fallo_por_llamada_y_no_por_reintento(self):
        respuestas = Respuestas(503)
        breaker = CircuitBreaker(failure_threshold=2, clock=FakeClock())
        cliente, _ = _cliente(respuestas, max_attempts=3, breaker=breaker)

        with pytest.raises(httpx.HTTPStatusError):
            await cliente.get("/x")

        # 3 intentos HTTP, pero para el breaker es un solo fallo.
        assert respuestas.llamadas == 3
        assert breaker.state is CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_los_4xx_no_abren_el_circuito(self):
        respuestas = Respuestas(404)
        breaker = CircuitBreaker(failure_threshold=2, clock=FakeClock())
        cliente, _ = _cliente(respuestas, breaker=breaker)

        for _ in range(5):
            with pytest.raises(httpx.HTTPStatusError):
                await cliente.get("/x")

        assert breaker.state is CircuitState.CLOSED

    @pytest.mark.asyncio
    async def test_se_recupera_cuando_el_servicio_vuelve(self):
        respuestas = Respuestas(httpx.ConnectError("caído"), httpx.ConnectError("caído"), 200)
        reloj = FakeClock()
        breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=30.0, clock=reloj)
        cliente, _ = _cliente(respuestas, max_attempts=1, breaker=breaker)

        for _ in range(2):
            with pytest.raises(httpx.ConnectError):
                await cliente.get("/x")
        assert breaker.state is CircuitState.OPEN

        # Mientras el circuito está abierto no se llama al servicio.
        with pytest.raises(CircuitOpenError):
            await cliente.get("/x")
        assert respuestas.llamadas == 2

        # Pasa el tiempo de recuperación: el intento de prueba sale bien y cierra el circuito.
        reloj.now = 31.0
        resultado = await cliente.get("/x")

        assert resultado == {"codigo": 200}
        assert breaker.state is CircuitState.CLOSED
