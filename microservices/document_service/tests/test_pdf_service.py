"""
Tests unitarios - pdf_processor.py

Prueban la lógica pura de extracción de texto y cálculo de checksum,
sin depender de la base de datos ni de la capa HTTP.
"""
import hashlib
import pytest
from app.services.pdf_processor import extract_text, calculate_checksum


class TestExtractText:

    def test_extraer_texto_de_pdf_vacio_lanza_error(self):
        """Un archivo sin bytes debe rechazarse."""
        with pytest.raises(ValueError, match="El archivo está vacío o es inválido"):
            extract_text(b"")

    def test_archivo_no_pdf_lanza_error(self, invalid_pdf_bytes):
        """Un archivo que no empieza con %PDF debe rechazarse."""
        with pytest.raises(ValueError, match="El contenido del archivo no tiene un formato PDF válido"):
            extract_text(invalid_pdf_bytes)

    def test_extraer_texto_de_pdf_valido_devuelve_el_contenido(self, valid_pdf_bytes):
        """Un PDF real y válido debe devolver el texto que contiene."""
        texto = extract_text(valid_pdf_bytes)
        assert "Contenido de prueba para el parcial" in texto


class TestCalculateChecksum:

    def test_calcular_checksum_de_archivo_valido(self):
        """El checksum debe coincidir con el SHA-256 calculado manualmente."""
        pdf_simulado = b"hola"
        hash_esperado = hashlib.sha256(pdf_simulado).hexdigest()
        resultado = calculate_checksum(pdf_simulado)
        assert resultado == hash_esperado

    def test_calculate_checksum_es_consistente(self):
        """El mismo archivo debe generar siempre el mismo checksum."""
        contenido = b"%PDF-1.4 prueba de contenido"
        assert calculate_checksum(contenido) == calculate_checksum(contenido)

    def test_calculate_checksum_diferente_para_archivos_distintos(self):
        """Archivos distintos deben generar checksums distintos."""
        archivo1 = b"%PDF-1.4 contenido A"
        archivo2 = b"%PDF-1.4 contenido B"
        assert calculate_checksum(archivo1) != calculate_checksum(archivo2)

    def test_calcular_checksum_de_archivo_vacio_lanza_error(self):
        """No se puede calcular checksum de un archivo vacío."""
        with pytest.raises(ValueError, match="No se puede calcular el checksum de un archivo vacío"):
            calculate_checksum(b"")
