# tracking_service.py
from datetime import datetime

class TrackingService:
    def __init__(self, db_repository):
        self.db = db_repository

    def calcular_tasa_cumplimiento(self, usuario_id, habito_id, dias_analisis=7):
        registros = self.db.obtener_registros_recientes(habito_id, dias_analisis)
        if not registros:
            return 0.0

        dias_cumplidos = sum(1 for reg in registros if reg.completado)
        tasa = (dias_cumplidos / dias_analisis) * 100
        
        return round(tasa, 2)

    def detectar_riesgo_abandono(self, usuario_id, habito_id, umbral_dias_inactivo=3):
        ultimo_registro = self.db.obtener_ultimo_registro(habito_id)
        
        if not ultimo_registro:
            return True 
            
        fecha_actual = datetime.now().date()
        dias_sin_actividad = (fecha_actual - ultimo_registro.fecha).days
        
        return dias_sin_actividad >= umbral_dias_inactivo

    def generar_reporte_estado(self, usuario_id):
        habitos_usuario = self.db.obtener_habitos_por_usuario(usuario_id)
        habitos_en_riesgo = []

        for habito in habitos_usuario:
            es_riesgo = self.detectar_riesgo_abandono(usuario_id, habito.id)
            tasa = self.calcular_tasa_cumplimiento(usuario_id, habito.id)

            if es_riesgo or tasa < 50.0:
                habitos_en_riesgo.append({
                    "habito_id": habito.id,
                    "nombre": habito.nombre,
                    "estado": "Riesgo de abandono" if es_riesgo else "Bajo cumplimiento",
                    "tasa_actual": tasa
                })

        return habitos_en_riesgo


# ai_service.py
import random

class AIService:
    def __init__(self, tracking_service):
        self.tracking = tracking_service
        self.mensajes_abandono = [
            "Notamos que has dejado de registrar '{habito}'. ¡Un pequeño paso hoy hace la diferencia!",
            "Retomar '{habito}' puede ser difícil, pero puedes empezar con solo 5 minutos hoy.",
            "No rompas tu progreso por completo. ¿Qué te parece si intentas '{habito}' hoy?"
        ]
        self.mensajes_bajo_cumplimiento = [
            "Tu cumplimiento en '{habito}' está en {tasa}%. Intenta ajustar tu meta si es muy alta.",
            "Mantén la constancia en '{habito}'. Un {tasa}% demuestra esfuerzo, ¡tú puedes subirlo!",
            "Estás a medio camino con '{habito}'. Intenta programar un recordatorio para mejorar ese {tasa}%."
        ]

    def generar_mensaje(self, habito_nombre, estado, tasa):
        if estado == "Riesgo de abandono":
            plantilla = random.choice(self.mensajes_abandono)
        else:
            plantilla = random.choice(self.mensajes_bajo_cumplimiento)
        
        return plantilla.format(habito=habito_nombre, tasa=tasa)

    def obtener_recomendaciones_usuario(self, usuario_id):
        habitos_riesgo = self.tracking.generar_reporte_estado(usuario_id)
        recomendaciones = []

        for item in habitos_riesgo:
            mensaje = self.generar_mensaje(item["nombre"], item["estado"], item["tasa_actual"])
            recomendaciones.append({
                "habito_id": item["habito_id"],
                "recomendacion": mensaje,
                "estado": item["estado"]
            })

        return recomendaciones