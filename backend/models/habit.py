from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Habit:
    """
    Modelo que representa un hábito dentro de HabitTracker.
    """

    id: int
    nombre: str
    descripcion: str = ""
    frecuencia: str = "diaria"
    hora_recordatorio: Optional[str] = None
    completado: bool = False
    fecha_creacion: str = ""

    # Cantidad de veces que el hábito debía realizarse
    veces_programadas: int = 0

    # Cantidad de veces que el usuario lo completó
    veces_completadas: int = 0

    def __post_init__(self):

        if not self.fecha_creacion:
            self.fecha_creacion = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

        if self.veces_programadas < 0:
            self.veces_programadas = 0

        if self.veces_completadas < 0:
            self.veces_completadas = 0

    def marcar_completado(self):
        """
        Marca el hábito como completado.
        """

        self.completado = True
        self.veces_completadas += 1

    def marcar_pendiente(self):
        """
        Marca el hábito como pendiente.
        """

        self.completado = False

    def porcentaje_cumplimiento(self):
        """
        Calcula el porcentaje de cumplimiento del hábito.
        """

        if self.veces_programadas == 0:
            return 0

        porcentaje = (
            self.veces_completadas
            / self.veces_programadas
        ) * 100

        return round(porcentaje, 2)

    def to_dict(self):
        """
        Convierte el hábito a un diccionario.
        """

        datos = asdict(self)

        datos["porcentaje_cumplimiento"] = (
            self.porcentaje_cumplimiento()
        )

        return datos
