from database import encriptar_contrasena, verificar_contrasena  # AJUSTA


def test_encriptar_contrasena_genera_hash_bcrypt_valido():
    hash_generado = encriptar_contrasena("MiClave123")
    if isinstance(hash_generado, bytes):
        hash_generado = hash_generado.decode()
    assert hash_generado != "MiClave123"
    assert hash_generado.startswith(("$2a$", "$2b$", "$2y$"))


def test_verificar_contrasena_correcta_e_incorrecta():
    hash_generado = encriptar_contrasena("MiClave123")
    assert verificar_contrasena("MiClave123", hash_generado) is True
    assert verificar_contrasena("ClaveEquivocada", hash_generado) is False
