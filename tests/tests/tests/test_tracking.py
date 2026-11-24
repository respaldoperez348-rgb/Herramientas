from tracking_service import calcular_tasa_cumplimiento, detectar_riesgo_abandono


def test_tasa_cumplimiento_5_de_7_dias():
    registros = [True, True, False, True, True, False, True]  # 5 de 7
    tasa = calcular_tasa_cumplimiento(registros)
    assert round(tasa, 2) == 71.43


def test_riesgo_abandono_si_cumplimiento_menor_50():
    registros = [True, False, False, False, True, False, False]  # 2 de 7
    assert detectar_riesgo_abandono(registros) is True


def test_tasa_cumplimiento_total_es_100():
    assert calcular_tasa_cumplimiento([True] * 7) == 100


def test_tasa_cumplimiento_nulo_es_0():
    assert calcular_tasa_cumplimiento([False] * 7) == 0


def test_no_hay_riesgo_si_cumplimiento_es_alto():
    registros = [True, True, False, True, True, False, True]  # 71.43%
    assert detectar_riesgo_abandono(registros) is False
