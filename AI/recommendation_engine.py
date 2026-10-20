
if __package__:
    from .habit_analyzer import analizar_habitos
    from .recommendation_rules import generar_recomendaciones
else:
    from habit_analyzer import analizar_habitos
    from recommendation_rules import generar_recomendaciones


class RecommendationEngine:
    """
    Motor encargado de coordinar el análisis
    y la generación de recomendaciones.
    """

    def generar_recomendacion(self, habitos):
        """
        Recibe una lista de hábitos y devuelve
        estadísticas y recomendaciones.
        """

        if not habitos:
            return {
                "estadisticas": {
                    "total_habitos": 0,
                    "completados": 0,
                    "pendientes": 0,
                    "porcentaje_promedio": 0
                },
                "recomendaciones": [
                    "Aún no tienes hábitos registrados. "
                    "Comienza agregando uno."
                ]
            }

        estadisticas = analizar_habitos(habitos)

        recomendaciones = generar_recomendaciones(
            estadisticas,
            habitos
        )

        return {
            "estadisticas": estadisticas,
            "recomendaciones": recomendaciones
        }
