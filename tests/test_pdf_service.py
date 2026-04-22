import pytest
from app.services.pdf_processor import extract_text, calculate_checksum

def test_extraer_texto_de_pdf_vacio_lanza_error():
    """Prueba que un archivo sin bytes lance error """
    # 1. Arrange
    pdf_vacio = b"" 
    
    # 2 & 3. Act & Assert
    with pytest.raises(ValueError, match="El archivo está vacío o es inválido"):
        extract_text(pdf_vacio)

def test_archivo_no_pdf_lanza_error():
    """Prueba que un archivo que no empieza con %PDF sea rechazado """
    # Arrange: Un archivo de texto común
    fake_pdf = b"Esto no es un PDF, es un texto"
    
    # Act & Assert
    with pytest.raises(ValueError, match="El contenido del archivo no tiene un formato PDF válido"):
        extract_text(fake_pdf)

def test_calculate_checksum_es_consistente():
    """Prueba que el checksum sea siempre el mismo para el mismo archivo"""
    # Arrange
    contenido = b"%PDF-1.4 prueba de contenido"
    
    # Act
    hash1 = calculate_checksum(contenido)
    hash2 = calculate_checksum(contenido)
    
    # Assert
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 siempre tiene 64 caracteres

def test_calculate_checksum_diferente_para_archivos_distintos():
    """Prueba que dos archivos distintos generen huellas distintas"""
    archivo1 = b"%PDF-1.4 contenido A"
    archivo2 = b"%PDF-1.4 contenido B"
    
    assert calculate_checksum(archivo1) != calculate_checksum(archivo2)