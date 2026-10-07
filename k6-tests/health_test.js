import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';
import { Counter } from 'k6/metrics';

const usuarios = new SharedArray('usuarios', function () {
  return JSON.parse(open('./megafile_usuarios.json'));
});

// Contadores personalizados para ver en la consola final
const respuestas200 = new Counter('respuestas_200_ok');
const respuestas429 = new Counter('respuestas_429_ratelimit');

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

  if (respuesta.status === 200) {
    respuestas200.add(1);
  } else if (respuesta.status === 429) {
    respuestas429.add(1);
  }

  check(respuesta, {
    'codigo valido (200 o 429)': (r) => r.status === 200 || r.status === 429,
  });

  sleep(1);
}
