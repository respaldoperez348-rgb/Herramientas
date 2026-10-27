from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDFillRoundFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.screenmanager import SlideTransition
from kivy.properties import StringProperty, NumericProperty, BooleanProperty, ListProperty
from datetime import datetime

try:
    from gamificacion import SistemaGamificacion
except ImportError:
    try:
        from proyecto.gamificacion import SistemaGamificacion
    except ImportError:
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from gamificacion import SistemaGamificacion

class InsigniaCardItem(MDCard):
    titulo = StringProperty("")
    descripcion = StringProperty("")
    icono = StringProperty("medal")
    color_rgba = ListProperty([1, 1, 1, 1])
    progreso_texto = StringProperty("")
    xp_texto = StringProperty("+100 XP")
    desbloqueado = BooleanProperty(False)


class LogrosModalContent(MDBoxLayout):
    pass

class HabitCard(MDCard):
    habit_id = None
    nombre = StringProperty("")
    descripcion = StringProperty("")
    sesiones = NumericProperty(0)
    racha = NumericProperty(0)
    total_min = NumericProperty(0)
    objetivo = NumericProperty(30)
    categoria = StringProperty("Salud")
    horario = StringProperty("07:00 PM")
    completado_hoy = BooleanProperty(False)

    def __init__(self, **kwargs):
        self.habit_id = kwargs.pop('habit_id', None)
        self.app = kwargs.pop('app', None)
        self.inicio_screen = kwargs.pop('inicio_screen', None)

        nombre_val = kwargs.pop('nombre', "")
        desc_val = kwargs.pop('descripcion', "")
        sesiones_val = kwargs.pop('sesiones', 0)
        racha_val = kwargs.pop('racha', 0)
        total_min_val = kwargs.pop('total_min', 0)
        objetivo_val = kwargs.pop('objetivo', 30)
        cat_val = kwargs.pop('categoria', "Salud")
        horario_val = kwargs.pop('horario', "07:00 PM")
        completado_val = kwargs.pop('completado_hoy', False)

        super().__init__(**kwargs)

        self.nombre = nombre_val
        self.descripcion = desc_val
        self.sesiones = sesiones_val
        self.racha = racha_val
        self.total_min = total_min_val
        self.objetivo = objetivo_val
        self.categoria = cat_val
        self.horario = horario_val
        self.completado_hoy = completado_val

    def toggle_check(self):
        self.completado_hoy = not self.completado_hoy
        if self.completado_hoy:
            self.sesiones += 1
            self.racha += 1
            self.total_min += self.objetivo
        else:
            self.sesiones = max(0, self.sesiones - 1)
            self.racha = max(0, self.racha - 1)
            self.total_min = max(0, self.total_min - self.objetivo)

        if self.inicio_screen:
            self.inicio_screen.actualizar_estado_habito(
                self.habit_id, self.completado_hoy, self.sesiones, self.racha, self.total_min
            )

    def ver_detalle(self):
        if self.inicio_screen:
            self.inicio_screen.abrir_detalle_habito(self.habit_id)

    def editar_habito(self):
        if self.inicio_screen:
            self.inicio_screen.editar_habito_dialog(self.habi3t_id)

    def eliminar_habito(self):
        if self.inicio_screen:
            self.inicio_screen.eliminar_habito_dialog(self.habit_id)


