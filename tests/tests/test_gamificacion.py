from gamificacion import calcular_nivel, obtener_insignias  # AJUSTA el import


def test_usuario_con_0_xp_es_nivel_1():
    nivel, nombre = calcular_nivel(0)
    assert nivel == 1
    assert nombre == "Novato Constante"


def test_950_xp_es_nivel_4():
    nivel, nombre = calcular_nivel(950)
    assert nivel == 4
    assert nombre == "Titán de la Rutina"


def test_racha_7_dias_desbloquea_racha_de_fuego():
    insignias = obtener_insignias(racha=7)
    assert "Racha de Fuego" in insignias
