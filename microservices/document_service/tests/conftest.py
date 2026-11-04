"""
Fixtures compartidas para toda la suite de tests.
"""
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
