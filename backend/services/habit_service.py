from typing import Optional, List

from backend.models.habit import Habit


class HabitService:
    """
    Contiene la lógica de negocio relacionada
    con los hábitos.
    """

    def __init__(self):

        self.habitos: List[Habit] = []
        self.siguiente_id = 1

    # ==========================================
    # CREAR HÁBITO
    # ==========================================

    def crear_habito(
        self,
        nombre: str,
        descripcion: str = "",
        frecuencia: str = "diaria",
        hora_recordatorio: Optional[str] = None,
        veces_programadas: int = 0
    ) -> Habit:

        if not nombre or not nombre.strip():

            raise ValueError(
                "El nombre del hábito es obligatorio."
            )

        if frecuencia not in [
            "diaria",
            "semanal",
            "mensual"
        ]:

            raise ValueError(
                "La frecuencia debe ser diaria, "
                "semanal o mensual."
            )

        if veces_programadas < 0:

            raise ValueError(
                "Las veces programadas no pueden ser negativas."
            )

        habit = Habit(
            id=self.siguiente_id,
            nombre=nombre.strip(),
            descripcion=descripcion.strip(),
            frecuencia=frecuencia,
            hora_recordatorio=hora_recordatorio,
            veces_programadas=veces_programadas
        )

        self.habitos.append(habit)

        self.siguiente_id += 1

        return habit

    # ==========================================
    # OBTENER TODOS
    # ==========================================

    def obtener_habitos(self) -> List[Habit]:

        return self.habitos

    # ==========================================
    # OBTENER POR ID
    # ==========================================

    def obtener_habito(
        self,
        habit_id: int
    ) -> Optional[Habit]:

        for habit in self.habitos:

            if habit.id == habit_id:
                return habit

        return None

    # ==========================================
    # ACTUALIZAR
    # ==========================================

    def actualizar_habito(
        self,
        habit_id: int,
        datos: dict
    ) -> Optional[Habit]:

        habit = self.obtener_habito(habit_id)

        if habit is None:
            return None

        if "nombre" in datos:

            nombre = datos["nombre"]

            if not nombre or not nombre.strip():

                raise ValueError(
                    "El nombre del hábito no puede estar vacío."
                )

            habit.nombre = nombre.strip()

        if "descripcion" in datos:

            habit.descripcion = (
                datos["descripcion"].strip()
            )

        if "frecuencia" in datos:

            frecuencia = datos["frecuencia"]

            if frecuencia not in [
                "diaria",
                "semanal",
                "mensual"
            ]:

                raise ValueError(
                    "Frecuencia no válida."
                )

            habit.frecuencia = frecuencia

        if "hora_recordatorio" in datos:

            habit.hora_recordatorio = (
                datos["hora_recordatorio"]
            )

        if "veces_programadas" in datos:

            veces = datos["veces_programadas"]

            if veces < 0:

                raise ValueError(
                    "Las veces programadas "
                    "no pueden ser negativas."
                )

            habit.veces_programadas = veces

        return habit

    # ==========================================
    # ELIMINAR
    # ==========================================

    def eliminar_habito(
        self,
        habit_id: int
    ) -> bool:

        habit = self.obtener_habito(habit_id)

        if habit is None:
            return False

        self.habitos.remove(habit)

        return True

    # ==========================================
    # COMPLETAR
    # ==========================================

    def completar_habito(
        self,
        habit_id: int
    ) -> Optional[Habit]:

        habit = self.obtener_habito(habit_id)

        if habit is None:
            return None

        habit.marcar_completado()

        return habit

    # ==========================================
    # PENDIENTE
    # ==========================================

    def marcar_pendiente(
        self,
        habit_id: int
    ) -> Optional[Habit]:

        habit = self.obtener_habito(habit_id)

        if habit is None:
            return None

        habit.marcar_pendiente()

        return habit

    # ==========================================
    # ESTADÍSTICAS
    # ==========================================

    def obtener_estadisticas(self):

        total = len(self.habitos)

        completados = sum(
            1
            for habit in self.habitos
            if habit.completado
        )

        pendientes = total - completados

        if total > 0:

            porcentaje_general = round(
                (completados / total) * 100,
                2
            )

        else:

            porcentaje_general = 0

        return {
            "total_habitos": total,
            "habitos_completados": completados,
            "habitos_pendientes": pendientes,
            "porcentaje_general": porcentaje_general
        }
