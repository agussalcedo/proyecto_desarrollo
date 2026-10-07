import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';

// Carga el megafile UNA sola vez (SharedArray evita cargarlo por cada
// usuario virtual, para no gastar memoria de más)
const usuarios = new SharedArray('usuarios', function () {
  return JSON.parse(open('./megafile_usuarios.json'));
});

export const options = {
  // Rampa de carga real: sube gradualmente en vez de un número fijo de
  // usuarios, para encontrar el punto en el que el sistema empieza a
  // fallar o el rate limiting de Traefik empieza a actuar.
  stages: [
    { duration: '15s', target: 10 },  // calentamiento: 10 usuarios
    { duration: '30s', target: 33 },  // objetivo de carga (33 tx/seg aprox)
    { duration: '30s', target: 50 },  // estres: por encima del objetivo
    { duration: '15s', target: 0 },   // enfriamiento
  ],
  thresholds: {
    // Si el 95% de los pedidos no responde en menos de 1 segundo, o si
    // más del 10% falla, la prueba se marca como no superada.
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate<0.10'],
  },
};

export default function () {
  const usuario = usuarios[Math.floor(Math.random() * usuarios.length)];

  // Sin el puerto :8000: el pedido entra por Traefik (puerto 80), que es
  // quien debe reenviarlo a la API y aplicar el rate limiting.
  const respuesta = http.get('http://localhost/health', {
    headers: {
      'X-Forwarded-For': usuario.ip_simulada,
    },
  });

  check(respuesta, {
    'respondio 200 (paso) o 429 (rate limit activo)': (r) =>
      r.status === 200 || r.status === 429,
  });

  sleep(1);
}
