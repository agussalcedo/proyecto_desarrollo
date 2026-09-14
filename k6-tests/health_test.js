import http from 'k6/http';
import { check, sleep } from 'k6';
import { SharedArray } from 'k6/data';

// Carga el megafile UNA sola vez (SharedArray evita cargarlo por cada usuario
// virtual, para no gastar memoria de más)
const usuarios = new SharedArray('usuarios', function () {
  return JSON.parse(open('./megafile_usuarios.json'));
});

export const options = {
  vus: 5,
  duration: '15s',
};

export default function () {
  // Cada iteración toma un usuario distinto del megafile, en vez de
  // mandar siempre el mismo pedido
  const usuario = usuarios[Math.floor(Math.random() * usuarios.length)];

  const respuesta = http.get('http://localhost:8000/health', {
    headers: {
      // Simula que el pedido viene de la IP de ese usuario falso
      'X-Forwarded-For': usuario.ip_simulada,
    },
  });

  check(respuesta, {
    'el servidor respondio 200 OK': (r) => r.status === 200,
  });

  sleep(1);
}