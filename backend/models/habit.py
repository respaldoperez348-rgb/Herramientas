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
    descripcion: str
    frecuencia: str
    hora_recordatorio: Optional[str] = None
    completado: bool = False
    fecha_creacion: str = ""

    def __post_init__(self):
        if not self.fecha_creacion:
            self.fecha_creacion = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

    def marcar_completado(self):
        self.completado = True

    def marcar_pendiente(self):
        self.completado = False

    def to_dict(self):
        return asdict(self)
