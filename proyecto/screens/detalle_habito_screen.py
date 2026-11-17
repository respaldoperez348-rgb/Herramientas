from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
import time

class DetalleHabitoScreen(MDScreen):
    nombre_habito_texto = StringProperty("Lectura técnica")
    descripcion_habito_texto = StringProperty("Leer y profundizar en temas técnicos relevantes.")
    icono_habito = StringProperty("book-open-page-variant")
    enfoque_label = StringProperty("Enfoque en lectura")
    display_tiempo = StringProperty("24:35")
    meta_label = StringProperty("de 30 min")
    temporizador_activo = BooleanProperty(False)
    angulo_progreso = NumericProperty(295)
    racha_actual_texto = StringProperty("5 días")
    meta_hoy_texto = StringProperty("30 min")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.habito_actual = None
        self.tiempo_inicio = None
        self.segundos_acumulados = 24 * 60 + 35  # Tiempo visual inicial por defecto (24m 35s)
        self.evento_temporizador = None
        self.recordatorio_activo = False

    def on_pre_enter(self):
        if self.app and hasattr(self.app, 'habito_seleccionado') and self.app.habito_seleccionado:
            self.habito_actual = self.app.habito_seleccionado
            self.actualizar_pantalla()
        else:
            self.actualizar_pantalla_demo()

    def actualizar_pantalla_demo(self):
        self.nombre_habito_texto = "Lectura técnica"
        self.descripcion_habito_texto = "Leer y profundizar en temas técnicos relevantes."
        self.icono_habito = "book-open-page-variant"
        self.enfoque_label = "Enfoque en lectura"
        self.meta_label = "de 30 min"
        self.racha_actual_texto = "5 días"
        self.meta_hoy_texto = "30 min"
        self.display_tiempo = "24:35"
        self.angulo_progreso = 295

    def actualizar_pantalla(self):
        if not self.habito_actual:
            self.actualizar_pantalla_demo()
            return

        nombre = self.habito_actual.get('nombre', 'Lectura técnica')
        self.nombre_habito_texto = nombre
        self.descripcion_habito_texto = self.habito_actual.get('descripcion', 'Constancia y progreso diario')
        
        # Determinar icono y etiqueta de enfoque
        nom_low = nombre.lower()
        if "lect" in nom_low or "libro" in nom_low:
            self.icono_habito = "book-open-page-variant"
            self.enfoque_label = "Enfoque en lectura"
        elif "agua" in nom_low:
            self.icono_habito = "water"
            self.enfoque_label = "Hidratación consciente"
        elif "entrena" in nom_low or "gym" in nom_low:
            self.icono_habito = "dumbbell"
            self.enfoque_label = "Sesión de entrenamiento"
        elif "python" in nom_low or "código" in nom_low or "prog" in nom_low:
            self.icono_habito = "xml"
            self.enfoque_label = "Sesión de programación"
        else:
            self.icono_habito = "target"
            self.enfoque_label = f"Enfoque en {nombre}"

        objetivo = self.habito_actual.get('objetivo_diario_minutos', 30)
        self.meta_label = f"de {objetivo} min"
        self.meta_hoy_texto = f"{objetivo} min"

        racha = self.habito_actual.get('racha_dias', self.habito_actual.get('racha', 5))
        self.racha_actual_texto = f"{racha} días"

        # Tiempo transcurrido
        tot_seg = self.habito_actual.get('total_segundos', 0)
        if tot_seg > 0:
            self.segundos_acumulados = min(tot_seg, objetivo * 60)
            m = self.segundos_acumulados // 60
            s = self.segundos_acumulados % 60
            self.display_tiempo = f"{m:02d}:{s:02d}"
            porc = min(1.0, self.segundos_acumulados / (objetivo * 60)) if objetivo > 0 else 0.8
            self.angulo_progreso = int(porc * 360)
        else:
            self.display_tiempo = "24:35"
            self.angulo_progreso = 295

    def toggle_temporizador(self):
        if self.temporizador_activo:
            self.pausar_temporizador()
        else:
            self.iniciar_temporizador()

    def iniciar_temporizador(self):
        if not self.temporizador_activo:
            self.temporizador_activo = True
            self.tiempo_inicio = time.time()
            self.evento_temporizador = Clock.schedule_interval(self.actualizar_temporizador, 1.0)

    def pausar_temporizador(self):
        if self.temporizador_activo:
            self.temporizador_activo = False
            if self.evento_temporizador:
                Clock.unschedule(self.evento_temporizador)
                self.evento_temporizador = None

    def detener_temporizador(self):
        self.pausar_temporizador()
        if self.segundos_acumulados > 0:
            self.guardar_sesion(self.segundos_acumulados)
        self.volver_atras()

    def actualizar_temporizador(self, dt):
        if self.temporizador_activo:
            self.segundos_acumulados += 1
            m = self.segundos_acumulados // 60
            s = self.segundos_acumulados % 60
            self.display_tiempo = f"{m:02d}:{s:02d}"

            objetivo = 30
            if self.habito_actual:
                objetivo = self.habito_actual.get('objetivo_diario_minutos', 30)
            frac = min(1.0, self.segundos_acumulados / (objetivo * 60))
            self.angulo_progreso = int(frac * 360)

    def guardar_sesion(self, duracion_segundos):
        minutos = duracion_segundos // 60
        if minutos == 0 and duracion_segundos > 0:
            minutos = 1

        if self.habito_actual:
            self.habito_actual['minutos_hoy'] = self.habito_actual.get('minutos_hoy', 0) + minutos
            self.habito_actual['total_segundos'] = self.habito_actual.get('total_segundos', 0) + duracion_segundos
            self.habito_actual['total_min'] = self.habito_actual.get('total_min', 0) + minutos
            self.habito_actual['total_sesiones'] = self.habito_actual.get('total_sesiones', 0) + 1
            if self.habito_actual['minutos_hoy'] >= self.habito_actual.get('objetivo_diario_minutos', 30):
                self.habito_actual['completado_hoy'] = True

            # Sincronizar con inicio_screen si existe
            if self.app and hasattr(self.app, 'gestor_pantallas'):
                try:
                    inicio = self.app.gestor_pantallas.get_screen('inicio')
                    for h in getattr(inicio, '_habitos_demo', []):
                        if h['id'] == self.habito_actual['id']:
                            h['total_sesiones'] = self.habito_actual['total_sesiones']
                            h['total_segundos'] = self.habito_actual['total_segundos']
                            h['completado_hoy'] = self.habito_actual['completado_hoy']
                            break
                    inicio.cargar_estadisticas()
                    inicio.calcular_progreso_general()
                except Exception:
                    pass

        if self.habito_actual and self.app and getattr(self.app, 'base_datos', None):
            try:
                self.app.base_datos.registrar_sesion(self.habito_actual['id'], duracion_segundos)
            except Exception as e:
                print(f"Aviso guardando sesión en BD: {e}")

    def volver_atras(self):
        if self.app:
            self.app.cambiar_pantalla('inicio', direccion='right')
        else:
            self.manager.current = 'inicio'
            self.manager.transition.direction = 'right'
