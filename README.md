# Integrantes del grupo
Agustin Salcedo, Juan Pablo Cañada, Nicolas Martínez, Carlos Reta, Santiago Miscovich

## Instalación y Ejecución

Pasos para configurar el entorno y ejecutar la aplicación localmente:

### 1. Requisitos Previos
* Python 3.12 o superior.
* Se recomienda el uso de un entorno virtual (`venv`).

### 2. Configuración del Entorno
Clone el repositorio y cree un entorno virtual:
```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_CARPETA>
python -m venv venv
```
Activar el entorno virtual

Windows: venv\Scripts\activate
Linux/Mac: source venv/bin/activate

### 3. Instalar librerias
pip install -r requirements.txt

### 4. Iniciar aplicación
```bash
uvicorn app.main:app --reload
```