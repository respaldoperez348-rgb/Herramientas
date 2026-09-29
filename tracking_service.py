from datetime import datetime, timedelta

class TrackingService:
    def __init__(self, db_repository):
        """
        Inyectamos el repositorio o manejador de base de datos para consultar 
        los registros de los hábitos sin acoplar el código directamente a la BD.
        """
        self.db = db_repository

    def calcular_tasa_cumplimiento(self, usuario_id, habito_id, dias_analisis=7):
        """
        Analiza qué porcentaje del objetivo se ha cumplido en los últimos N días.
        Útil para detectar 'bajo cumplimiento' antes de que sea un abandono total.
        """
        registros = self.db.obtener_registros_recientes(habito_id, dias_analisis)
        if not registros:
            return 0.0

        dias_cumplidos = sum(1 for reg in registros if reg.completado)
        tasa = (dias_cumplidos / dias_analisis) * 100
        
        return round(tasa, 2)

    def detectar_riesgo_abandono(self, usuario_id, habito_id, umbral_dias_inactivo=3):
        """
        Verifica cuántos días consecutivos han pasado sin que el usuario 
        registre actividad en un hábito específico.
        """
        ultimo_registro = self.db.obtener_ultimo_registro(habito_id)
        
        if not ultimo_registro:
            return True # Si no hay registros, está abandonado por defecto
            
        fecha_actual = datetime.now().date()
        dias_sin_actividad = (fecha_actual - ultimo_registro.fecha).days
        
        return dias_sin_actividad >= umbral_dias_inactivo

    def generar_reporte_estado(self, usuario_id):
        """
        Escanea todos los hábitos de un usuario y devuelve un reporte estructurado
        con los hábitos que necesitan intervención inmediata.
        """
        habitos_usuario = self.db.obtener_habitos_por_usuario(usuario_id)
        habitos_en_riesgo = []

        for habito in habitos_usuario:
            es_riesgo = self.detectar_riesgo_abandono(usuario_id, habito.id)
            tasa = self.calcular_tasa_cumplimiento(usuario_id, habito.id)

            if es_riesgo or tasa < 50.0: # Si está inactivo o cumple menos del 50%
                habitos_en_riesgo.append({
                    "habito_id": habito.id,
                    "nombre": habito.nombre,
                    "estado": "Riesgo de abandono" if es_riesgo else "Bajo cumplimiento",
                    "tasa_actual": tasa
                })

        return habitos_en_riesgo
