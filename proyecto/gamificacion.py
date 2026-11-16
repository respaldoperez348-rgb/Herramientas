"""
Módulo de Gamificación y Sistema de Logros (RPG de Hábitos) para HabitPulse.
Gestiona el cálculo de experiencia (XP), niveles, rangos e insignias desbloqueables.
"""

class SistemaGamificacion:
    # Definición de niveles y rangos RPG
    NIVELES = [
        {"nivel": 1, "rango": "Novato Constante", "xp_min": 0, "xp_max": 250, "icono": "seedling"},
        {"nivel": 2, "rango": "Guardián del Enfoque", "xp_min": 250, "xp_max": 500, "icono": "shield-check"},
        {"nivel": 3, "rango": "Maestro HabitPulse", "xp_min": 500, "xp_max": 850, "icono": "crown"},
        {"nivel": 4, "rango": "Titán de la Rutina", "xp_min": 850, "xp_max": 1300, "icono": "fire-circle"},
        {"nivel": 5, "rango": "Leyenda Atómica", "xp_min": 1300, "xp_max": 2000, "icono": "star-shooting"}
    ]

    @classmethod
    def evaluar_insignias(cls, habitos, minutos_temporizador=0):
        """
        Evalúa el estado de todas las insignias del sistema basadas en los hábitos actuales
        y el tiempo registrado en temporizador.
        """
        habitos = habitos or []

        # Métricas clave
        racha_max = max((h.get('racha_dias', 0) for h in habitos), default=0)
        
        # Verificar madrugador (hábito completado con horario de mañana <= 08:00 AM)
        es_madrugador = False
        for h in habitos:
            horario = str(h.get('horario', '')).upper()
            completado = h.get('completado_hoy', False)
            if completado and ("08:00 AM" in horario or "07:00 AM" in horario or "06:00 AM" in horario or "05:00 AM" in horario):
                es_madrugador = True
                break
            # Fallback: si se llama 'Beber 2L de agua' o 'agua' y está completado
            if completado and "agua" in h.get('nombre', '').lower():
                es_madrugador = True
                break

        # Minutos acumulados totales (de temporizador + minutos registrados en hábitos)
        minutos_habitos = sum((h.get('total_segundos', 0) // 60) for h in habitos)
        minutos_totales = max(minutos_temporizador, minutos_habitos)

        # Cumplimiento diario
        total_habitos = len(habitos)
        completados_hoy = sum(1 for h in habitos if h.get('completado_hoy', False))
        porcentaje_dia = (completados_hoy / total_habitos * 100) if total_habitos > 0 else 0

        insignias = [
            {
                "id": "racha_fuego",
                "titulo": "Racha de Fuego",
                "descripcion": "7 días seguidos cumpliendo un hábito",
                "icono": "fire",
                "color_hex": "#FF7A00",
                "color_rgba": (1, 0.48, 0.05, 1),
                "xp": 150,
                "meta": 7,
                "unidad": "días",
                "progreso_actual": min(7, racha_max),
                "desbloqueado": racha_max >= 7,
                "progreso_texto": f"{min(7, racha_max)}/7 días de racha"
            },
            {
                "id": "madrugador",
                "titulo": "Madrugador",
                "descripcion": "Registrar o cumplir un hábito antes de las 8:00 AM",
                "icono": "weather-sunset-up",
                "color_hex": "#FFB800",
                "color_rgba": (1, 0.72, 0.0, 1),
                "xp": 100,
                "meta": 1,
                "unidad": "hábito",
                "progreso_actual": 1 if es_madrugador else 0,
                "desbloqueado": es_madrugador,
                "progreso_texto": "¡Completado a las 8:00 AM!" if es_madrugador else "Cumple un hábito antes de 8:00 AM"
            },
            {
                "id": "enfoque_absoluto",
                "titulo": "Enfoque Absoluto",
                "descripcion": "Acumular 60 minutos con el temporizador",
                "icono": "timer-sand-complete",
                "color_hex": "#00F7FF",
                "color_rgba": (0, 0.97, 1, 1),
                "xp": 200,
                "meta": 60,
                "unidad": "min",
                "progreso_actual": min(60, minutos_totales),
                "desbloqueado": minutos_totales >= 60,
                "progreso_texto": f"{min(60, minutos_totales)}/60 min enfocados"
            },
            {
                "id": "maestro_disciplina",
                "titulo": "Maestro de Disciplina",
                "descripcion": "Completar el 100% de los hábitos del día",
                "icono": "shield-crown",
                "color_hex": "#E11D48",
                "color_rgba": (0.88, 0.11, 0.28, 1),
                "xp": 120,
                "meta": 100,
                "unidad": "%",
                "progreso_actual": int(porcentaje_dia),
                "desbloqueado": total_habitos > 0 and completados_hoy == total_habitos,
                "progreso_texto": f"{int(porcentaje_dia)}% de hábitos hoy"
            },
            {
                "id": "iniciado_zen",
                "titulo": "Iniciado Zen",
                "descripcion": "Crear y registrar tu primer hábito personalizado",
                "icono": "meditation",
                "color_hex": "#10B981",
                "color_rgba": (0.16, 0.85, 0.55, 1),
                "xp": 50,
                "meta": 1,
                "unidad": "hábito",
                "progreso_actual": 1 if total_habitos >= 1 else 0,
                "desbloqueado": total_habitos >= 1,
                "progreso_texto": f"{total_habitos} hábito(s) activos"
            }
        ]

        return insignias

    @classmethod
    def calcular_estado_rpg(cls, habitos, minutos_temporizador=0):
        """
        Calcula el progreso completo de RPG: XP acumulado, nivel, rango y lista de insignias.
        """
        insignias = cls.evaluar_insignias(habitos, minutos_temporizador)
        
        # XP base inicial para David
        xp_base = 250
        
        # XP por hábitos completados hoy (+40 XP cada uno)
        completados = sum(1 for h in habitos if h.get('completado_hoy', False))
        xp_habitos = completados * 40
        
        # XP por tiempo de enfoque (+1 XP por cada 2 minutos)
        minutos_habitos = sum((h.get('total_segundos', 0) // 60) for h in habitos)
        minutos_totales = max(minutos_temporizador, minutos_habitos)
        xp_tiempo = minutos_totales // 2
        
        # XP por insignias desbloqueadas
        xp_insignias = sum(i['xp'] for i in insignias if i['desbloqueado'])
        
        xp_total = xp_base + xp_habitos + xp_tiempo + xp_insignias

        # Determinar nivel actual
        nivel_info = cls.NIVELES[0]
        for n in cls.NIVELES:
            if xp_total >= n["xp_min"]:
                nivel_info = n

        nivel_num = nivel_info["nivel"]
        rango_nombre = nivel_info["rango"]
        icono_rango = nivel_info["icono"]
        xp_min = nivel_info["xp_min"]
        xp_max = nivel_info["xp_max"]

        # Porcentaje de avance hacia el siguiente nivel
        rango_xp = xp_max - xp_min
        xp_ganado_en_nivel = max(0, xp_total - xp_min)
        porcentaje_nivel = min(100, int((xp_ganado_en_nivel / rango_xp) * 100)) if rango_xp > 0 else 100

        desbloqueadas_count = sum(1 for i in insignias if i['desbloqueado'])
        total_insignias = len(insignias)

        return {
            "xp_total": xp_total,
            "nivel": nivel_num,
            "rango": rango_nombre,
            "icono_rango": icono_rango,
            "xp_min": xp_min,
            "xp_max": xp_max,
            "xp_en_nivel": xp_ganado_en_nivel,
            "porcentaje_nivel": porcentaje_nivel,
            "insignias": insignias,
            "desbloqueadas_count": desbloqueadas_count,
            "total_insignias": total_insignias,
            "texto_resumen": f"Nvl {nivel_num} {rango_nombre} • {xp_total} / {xp_max} XP"
        }
