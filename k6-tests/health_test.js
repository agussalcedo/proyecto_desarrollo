import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';

const usuarios = new SharedArray('usuarios', function () {
  return JSON.parse(open('./megafile_usuarios.json'));
});

// Le decimos a k6 explícitamente que tanto 200 (paso) como 429 (rate
// limit activo) son respuestas ESPERADAS, no fallas del sistema. Sin
// esto, k6 cuenta cualquier 429 como "request fallido" por defecto,
// aunque sea justamente el comportamiento que queremos del gateway.
http.setResponseCallback(http.expectedStatuses(200, 429));

export const options = {
  stages: [
    { duration: '15s', target: 10 },
    { duration: '30s', target: 33 },
    { duration: '30s', target: 50 },
    { duration: '15s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<1000'],
    http_req_failed: ['rate<0.10'],
  },
};

export default function () {
  const usuario = usuarios[Math.floor(Math.random() * usuarios.length)];

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
