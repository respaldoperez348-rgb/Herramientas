from tracking import calcular_tasa_cumplimiento, detectar_riesgo_abandono  # AJUSTA


def test_tasa_cumplimiento_5_de_7_dias():
    registros = [True, True, False, True, True, False, True]
    tasa = calcular_tasa_cumplimiento(registros)
    assert round(tasa, 2) == 71.43


def test_riesgo_abandono_si_cumplimiento_menor_50():
    registros = [True, False, False, False, True, False, False]
    assert detectar_riesgo_abandono(registros) is True
