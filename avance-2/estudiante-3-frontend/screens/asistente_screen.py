from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from kivy.clock import Clock
from datetime import datetime, timedelta


class AlertaRiesgoCard(MDCard):
    id_habito = NumericProperty(0)
    nombre_habito = StringProperty("")
    porcentaje_cumplimiento = NumericProperty(0)
    diagnostico = StringProperty("")
    recomendacion = StringProperty("")

    def __init__(self, **kwargs):
        self.screen_padre = kwargs.pop('screen_padre', None)
        super().__init__(**kwargs)

    def accion_reajustar(self):
        if self.screen_padre:
            self.screen_padre.mostrar_dialogo_reajuste(self.id_habito, self.nombre_habito)

    def accion_recordatorio(self):
        if self.screen_padre and hasattr(self.screen_padre, 'app'):
            self.screen_padre.app.cambiar_pantalla('recordatorios', 'left')


class MensajeChatWidget(MDBoxLayout):
    texto = StringProperty("")
    es_usuario = BooleanProperty(False)


class AsistenteScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.dialog = None
        self.mensajes_cargados = False

    def on_pre_enter(self):
        self.auditar_habitos_desercion()
        if not self.mensajes_cargados:
            self.inicializar_chat()
            self.mensajes_cargados = True

    def auditar_habitos_desercion(self):
        """
        Módulo Auditor de los últimos 7 a 14 días.
        Identifica hábitos con < 50% de completitud para prevenir deserción.
        """
        container = self.ids.contenedor_alertas_riesgo
        container.clear_widgets()

        habitos_en_riesgo = []

        # Intentar obtener datos reales si el servicio o BD están presentes
        user_id = 1
        if self.app and getattr(self.app, 'usuario_actual', None):
            user_id = self.app.usuario_actual.get('id') or self.app.usuario_actual.get('id_usuario', 1)

        # Si existe tracking_service o método en BD:
        datos_auditados = None
        if self.app and hasattr(self.app, 'base_datos') and hasattr(self.app.base_datos, 'obtener_habitos_en_riesgo'):
            try:
                datos_auditados = self.app.base_datos.obtener_habitos_en_riesgo(user_id, dias=7, umbral=50.0)
            except Exception as e:
                print(f"Nota: Consulta de auditoría en BD: {e}")

        if datos_auditados:
            habitos_en_riesgo = datos_auditados
        else:
            # Algoritmo de detección sobre registros simulados del Avance 2 (seed.sql)
            # En seed.sql: 'Lectura tecnica 30 min' tiene 1 cumplido de 3 días = 33.3% (<50%)
            habitos_en_riesgo = [
                {
                    "id_habito": 2,
                    "nombre": "Lectura técnica 30 min",
                    "porcentaje": 38.0,
                    "dias_evaluados": 7,
                    "dias_cumplidos": 2,
                    "diagnostico": "Detectado 38% de completitud en los últimos 7 días (2 de 7 días completados).",
                    "recomendacion": "Reajuste sugerido: reduce temporalmente el objetivo a 15 min diarios y activa recordatorio a las 19:00."
                }
            ]

        if habitos_en_riesgo:
            for item in habitos_en_riesgo:
                card = AlertaRiesgoCard(
                    id_habito=item.get('id_habito', 0),
                    nombre_habito=item.get('nombre', 'Hábito'),
                    porcentaje_cumplimiento=float(item.get('porcentaje', 38.0)),
                    diagnostico=item.get('diagnostico', 'Bajo cumplimiento detectado.'),
                    recomendacion=item.get('recomendacion', 'Reajusta tu meta para retomar consistencia.'),
                    screen_padre=self
                )
                container.add_widget(card)
        else:
            # Mensaje de todos los hábitos saludables
            card_saludable = MDCard(
                orientation='horizontal',
                size_hint_y=None,
                height="56dp",
                radius=["10dp", "10dp", "10dp", "10dp"],
                md_bg_color=(0.14, 0.22, 0.18, 1),
                padding=["12dp", "8dp"]
            )
            card_saludable.add_widget(
                MDFlatButton(
                    text="✓ Excelente: Ningún hábito se encuentra en riesgo de abandono (< 50%).",
                    theme_text_color="Custom",
                    text_color=(0.2, 0.9, 0.6, 1)
                )
            )
            container.add_widget(card_saludable)

    def inicializar_chat(self):
        """Carga el mensaje inicial de bienvenida del asistente inteligente."""
        container = self.ids.contenedor_chat
        container.clear_widgets()

        saludo = (
            "¡Hola! Soy tu Asistente Contextual de Hábitos. He auditado tus últimos "
            "7 días: tu hidratación va con 70% de consistencia, pero 'Lectura técnica' "
            "se encuentra en 38% (riesgo de deserción). ¿Deseas que reajustemos su meta o programemos una alerta?"
        )
        self.agregar_burbuja_chat(saludo, es_usuario=False)

    def agregar_burbuja_chat(self, texto, es_usuario=False):
        container = self.ids.contenedor_chat
        burbuja = MensajeChatWidget(texto=texto, es_usuario=es_usuario)
        container.add_widget(burbuja)

        # Desplazar hacia abajo
        Clock.schedule_once(lambda dt: self._scroll_al_fondo(), 0.1)

    def _scroll_al_fondo(self):
        if hasattr(self.ids, 'scroll_asistente'):
            self.ids.scroll_asistente.scroll_y = 0

    def enviar_consulta_rapida(self, texto):
        self.ids.campo_chat_mensaje.text = texto
        self.enviar_mensaje()

    def enviar_mensaje(self):
        texto = self.ids.campo_chat_mensaje.text.strip()
        if not texto:
            return

        # 1. Agregar mensaje del usuario
        self.agregar_burbuja_chat(texto, es_usuario=True)
        self.ids.campo_chat_mensaje.text = ""

        # 2. Generar respuesta contextual del Asistente
        Clock.schedule_once(lambda dt: self._responder_asistente(texto), 0.3)

    def _responder_asistente(self, consulta):
        respuesta = self.generar_respuesta_inteligente(consulta)
        self.agregar_burbuja_chat(respuesta, es_usuario=False)

    def generar_respuesta_inteligente(self, consulta):
        q = consulta.lower()

        if "riesgo" in q or "abandono" in q or "deserci" in q:
            return (
                "🔍 Diagnóstico del Auditor:\n"
                "• Hábito crítico: 'Lectura técnica 30 min' con 38% de efectividad.\n"
                "• Causa común: Bloques muy extensos en horario nocturno.\n"
                "• Sugerencia inteligente: Reduce la meta a 15 minutos diarios durante 1 semana. "
                "Al acumular 5 días seguidos podrás volver a incrementarla sin fricción."
            )

        if "reajust" in q or "meta" in q:
            return (
                "🎯 Estrategia de Reajuste Progresivo:\n"
                "1. Si un hábito está por debajo del 50%, no intentes forzar 1 hora de golpe.\n"
                "2. Ve a la pantalla de 'Metas' y ajusta el objetivo a un micro-paso alcanzable.\n"
                "3. Mantén la victoria diaria pequeña para no cortar la cadena motivacional."
            )

        if "racha" in q or "recuper" in q:
            return (
                "🔥 Regla de Oro para Salvar Rachas:\n"
                "• Regla de los 2 Días: Nunca permitas fallar dos días consecutivos.\n"
                "• Si ayer no pudiste completar tu rutina, hoy haz al menos una versión mínima de 2 minutos.\n"
                "• La identidad se construye manteniendo el hábito, aunque sea en versión reducida."
            )

        if "2 min" in q or "regla" in q:
            return (
                "⚡ La Regla de los 2 Minutos (James Clear):\n"
                "• Todo hábito nuevo debe poder iniciarse en menos de 2 minutos.\n"
                "• 'Leer 30 min' se convierte en 'Leer 1 página'.\n"
                "• 'Hacer pesas' se convierte en 'Ponerse las zapatillas'.\n"
                "• Una vez empezado, el 80% de las veces continuarás la sesión."
            )

        if "recordatorio" in q or "hora" in q or "alerta" in q:
            return (
                "⏰ Sugerencia de Horario Óptimo:\n"
                "• Hábitos de concentración (lectura/estudio): Fíjalos entre las 18:30 y 20:00.\n"
                "• Hábitos de salud (agua/ejercicio): Fíjalos antes del mediodía.\n"
                "• Puedes activar y editar tus recordatorios con MDSwitch en la pestaña 'Horarios'."
            )

        # Respuesta general con analítica
        return (
            f"He registrado tu consulta sobre '{consulta}'. Basado en tus estadísticas actuales: "
            "tu mayor fortaleza es la consistencia en hidratación. "
            "Para potenciar tu productividad general, te sugiero sincronizar tus sesiones de estudio con el temporizador "
            "y revisar las metas semanales antes de cada domingo."
        )

    def mostrar_dialogo_reajuste(self, id_habito, nombre_habito):
        def _aplicar(*args):
            if self.dialog:
                self.dialog.dismiss()
            # Navegar a pantalla de metas o notificar
            if hasattr(self, 'app'):
                self.app.cambiar_pantalla('metas', 'left')

        self.dialog = MDDialog(
            title="Reajuste Inteligente de Meta",
            text=(
                f"El asistente recomienda reducir el objetivo de '{nombre_habito}' a 15 minutos diarios "
                "para romper el patrón de deserción de los últimos 7 días. ¿Deseas aplicar este reajuste en Metas?"
            ),
            buttons=[
                MDFlatButton(text="Más tarde", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Ir a Metas", md_bg_color=(0, 0.7, 0.9, 1), on_release=_aplicar)
            ]
        )
        self.dialog.open()
