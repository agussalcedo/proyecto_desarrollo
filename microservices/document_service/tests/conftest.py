"""
Fixtures compartidas para toda la suite de tests.
"""
import os

# La app lee su configuración al importarse. Estos valores por defecto hacen
# que la suite corra aunque no exista un archivo .env (por ejemplo en la compu
# de otro integrante del equipo o en CI). Si ya están definidos, no se pisan.
os.environ.setdefault("MONGO_URL", "mongodb://localhost:27017")
os.environ.setdefault("MONGO_DB_NAME", "proyecto_desarrollo_test")

import pytest
import fitz  # PyMuPDF


@pytest.fixture
def valid_pdf_bytes() -> bytes:
    """
    Genera un PDF real y válido en memoria (una página con texto),
    para probar la extracción de texto contra un archivo genuino
    en vez de simular bytes arbitrarios.
    """
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((72, 72), "Contenido de prueba para el parcial")
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes


@pytest.fixture
def invalid_pdf_bytes() -> bytes:
    """Bytes que no representan un PDF válido."""
    return b"Esto no es un PDF, es texto plano"
