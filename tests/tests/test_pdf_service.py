import hashlib

def test_calcular_checksum_de_archivo_valido():
    # 1. Arrange: Simulamos un PDF con algunos bytes (la palabra "hola")
    pdf_simulado = b"hola"
    
    # Calculamos el hash real de "hola" para saber qué deberíamos esperar
    hash_esperado = hashlib.sha256(pdf_simulado).hexdigest()
    
    # 2. Act: Llamamos a una nueva función (que AÚN NO EXISTE) para calcular el checksum
    from app.services.pdf_processor import calculate_checksum
    resultado = calculate_checksum(pdf_simulado)
    
    # 3. Assert: Verificamos que nuestra función devuelva el hash correcto
    assert resultado == hash_esperado