import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  vus: 5,
  duration: '15s',
};

export default function () {
  const respuesta = http.get('http://localhost:8000/health');

  check(respuesta, {
    'el servidor respondio 200 OK': (r) => r.status === 200,
  });

  sleep(1);
}