import pytest

# Nota: Aún no hemos creado el archivo 'pdf_processor.py' en 'app/services/', 
# pero en TDD siempre imaginamos cómo queremos usar el código antes de crearlo.
from app.services.pdf_processor import extract_text

def test_extraer_texto_de_pdf_vacio_lanza_error():
    # 1. Preparación (Arrange): Simulamos un archivo de 0 bytes
    pdf_vacio = b"" 
    
    # 2 & 3. Acción y Verificación (Act & Assert): 
    # Esperamos que nuestro sistema detecte el error y lance una excepción (ValueError)
    with pytest.raises(ValueError, match="El archivo está vacío o es inválido"):
        extract_text(pdf_vacio)