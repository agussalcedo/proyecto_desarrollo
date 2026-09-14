"""
Genera un archivo JSON con datos de usuarios falsos, para que k6
los use como base de las pruebas de carga (simulando usuarios distintos
en vez de mandar siempre la misma data).
"""
import json
import random

CANTIDAD_USUARIOS = 1000


def generar_usuario(indice: int) -> dict:
    return {
        "id": indice,
        "nombre": f"Usuario{indice}",
        "email": f"usuario{indice}@ejemplo.com",
        "ip_simulada": f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}",
    }


usuarios = [generar_usuario(i) for i in range(1, CANTIDAD_USUARIOS + 1)]

with open("k6-tests/megafile_usuarios.json", "w", encoding="utf-8") as archivo:
    json.dump(usuarios, archivo, indent=2, ensure_ascii=False)

print(f"Se generaron {CANTIDAD_USUARIOS} usuarios en k6-tests/megafile_usuarios.json")