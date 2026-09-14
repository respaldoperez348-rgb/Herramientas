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

    def crear_habito(
        self,
        nombre: str,
        descripcion: str = "",
        frecuencia: str = "diaria",
        hora_recordatorio: Optional[str] = None
    ) -> Habit:

        if not nombre or not nombre.strip():
            raise ValueError("El nombre del hábito es obligatorio.")

        habit = Habit(
            id=self.siguiente_id,
            nombre=nombre.strip(),
            descripcion=descripcion.strip(),
            frecuencia=frecuencia,
            hora_recordatorio=hora_recordatorio
        )

        self.habitos.append(habit)
        self.siguiente_id += 1
        return habit

    def obtener_habitos(self) -> List[Habit]:
        return self.habitos

    def obtener_habito(self, habit_id: int) -> Optional[Habit]:
        for habit in self.habitos:
            if habit.id == habit_id:
                return habit
        return None

    def actualizar_habito(self, habit_id: int, datos: dict) -> Optional[Habit]:
        habit = self.obtener_habito(habit_id)

        if habit is None:
            return None

        if "nombre" in datos:
            nombre = datos["nombre"]
            if not nombre or not nombre.strip():
                raise ValueError("El nombre del hábito no puede estar vacío.")
            habit.nombre = nombre.strip()

        if "descripcion" in datos:
            habit.descripcion = datos["descripcion"].strip()

        if "frecuencia" in datos:
            habit.frecuencia = datos["frecuencia"]

        if "hora_recordatorio" in datos:
            habit.hora_recordatorio = datos["hora_recordatorio"]

        if "completado" in datos:
            habit.completado = bool(datos["completado"])

        return habit

    def eliminar_habito(self, habit_id: int) -> bool:
        habit = self.obtener_habito(habit_id)

        if habit is None:
            return False

        self.habitos.remove(habit)
        return True

    def completar_habito(self, habit_id: int) -> Optional[Habit]:
        habit = self.obtener_habito(habit_id)

        if habit is None:
            return None

        habit.marcar_completado()
        return habit

    def marcar_pendiente(self, habit_id: int) -> Optional[Habit]:
        habit = self.obtener_habito(habit_id)

        if habit is None:
            return None

        habit.marcar_pendiente()
        return habit
