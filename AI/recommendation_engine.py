class RecommendationEngine:
    """
    Motor encargado de generar
    recomendaciones personalizadas.
    """

    def generar_recomendacion(self, habitos):

        if not habitos:
            return (
                "Aún no tienes hábitos registrados. "
                "Comienza agregando uno."
            )

        pendientes = [
            habit for habit in habitos
            if not habit.completado
        ]

        if pendientes:
            habit = pendientes[0]

            return (
                f"Recuerda completar tu hábito: "
                f"{habit.nombre}."
            )

        return (
            "¡Excelente! Has completado "
            "todos tus hábitos registrados."
        )