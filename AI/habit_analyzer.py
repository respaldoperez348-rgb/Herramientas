def obtener_valor(habito, campo, predeterminado=None):
    """Permite leer un hábito como objeto o diccionario."""
    if isinstance(habito, dict):
        return habito.get(campo, predeterminado)

    return getattr(habito, campo, predeterminado)


def analizar_habitos(habitos):
    """Genera indicadores básicos del estado de los hábitos."""

    total = len(habitos)

    completados = sum(
        1 for h in habitos
        if obtener_valor(h, "completado", False)
    )

    pendientes = total - completados

    porcentajes = [
        obtener_valor(h, "porcentaje_cumplimiento", 0)
        for h in habitos
    ]

    # En los objetos Habit, el porcentaje es un método.
    porcentajes = [
        valor() if callable(valor) else valor
        for valor in porcentajes
    ]

    porcentaje_promedio = (
        round(sum(porcentajes) / total, 2)
        if total else 0
    )

    return {
        "total_habitos": total,
        "completados": completados,
        "pendientes": pendientes,
        "porcentaje_promedio": porcentaje_promedio
    }