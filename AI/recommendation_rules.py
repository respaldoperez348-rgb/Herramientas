def generar_recomendaciones(estadisticas, habitos):
    recomendaciones = []

    if estadisticas["total_habitos"] == 0:
        return [
            "Registra tu primer hábito y establece "
            "una meta que puedas mantener."
        ]

    pendientes = [
        h for h in habitos
        if not (
            h.get("completado", False)
            if isinstance(h, dict)
            else getattr(h, "completado", False)
        )
    ]

    if pendientes:
        habito = pendientes[0]

        nombre = (
            habito.get("nombre", "tu hábito")
            if isinstance(habito, dict)
            else habito.nombre
        )

        recomendaciones.append(
            f"Recuerda dedicar tiempo a '{nombre}'. "
            "Puedes comenzar con una tarea pequeña."
        )

    porcentaje = estadisticas["porcentaje_promedio"]

    if porcentaje >= 80:
        recomendaciones.append(
            "¡Vas por buen camino! Mantén la constancia "
            "y continúa con tus objetivos."
        )
    elif porcentaje < 50:
        recomendaciones.append(
            "Intenta reducir temporalmente la dificultad "
            "de tus objetivos y organizar un horario realista."
        )

    return recomendaciones