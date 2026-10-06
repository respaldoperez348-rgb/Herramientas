from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDFillRoundFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivy.uix.screenmanager import SlideTransition
from kivy.properties import StringProperty, NumericProperty
from datetime import datetime

class HabitCard(MDCard):
    habit_id = None
    nombre = StringProperty("")
    descripcion = StringProperty("")
    sesiones = NumericProperty(0)
    racha = NumericProperty(0)
    total_min = NumericProperty(0)
    objetivo = NumericProperty(30)
    
    def __init__(self, **kwargs):
        self.habit_id = kwargs.pop('habit_id', None)
        
        # Extraer valores antes de llamar a super()
        nombre_value = kwargs.pop('nombre', "")
        descripcion_value = kwargs.pop('descripcion', "")
        sesiones_value = kwargs.pop('sesiones', 0)
        racha_value = kwargs.pop('racha', 0)
        total_min_value = kwargs.pop('total_min', 0)
        objetivo_value = kwargs.pop('objetivo', 30)
        
        super().__init__(**kwargs)
        
        # Asignar valores después de inicializar
        self.nombre = nombre_value
        self.descripcion = descripcion_value
        self.sesiones = sesiones_value
        self.racha = racha_value
        self.total_min = total_min_value
        self.objetivo = objetivo_value
        
        # Crear menú contextual
        self.menu = None
        self.crear_menu_contextual()
    
    def crear_menu_contextual(self):
        menu_items = [
            {
                "text": "Editar",
                "viewclass": "OneLineListItem",
                "on_release": lambda: self.editar_habito(),
            },
            {
                "text": "Eliminar",
                "viewclass": "OneLineListItem", 
                "on_release": lambda: self.eliminar_habito(),
            },
        ]
        
        self.menu = MDDropdownMenu(
            caller=self,
            items=menu_items,
            width_mult=4,
        )
    
    def editar_habito(self):
        self.menu.dismiss()
        if hasattr(self, 'app') and hasattr(self.app, 'gestor_pantallas'):
            for screen in self.app.gestor_pantallas.screens:
                if isinstance(screen, InicioScreen):
                    screen.editar_habito_dialog(self.habit_id)
                    break
    
    def eliminar_habito(self):
        self.menu.dismiss()
        if hasattr(self, 'app') and hasattr(self.app, 'gestor_pantallas'):
            for screen in self.app.gestor_pantallas.screens:
                if isinstance(screen, InicioScreen):
                    screen.eliminar_habito_dialog(self.habit_id)
                    break
    
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            if touch.button == 'right':  # Click derecho para menú contextual
                if self.menu:
                    self.menu.open()
                return True
        return super().on_touch_down(touch)
    
    def on_release(self):
        pass

