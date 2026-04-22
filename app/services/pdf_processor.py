import hashlib
import fitz  # PyMuPDF
import io

def extract_text(pdf_bytes: bytes) -> str:
    """
    Extrae el texto del PDF directamente desde la memoria.
    Cumple con la restricción de no persistir temporalmente.
    """
    # 1. Validación de nulidad
    if not pdf_bytes:
        raise ValueError("El archivo está vacío o es inválido")
    
    # 2. Validación de Formato (Magic Bytes) 
    # Verificamos que el contenido empiece con el estándar de PDF
    if not pdf_bytes.startswith(b'%PDF'):
        raise ValueError("El contenido del archivo no tiene un formato PDF válido")

    text_content = ""
    try:
        # 3. Extracción en memoria usando PyMuPDF
        # Abrimos el stream de bytes sin tocar el disco rígido 
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            for page in doc:
                text_content += page.get_text()
        
        return text_content
    except Exception as e:
        # Si PyMuPDF no puede leerlo, el archivo está corrupto o protegido
        raise ValueError(f"Error técnico al procesar el PDF: {str(e)}")

def calculate_checksum(file_bytes: bytes) -> str:
    """
    Calcula el hash SHA-256 de los bytes de un archivo[cite: 9, 10].
    Sirve para evitar que existan duplicados en la base de datos.
    """
    if not file_bytes:
        raise ValueError("No se puede calcular el checksum de un archivo vacío")
        
    return hashlib.sha256(file_bytes).hexdigest()