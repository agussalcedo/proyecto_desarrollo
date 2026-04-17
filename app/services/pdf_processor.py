import hashlib

def extract_text(pdf_bytes: bytes) -> str:
    # Si el archivo viene vacío (0 bytes), lanzamos el error que espera el test
    if not pdf_bytes:
        raise ValueError("El archivo está vacío o es inválido")
    
    # Aquí irá la lógica real de PyPDF2 o pdfplumber más adelante
    return "Texto extraído simulado"

def calculate_checksum(file_bytes: bytes) -> str:
    """
    Calcula el hash SHA-256 de los bytes de un archivo.
    Esta es la 'huella digital' única del documento.
    """
    if not file_bytes:
        raise ValueError("No se puede calcular el checksum de un archivo vacío")
        
    return hashlib.sha256(file_bytes).hexdigest()