class NuevoHabitoForm(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = 15
        self.padding = 10
        self.size_hint_y = None
        self.height = 350
        
        self.nombre_field = MDTextField(
            hint_text="Nombre del hábito",
            mode="rectangle",
            size_hint_y=None,
            height=50
        )
        self.add_widget(self.nombre_field)
        
        self.desc_field = MDTextField(
            hint_text="Descripción (opcional)",
            mode="rectangle",
            multiline=True,
            size_hint_y=None,
            height=80
        )
        self.add_widget(self.desc_field)
        
        self.obj_field = MDTextField(
            hint_text="Objetivo diario (minutos)",
            mode="rectangle",
            size_hint_y=None,
            height=50,
            input_filter="int"
        )
        self.obj_field.text = "30"
        self.add_widget(self.obj_field)
        
        self.cat_field = MDTextField(
            hint_text="Categoría (Salud, Estudio, Deporte)",
            mode="rectangle",
            size_hint_y=None,
            height=50
        )
        self.cat_field.text = "Salud"
        self.add_widget(self.cat_field)

class InicioScreen(MDScreen):
    _habitos_demo = [
        {"id": 1, "nombre": "Beber 2L de agua", "descripcion": "Meta diaria de hidratación", "total_sesiones": 4, "racha_dias": 4, "total_segundos": 7200, "objetivo_diario_minutos": 30, "categoria": "Salud"},
        {"id": 2, "nombre": "Lectura técnica 30 min", "descripcion": "Libros de arquitectura y patrones", "total_sesiones": 2, "racha_dias": 1, "total_segundos": 3600, "objetivo_diario_minutos": 30, "categoria": "Estudio"},
        {"id": 3, "nombre": "Rutina de pesas", "descripcion": "Entrenamiento de fuerza", "total_sesiones": 3, "racha_dias": 3, "total_segundos": 5400, "objetivo_diario_minutos": 45, "categoria": "Deporte"}
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None 
        self.current_user_id = None
        self.dialog = None
    
    def on_pre_enter(self):
        if not self.app or not getattr(self.app, 'usuario_actual', None):
            if self.app:
                self.app.usuario_actual = {"id": 1, "id_usuario": 1, "nombre_usuario": "Manuel David", "email": "david.tineo@email.com"}
        
        if self.app and self.app.usuario_actual:
            self.current_user_id = self.app.usuario_actual.get("id") or self.app.usuario_actual.get("id_usuario", 1)
            username = self.app.usuario_actual.get("nombre_usuario") or self.app.usuario_actual.get("nombre", "Manuel David")
            
            if hasattr(self.ids, 'bienvenido'):
                self.ids.bienvenido.text = f"¡Hola, {username}!"
            
            self.cargar_estadisticas()
            self.calcular_progreso_general()
            self.load_habits()
    
    def cargar_estadisticas(self):
        estadisticas = None
        if self.app and hasattr(self.app, 'base_datos'):
            try:
                estadisticas = self.app.base_datos.obtener_estadisticas_usuario(self.current_user_id)
            except Exception as e:
                print(f"Nota: Usando estadísticas locales: {e}")
                
        if not estadisticas or not isinstance(estadisticas, dict):
            estadisticas = {
                'total_sesiones': 9,
                'total_segundos': 16200,
                'racha_total': 4,
                'minutos_hoy': 25
            }
            
        if hasattr(self.ids, 'sesiones'):
            self.ids.sesiones.text = str(estadisticas.get('total_sesiones', 9))
        
        if hasattr(self.ids, 'tiempo'):
            total_min = estadisticas.get('total_segundos', 0) // 60
            self.ids.tiempo.text = str(total_min or 120)
        
        if hasattr(self.ids, 'racha'):
            self.ids.racha.text = str(estadisticas.get('racha_total', 4))
        
        if hasattr(self.ids, 'hoy'):
            minutos_hoy = self.obtener_minutos_hoy_usuario()
            self.ids.hoy.text = str(minutos_hoy or 25)
    
    def calcular_progreso_general(self):
        """Calcula el progreso general de todos los hábitos"""
        habits = []
        if self.app and hasattr(self.app, 'base_datos'):
            try:
                habits = self.app.base_datos.obtener_habitos_usuario(self.current_user_id)
            except Exception as e:
                habits = self._habitos_demo
        else:
            habits = self._habitos_demo
        
        if not habits:
            porcentaje = 0
        else:
            total_objetivo = 0
            total_realizado = 0
            for habit in habits:
                objetivo = habit.get('objetivo_diario_minutos', 30)
                total_objetivo += objetivo
                minutos_hoy = 0
                if self.app and hasattr(self.app, 'base_datos'):
                    try:
                        minutos_hoy = self.app.base_datos.obtener_minutos_hoy(habit['id'])
                    except Exception:
                        minutos_hoy = 20
                else:
                    minutos_hoy = 20
                total_realizado += min(minutos_hoy, objetivo)
            
            porcentaje = int((total_realizado / total_objetivo) * 100) if total_objetivo > 0 else 65
        
        if hasattr(self.ids, 'barra_progreso_general'):
            self.ids.barra_progreso_general.value = porcentaje
        if hasattr(self.ids, 'progreso_general_porcentaje'):
            self.ids.progreso_general_porcentaje.text = f"{porcentaje}%"
    
    def obtener_minutos_hoy_usuario(self):
        if not self.app or not hasattr(self.app, 'base_datos'):
            return 25
            
        try:
            habits = self.app.base_datos.obtener_habitos_usuario(self.current_user_id)
            if not habits:
                return 25
            total_minutos_hoy = 0
            for habit in habits:
                minutos_hoy = self.app.base_datos.obtener_minutos_hoy(habit['id'])
                total_minutos_hoy += minutos_hoy
            return total_minutos_hoy
        except Exception:
            return 25
    
    def load_habits(self):
        try:
            if hasattr(self.ids, 'habits_container'):
                self.ids.habits_container.clear_widgets()
                
                habits = []
                if hasattr(self.app, 'base_datos'):
                    try:
                        habits = self.app.base_datos.obtener_habitos_usuario(self.current_user_id)
                    except Exception as e:
                        print(f"Nota: Usando hábitos de prueba: {e}")
                        habits = self._habitos_demo
                else:
                    habits = self._habitos_demo
                
                if not habits:
                    habits = self._habitos_demo
                
                for habit in habits:
                    sesiones = habit.get('total_sesiones', 0)
                    racha = habit.get('racha_dias', 0)
                    total_min = habit.get('total_segundos', 0) // 60 if habit.get('total_segundos') else 30
                    objetivo = habit.get('objetivo_diario_minutos', 30)
                    desc = habit.get('descripcion', '')
                    
                    card = HabitCard(
                        habit_id=habit['id'],
                        nombre=habit['nombre'],
                        descripcion=desc,
                        sesiones=sesiones,
                        racha=racha,
                        total_min=total_min,
                        objetivo=objetivo
                    )
                    card.app = self.app
                    card.bind(on_release=lambda x, h=habit['id']: self.ver_detalle_habito(h))
                    self.ids.habits_container.add_widget(card)
                        
        except Exception as e:
            print(f"Error cargando hábitos: {e}")

    def ver_detalle_habito(self, habit_id):
        habito = None
        if self.app and hasattr(self.app, 'base_datos'):
            try:
                habito = self.app.base_datos.obtener_habito_por_id(habit_id)
            except Exception as e:
                print(f"Error al obtener hábito de BD: {e}")
        
        if not habito:
            for h in self._habitos_demo:
                if h['id'] == habit_id:
                    habito = h
                    break
        
        if habito and self.app:
            self.app.habito_seleccionado = habito
            self.manager.current = 'detalle_habito'
            self.manager.transition.direction = 'left'

    def add_new_habit(self):
        self.dialog = MDDialog(
            title="Nuevo Hábito",
            type="custom",
            content_cls=NuevoHabitoForm(),
            buttons=[
                MDFlatButton(
                    text="Cancelar",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Crear Hábito",
                    md_bg_color=(0.1, 0.55, 0.9, 1),
                    on_release=self.crear_habito
                )
            ],
            size_hint=(0.85, None)
        )
        self.dialog.open()
    
    def crear_habito(self, *args):
        if not self.dialog:
            return
        
        form = self.dialog.content_cls
        nombre = form.nombre_field.text.strip()
        descripcion = form.desc_field.text.strip()
        objetivo_text = form.obj_field.text.strip()
        categoria = form.cat_field.text.strip() or "Salud"
        
        if not nombre:
            return
        
        try:
            objetivo = int(objetivo_text) if objetivo_text else 30
        except:
            objetivo = 30
        
        nuevo_h = {
            "id": len(self._habitos_demo) + 1,
            "nombre": nombre,
            "descripcion": descripcion,
            "total_sesiones": 0,
            "racha_dias": 0,
            "total_segundos": 0,
            "objetivo_diario_minutos": objetivo,
            "categoria": categoria
        }
        
        if hasattr(self.app, 'base_datos'):
            try:
                self.app.base_datos.crear_habito(
                    self.current_user_id,
                    nombre,
                    descripcion,
                    objetivo,
                    categoria
                )
            except Exception as e:
                print(f"Error creando hábito en BD: {e}")
        
        self._habitos_demo.append(nuevo_h)
        self.dialog.dismiss()
        self.cargar_estadisticas()
        self.calcular_progreso_general()
        self.load_habits()
    
    def editar_habito_dialog(self, habit_id):
        habito = None
        if hasattr(self.app, 'base_datos'):
            try:
                habito = self.app.base_datos.obtener_habito_por_id(habit_id)
            except Exception:
                pass
        if not habito:
            for h in self._habitos_demo:
                if h['id'] == habit_id:
                    habito = h
                    break
        if not habito:
            return
        
        form = NuevoHabitoForm()
        form.nombre_field.text = habito['nombre']
        form.desc_field.text = habito.get('descripcion', '')
        form.obj_field.text = str(habito.get('objetivo_diario_minutos', 30))
        form.cat_field.text = habito.get('categoria', 'Salud')
        
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
                    text="Guardar Cambios",
                    md_bg_color=(0.1, 0.55, 0.9, 1),
                    on_release=lambda x: self.actualizar_habito(habit_id)
                )
            ],
            size_hint=(0.85, None)
        )
        self.dialog.open()
    
    def actualizar_habito(self, habit_id):
        if not self.dialog:
            return
        
        form = self.dialog.content_cls
        nombre = form.nombre_field.text.strip()
        descripcion = form.desc_field.text.strip()
        objetivo_text = form.obj_field.text.strip()
        categoria = form.cat_field.text.strip() or "Salud"
        
        if not nombre:
            return
        
        try:
            objetivo = int(objetivo_text) if objetivo_text else 30
        except:
            objetivo = 30
        
        if hasattr(self.app, 'base_datos'):
            try:
                self.app.base_datos.actualizar_habito(
                    habit_id,
                    nombre,
                    descripcion,
                    objetivo,
                    categoria
                )
            except Exception as e:
                print(f"Error actualizando en BD: {e}")
        
        for h in self._habitos_demo:
            if h['id'] == habit_id:
                h['nombre'] = nombre
                h['descripcion'] = descripcion
                h['objetivo_diario_minutos'] = objetivo
                h['categoria'] = categoria
                break
        
        self.dialog.dismiss()
        self.cargar_estadisticas()
        self.calcular_progreso_general()
        self.load_habits()
    
    def eliminar_habito_dialog(self, habit_id):
        self.dialog = MDDialog(
            title="¿Eliminar Hábito?",
            text="¿Estás seguro de que quieres eliminar este hábito?",
            buttons=[
                MDFlatButton(
                    text="Cancelar",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Eliminar",
                    md_bg_color=(1, 0.3, 0.3, 1),
                    on_release=lambda x: self.eliminar_habito(habit_id)
                )
            ],
            size_hint=(0.85, None)
        )
        self.dialog.open()
    
    def eliminar_habito(self, habit_id):
        if hasattr(self.app, 'base_datos'):
            try:
                self.app.base_datos.eliminar_habito(habit_id)
            except Exception as e:
                print(f"Error eliminando de BD: {e}")
        
        self._habitos_demo = [h for h in self._habitos_demo if h['id'] != habit_id]
        if self.dialog:
            self.dialog.dismiss()
        self.cargar_estadisticas()
        self.calcular_progreso_general()
        self.load_habits()
    
    def logout(self):
        if self.app:
            self.app.cerrar_sesion()