class NuevoHabitoForm(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 6
        self.size_hint_y = None
        self.height = 290

        # Nombre personalizado (campo libre)
        self.nombre_field = MDTextField(
            hint_text="Nombre del hábito (ej. Meditar, Gym, Leer)",
            mode="rectangle",
            size_hint_y=None,
            height=46,
            font_size="13sp"
        )
        self.add_widget(self.nombre_field)

        # Categoría
        self.cat_field = MDTextField(
            hint_text="Categoría (Salud, Estudio, Deporte, Enfoque)",
            text="Salud",
            mode="rectangle",
            size_hint_y=None,
            height=46,
            font_size="13sp"
        )
        self.add_widget(self.cat_field)

        # Horario
        self.horario_field = MDTextField(
            hint_text="Horario (ej. 07:00 AM, 08:30 PM)",
            text="07:00 PM",
            mode="rectangle",
            size_hint_y=None,
            height=46,
            font_size="13sp"
        )
        self.add_widget(self.horario_field)

        # Objetivo diario en minutos
        self.obj_field = MDTextField(
            hint_text="Objetivo diario (minutos)",
            text="30",
            mode="rectangle",
            size_hint_y=None,
            height=46,
            font_size="13sp",
            input_filter="int"
        )
        self.add_widget(self.obj_field)


class PerfilForm(MDBoxLayout):
    def __init__(self, usuario_info=None, habitos_list=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 12
        self.padding = 8
        self.size_hint_y = None
        self.height = 320

        info = usuario_info or {}
        nombre = info.get("nombre_usuario") or info.get("nombre", "Manuel David")
        email = info.get("email") or info.get("correo", "david.tineo@email.com")

        estado_rpg = SistemaGamificacion.calcular_estado_rpg(habitos_list or [])

        self.add_widget(MDLabel(
            text=f"Usuario: {nombre}",
            font_style="Subtitle1",
            bold=True,
            size_hint_y=None,
            height=24
        ))

        self.add_widget(MDLabel(
            text=f"Correo: {email}",
            font_style="Caption",
            theme_text_color="Custom",
            text_color=(0.7, 0.75, 0.85, 1),
            size_hint_y=None,
            height=18
        ))

        self.add_widget(MDLabel(
            text=f"Rango: Nivel {estado_rpg['nivel']} - {estado_rpg['rango']} (+{estado_rpg['xp_total']} XP)",
            font_size="11sp",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.88, 0.11, 0.28, 1),
            size_hint_y=None,
            height=20
        ))

        # Apariencia
        self.add_widget(MDLabel(
            text="Preferencias de Interfaz:",
            font_style="Caption",
            bold=True,
            size_hint_y=None,
            height=20
        ))

        self.add_widget(MDLabel(
            text="• Estilo: Glassmorphism Obsidian / Crimson\n• Barra de Navegación: Dock Flotante Activo\n• Versión: HabitPulse v3.0 (Avance Final)",
            font_size="11sp",
            theme_text_color="Custom",
            text_color=(0.6, 0.65, 0.75, 1),
            size_hint_y=None,
            height=54
        ))


class InicioScreen(MDScreen):
    _habitos_demo = [
        {
            "id": 1,
            "nombre": "Beber 2L de agua",
            "descripcion": "Meta diaria de hidratación",
            "total_sesiones": 5,
            "racha_dias": 5,
            "total_segundos": 9000,
            "objetivo_diario_minutos": 30,
            "categoria": "Salud",
            "horario": "08:00 AM",
            "completado_hoy": True
        },
        {
            "id": 2,
            "nombre": "Lectura técnica de código",
            "descripcion": "Libros de arquitectura y patrones",
            "total_sesiones": 3,
            "racha_dias": 3,
            "total_segundos": 5400,
            "objetivo_diario_minutos": 45,
            "categoria": "Estudio",
            "horario": "07:00 PM",
            "completado_hoy": False
        },
        {
            "id": 3,
            "nombre": "Rutina de entrenamiento",
            "descripcion": "Fuerza y movilidad",
            "total_sesiones": 4,
            "racha_dias": 4,
            "total_segundos": 7200,
            "objetivo_diario_minutos": 45,
            "categoria": "Deporte",
            "horario": "06:30 PM",
            "completado_hoy": True
        }
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.current_user_id = None
        self.dialog = None
        self.filtro_busqueda = ""
        self._insignias_desbloqueadas_previas = set()
        self._notificacion_mostrada = set()

    def on_pre_enter(self):
        if not self.app or not getattr(self.app, 'usuario_actual', None):
            if self.app:
                self.app.usuario_actual = {
                    "id": 1,
                    "id_usuario": 1,
                    "nombre_usuario": "David",
                    "email": "david.tineo@email.com"
                }

        if self.app and self.app.usuario_actual:
            self.current_user_id = self.app.usuario_actual.get("id") or self.app.usuario_actual.get("id_usuario", 1)
            username = self.app.usuario_actual.get("nombre_usuario") or self.app.usuario_actual.get("nombre", "David")

            if hasattr(self.ids, 'bienvenido'):
                self.ids.bienvenido.text = f"¡Hola, {username}!"

            self.cargar_estadisticas()
            self.calcular_progreso_general()
            self.load_habits()

    def cargar_estadisticas(self):
        total_sesiones = sum(h.get('total_sesiones', 0) for h in self._habitos_demo)
        racha_max = max((h.get('racha_dias', 0) for h in self._habitos_demo), default=4)
        minutos_totales = sum((h.get('total_segundos', 0) // 60) for h in self._habitos_demo)
        minutos_hoy = sum(h.get('objetivo_diario_minutos', 30) for h in self._habitos_demo if h.get('completado_hoy'))

        if hasattr(self.ids, 'sesiones'):
            self.ids.sesiones.text = str(total_sesiones)
        if hasattr(self.ids, 'tiempo'):
            self.ids.tiempo.text = str(minutos_totales or 120)
        if hasattr(self.ids, 'racha'):
            self.ids.racha.text = f"{racha_max}d"
        if hasattr(self.ids, 'racha_header'):
            self.ids.racha_header.text = f"{racha_max} días"
        if hasattr(self.ids, 'hoy'):
            self.ids.hoy.text = f"{minutos_hoy}m"

    def calcular_progreso_general(self):
        total = len(self._habitos_demo)
        if total == 0:
            porcentaje = 0
        else:
            completados = sum(1 for h in self._habitos_demo if h.get('completado_hoy'))
            porcentaje = int((completados / total) * 100)

        if hasattr(self.ids, 'barra_progreso_general'):
            self.ids.barra_progreso_general.value = porcentaje
        if hasattr(self.ids, 'progreso_general_porcentaje'):
            self.ids.progreso_general_porcentaje.text = f"{porcentaje}%"

        # Integrar cálculo dinámico de Gamificación y RPG de Hábitos
        minutos_totales = sum((h.get('total_segundos', 0) // 60) for h in self._habitos_demo)
        estado_rpg = SistemaGamificacion.calcular_estado_rpg(self._habitos_demo, minutos_temporizador=minutos_totales)

        if hasattr(self.ids, 'nivel_xp_text'):
            self.ids.nivel_xp_text.text = estado_rpg['texto_resumen']
        if hasattr(self.ids, 'texto_insignias_banner'):
            self.ids.texto_insignias_banner.text = f"Logros RPG: {estado_rpg['desbloqueadas_count']}/{estado_rpg['total_insignias']} Desbloqueadas (+{estado_rpg['xp_total']} XP)"

        # Revisar si se acaba de desbloquear una insignia durante la interacción
        desbloqueadas_ahora = {i['id'] for i in estado_rpg['insignias'] if i['desbloqueado']}
        if hasattr(self, '_insignias_desbloqueadas_previas') and self._insignias_desbloqueadas_previas:
            nuevas = desbloqueadas_ahora - self._insignias_desbloqueadas_previas
            for nid in nuevas:
                if nid not in self._notificacion_mostrada:
                    ins_info = next((i for i in estado_rpg['insignias'] if i['id'] == nid), None)
                    if ins_info:
                        self.mostrar_felicitacion_logro(ins_info)
                        self._notificacion_mostrada.add(nid)
                        break
        self._insignias_desbloqueadas_previas = desbloqueadas_ahora

    def filtrar_habitos(self, texto):
        self.filtro_busqueda = texto.strip().lower()
        self.load_habits()

    def load_habits(self):
        try:
            if hasattr(self.ids, 'habits_container'):
                self.ids.habits_container.clear_widgets()

                habits = self._habitos_demo

                # Filtrar si hay texto en el buscador
                if self.filtro_busqueda:
                    habits = [
                        h for h in habits
                        if self.filtro_busqueda in h['nombre'].lower() or
                           self.filtro_busqueda in h.get('categoria', '').lower()
                    ]

                for habit in habits:
                    card = HabitCard(
                        habit_id=habit['id'],
                        nombre=habit['nombre'],
                        descripcion=habit.get('descripcion', ''),
                        sesiones=habit.get('total_sesiones', 0),
                        racha=habit.get('racha_dias', 0),
                        total_min=habit.get('total_segundos', 0) // 60 if habit.get('total_segundos') else 30,
                        objetivo=habit.get('objetivo_diario_minutos', 30),
                        categoria=habit.get('categoria', 'Salud'),
                        horario=habit.get('horario', '07:00 PM'),
                        completado_hoy=habit.get('completado_hoy', False),
                        app=self.app,
                        inicio_screen=self
                    )
                    self.ids.habits_container.add_widget(card)
        except Exception as e:
            print(f"Error cargando hábitos: {e}")

    def actualizar_estado_habito(self, habit_id, completado, sesiones, racha, total_min):
        for h in self._habitos_demo:
            if h['id'] == habit_id:
                h['completado_hoy'] = completado
                h['total_sesiones'] = sesiones
                h['racha_dias'] = racha
                h['total_segundos'] = total_min * 60
                break
        self.cargar_estadisticas()
        self.calcular_progreso_general()

    def add_new_habit(self):
        form = NuevoHabitoForm()
        self.dialog = MDDialog(
            title="Nuevo Hábito HabitPulse",
            type="custom",
            content_cls=form,
            buttons=[
                MDFlatButton(
                    text="Cancelar",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Crear Hábito",
                    md_bg_color=(0.88, 0.11, 0.28, 1),
                    on_release=lambda x: self.crear_habito(form)
                )
            ],
            size_hint=(0.9, None)
        )
        self.dialog.open()

    def crear_habito(self, form):
        nombre = form.nombre_field.text.strip()
        categoria = form.cat_field.text.strip() or "Salud"
        horario = form.horario_field.text.strip() or "07:00 PM"
        obj_text = form.obj_field.text.strip()

        if not nombre:
            return

        try:
            objetivo = int(obj_text) if obj_text else 30
        except:
            objetivo = 30

        nuevo_h = {
            "id": len(self._habitos_demo) + 1,
            "nombre": nombre,
            "descripcion": f"Hábito de {categoria}",
            "total_sesiones": 0,
            "racha_dias": 0,
            "total_segundos": 0,
            "objetivo_diario_minutos": objetivo,
            "categoria": categoria,
            "horario": horario,
            "completado_hoy": False
        }

        self._habitos_demo.append(nuevo_h)
        if self.dialog:
            self.dialog.dismiss()
        self.cargar_estadisticas()
        self.calcular_progreso_general()
        self.load_habits()

    def abrir_detalle_habito(self, habit_id):
        habito = next((h for h in self._habitos_demo if h['id'] == habit_id), None)
        if not habito:
            return
        if self.app:
            self.app.habito_seleccionado = {
                "id": habito['id'],
                "nombre": habito['nombre'],
                "descripcion": habito.get('descripcion', f"Hábito de {habito.get('categoria', 'Salud')}"),
                "objetivo_diario_minutos": habito.get('objetivo_diario_minutos', 30),
                "categoria": habito.get('categoria', 'Salud'),
                "horario": habito.get('horario', '07:00 PM'),
                "total_sesiones": habito.get('total_sesiones', 0),
                "racha_dias": habito.get('racha_dias', 0),
                "total_segundos": habito.get('total_segundos', 0),
                "total_min": (habito.get('total_segundos', 0) // 60) if habito.get('total_segundos') else 0,
                "minutos_hoy": habito.get('objetivo_diario_minutos', 30) if habito.get('completado_hoy') else 0,
                "completado_hoy": habito.get('completado_hoy', False)
            }
            self.app.cambiar_pantalla('detalle_habito', direccion='left')

    def editar_habito_dialog(self, habit_id):
        habito = next((h for h in self._habitos_demo if h['id'] == habit_id), None)
        if not habito:
            return

        form = NuevoHabitoForm()
        form.nombre_field.text = habito['nombre']
        form.cat_field.text = habito.get('categoria', 'Salud')
        form.horario_field.text = habito.get('horario', '07:00 PM')
        form.obj_field.text = str(habito.get('objetivo_diario_minutos', 30))

        self.dialog = MDDialog(
            title="Editar Hábito",
            type="custom",
            content_cls=form,
            buttons=[
                MDFlatButton(
                    text="Cancelar",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Guardar",
                    md_bg_color=(0.88, 0.11, 0.28, 1),
                    on_release=lambda x: self.actualizar_habito(habit_id, form)
                )
            ],
            size_hint=(0.9, None)
        )
        self.dialog.open()

    def actualizar_habito(self, habit_id, form):
        nombre = form.nombre_field.text.strip()
        if not nombre:
            return
        categoria = form.cat_field.text.strip() or "Salud"
        horario = form.horario_field.text.strip() or "07:00 PM"
        try:
            objetivo = int(form.obj_field.text.strip())
        except:
            objetivo = 30

        for h in self._habitos_demo:
            if h['id'] == habit_id:
                h['nombre'] = nombre
                h['categoria'] = categoria
                h['horario'] = horario
                h['objetivo_diario_minutos'] = objetivo
                break

        if self.dialog:
            self.dialog.dismiss()
        self.cargar_estadisticas()
        self.calcular_progreso_general()
        self.load_habits()

    def eliminar_habito_dialog(self, habit_id):
        habito = next((h for h in self._habitos_demo if h['id'] == habit_id), None)
        nombre = habito['nombre'] if habito else "este hábito"
        self.dialog = MDDialog(
            title="¿Eliminar Hábito?",
            text=f"¿Estás seguro de que deseas eliminar '{nombre}'?",
            buttons=[
                MDFlatButton(
                    text="Cancelar",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Eliminar",
                    md_bg_color=(0.9, 0.2, 0.2, 1),
                    on_release=lambda x: self.eliminar_habito(habit_id)
                )
            ],
            size_hint=(0.85, None)
        )
        self.dialog.open()

    def eliminar_habito(self, habit_id):
        self._habitos_demo = [h for h in self._habitos_demo if h['id'] != habit_id]
        if self.dialog:
            self.dialog.dismiss()
        self.cargar_estadisticas()
        self.calcular_progreso_general()
        self.load_habits()

    def abrir_perfil_dialog(self):
        usuario_info = self.app.usuario_actual if self.app else {}
        form = PerfilForm(usuario_info=usuario_info, habitos_list=self._habitos_demo)
        self.dialog = MDDialog(
            title="Perfil de Usuario & Ajustes",
            type="custom",
            content_cls=form,
            buttons=[
                MDFlatButton(
                    text="Cerrar",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Cerrar Sesión",
                    md_bg_color=(0.88, 0.11, 0.28, 1),
                    on_release=lambda x: self.cerrar_sesion_desde_perfil()
                )
            ],
            size_hint=(0.9, None)
        )
        self.dialog.open()

    def abrir_logros_dialog(self):
        minutos_totales = sum((h.get('total_segundos', 0) // 60) for h in self._habitos_demo)
        estado_rpg = SistemaGamificacion.calcular_estado_rpg(self._habitos_demo, minutos_temporizador=minutos_totales)
        
        content = LogrosModalContent()
        if hasattr(content.ids, 'titulo_rango_rpg'):
            content.ids.titulo_rango_rpg.text = f"Nivel {estado_rpg['nivel']}: {estado_rpg['rango']}"
        if hasattr(content.ids, 'icono_rango_rpg'):
            content.ids.icono_rango_rpg.icon = estado_rpg['icono_rango']
        if hasattr(content.ids, 'conteo_desbloqueadas_texto'):
            content.ids.conteo_desbloqueadas_texto.text = f"{estado_rpg['desbloqueadas_count']}/{estado_rpg['total_insignias']} Insignias"
        if hasattr(content.ids, 'barra_nivel_modal'):
            content.ids.barra_nivel_modal.value = estado_rpg['porcentaje_nivel']
        if hasattr(content.ids, 'xp_progreso_modal'):
            content.ids.xp_progreso_modal.text = f"{estado_rpg['xp_total']} / {estado_rpg['xp_max']} XP Acumulados"
        if hasattr(content.ids, 'siguiente_nivel_modal'):
            falta_xp = max(0, estado_rpg['xp_max'] - estado_rpg['xp_total'])
            content.ids.siguiente_nivel_modal.text = f"Faltan {falta_xp} XP para Nvl {estado_rpg['nivel']+1}"
        
        if hasattr(content.ids, 'contenedor_insignias'):
            container = content.ids.contenedor_insignias
            container.clear_widgets()
            
            for ins in estado_rpg['insignias']:
                item = InsigniaCardItem(
                    titulo=ins['titulo'],
                    descripcion=ins['descripcion'],
                    icono=ins['icono'],
                    color_rgba=ins['color_rgba'],
                    progreso_texto=ins['progreso_texto'],
                    xp_texto=f"+{ins['xp']} XP",
                    desbloqueado=ins['desbloqueado']
                )
                container.add_widget(item)
        
        self.dialog = MDDialog(
            title="🏆 Logros & Rango RPG HabitPulse",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(
                    text="¡Entendido, a por más!",
                    md_bg_color=(0.88, 0.11, 0.28, 1),
                    on_release=lambda x: self.dialog.dismiss()
                )
            ],
            size_hint=(0.95, None)
        )
        self.dialog.open()

    def mostrar_felicitacion_logro(self, ins_info):
        dlg = MDDialog(
            title="🏆 ¡NUEVA INSIGNIA DESBLOQUEADA!",
            text=f"¡Excelente constancia! Has desbloqueado '{ins_info['titulo']}' ({ins_info['descripcion']}). Has sumado +{ins_info['xp']} XP para tu rango RPG.",
            buttons=[
                MDRaisedButton(
                    text="¡Aceptar!",
                    md_bg_color=(0.16, 0.85, 0.55, 1),
                    on_release=lambda x: dlg.dismiss()
                )
            ],
            size_hint=(0.85, None)
        )
        dlg.open()

    def cerrar_sesion_desde_perfil(self):
        if self.dialog:
            self.dialog.dismiss()
        if self.app:
            self.app.cerrar_sesion()

    def logout(self):
        if self.app:
            self.app.cerrar_sesion()
