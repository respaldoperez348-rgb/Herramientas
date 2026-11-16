
import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from ai.recommendation_engine import RecommendationEngine
from ai.prompts import construir_prompt_asistente


# Ubicación del archivo .env del proyecto
RUTA_ENV = (
    Path(__file__).resolve().parent.parent
    / "proyecto"
    / ".env"
)

load_dotenv(RUTA_ENV)


class AIService:
    """
    Servicio que conecta el asistente de HabitTracker
    con Gemini y ofrece recomendaciones offline.
    """

    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.modelo = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash"
        )

        self.motor_reglas = RecommendationEngine()

    def generar_respuesta_asistente(
        self,
        pregunta_usuario,
        habitos_en_riesgo,
        usuario_info
    ):
        """
        Intenta generar una respuesta con Gemini.
        Si no hay clave o falla la conexión,
        utiliza el motor de recomendaciones offline.
        """

        if not pregunta_usuario or not pregunta_usuario.strip():
            return "Escribe una pregunta para poder ayudarte."

        if self.api_key:
            try:
                cliente = genai.Client(
                    api_key=self.api_key
                )

                prompt = construir_prompt_asistente(
                    pregunta_usuario,
                    habitos_en_riesgo,
                    usuario_info
                )

                respuesta = cliente.models.generate_content(
                    model=self.modelo,
                    contents=prompt
                )

                if respuesta.text:
                    return respuesta.text.strip()

            except Exception as error:
                print(
                    "No se pudo utilizar Gemini:",
                    error
                )

        return self._respuesta_offline(
            habitos_en_riesgo
        )

    def _respuesta_offline(self, habitos):
        """
        Utiliza el motor de reglas cuando Gemini
        no está disponible.
        """

        resultado = self.motor_reglas.generar_recomendacion(
            habitos
        )

        if isinstance(resultado, dict):
            recomendaciones = resultado.get(
                "recomendaciones", []
            )
            return "\n".join(recomendaciones)

        if isinstance(resultado, list):
            return "\n".join(str(r) for r in resultado)

        return str(resultado)
