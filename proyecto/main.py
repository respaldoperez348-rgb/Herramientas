from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.text import LabelBase
from kivy.properties import ColorProperty, StringProperty
import os

try:
    from database import BaseDatos
except ImportError:
    BaseDatos = None

from screens.login_screen import LoginScreen
from screens.registro_screen import RegisterScreen
from screens.inicio_screen import InicioScreen
from screens.metas_screen import MetasScreen
from screens.recordatorios_screen import RecordatoriosScreen
from screens.asistente_screen import AsistenteScreen
from screens.detalle_habito_screen import DetalleHabitoScreen
from screens.perfil_screen import PerfilScreen

Window.size = (380, 760)
Window.resizable = False

class HabitTrackerApp(MDApp):
    # Propiedades dinámicas reactivas para todo el sistema de interfaz
    bg_app = ColorProperty([0.03, 0.04, 0.07, 1])
    card_bg = ColorProperty([0.07, 0.09, 0.13, 0.95])
    card_item_bg = ColorProperty([0.08, 0.10, 0.15, 0.85])
    card_border = ColorProperty([1, 1, 1, 0.08])
    text_primary = ColorProperty([0.98, 0.98, 1.0, 1])
    text_secondary = ColorProperty([0.55, 0.60, 0.70, 1])
    nav_bg = ColorProperty([0.06, 0.08, 0.12, 0.95])
    color_acento = ColorProperty([0.88, 0.11, 0.28, 1])
    tema_nombre = StringProperty("Crimson")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.base_datos = None
        if BaseDatos:
            try:
                self.base_datos = BaseDatos()
                print("Base de datos PostgreSQL conectada")
            except Exception as e:
                print(f"Aviso: No se pudo conectar a PostgreSQL ({e}). Operando en modo demostración/local.")
                self.base_datos = None
        
        self.usuario_actual = {
            "id": 1,
            "id_usuario": 1,
            "nombre": "David.tineo",
            "nombre_usuario": "David.tineo",
            "correo": "david.tineo@email.com",
            "email": "david.tineo@email.com",
            "avatar": "lightning-bolt"
        }
        self.habito_seleccionado = None
        self.gestor_pantallas = ScreenManager()
    
    def build(self):
        # REGISTRAR FUENTE DE ICONOS
        try:
            ruta_actual = os.path.dirname(os.path.abspath(__file__))
            ruta_fuente = os.path.join(ruta_actual, "assets", "materialdesignicons-webfont.ttf")
            
            if os.path.exists(ruta_fuente):
                LabelBase.register(name="MaterialDesignIcons", fn_regular=ruta_fuente)
                print("Fuente de iconos registrada")
            else:
                print("No se encontró la fuente de iconos")
        except Exception as e:
            print(f"Error al registrar fuente: {e}")
        
        self.title = "HabitPulse"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        
        self.cargar_archivos_kv()
        
        # Instanciar y registrar pantallas de la aplicación
        pantallas = [
            LoginScreen(name='login'),
            RegisterScreen(name='registro'),
            InicioScreen(name='inicio'),
            MetasScreen(name='metas'),
            RecordatoriosScreen(name='recordatorios'),
            AsistenteScreen(name='asistente'),
            DetalleHabitoScreen(name='detalle_habito'),
            PerfilScreen(name='perfil')
        ]
        
        for pantalla in pantallas:
            pantalla.app = self
            self.gestor_pantallas.add_widget(pantalla)
        
        return self.gestor_pantallas
    
    def cargar_archivos_kv(self):
        archivos_kv = [
            'login_screen.kv',
            'registro_screen.kv',
            'inicio_screen.kv',
            'metas_screen.kv',
            'recordatorios_screen.kv',
            'asistente_screen.kv',
            'detalle_habito_screen.kv',
            'perfil_screen.kv'
        ]
        
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for kv in archivos_kv:
            ruta_kv = os.path.join(base_dir, 'screens', 'kv', kv)
            if os.path.exists(ruta_kv):
                Builder.load_file(ruta_kv)
            else:
                print(f"Advertencia: Archivo KV no encontrado: {ruta_kv}")
    
    def cambiar_pantalla(self, nombre_pantalla, direccion='left'):
        self.gestor_pantallas.transition = SlideTransition(direction=direccion)
        self.gestor_pantallas.current = nombre_pantalla
    
    def cerrar_sesion(self):
        self.usuario_actual = None
        self.habito_seleccionado = None
        self.cambiar_pantalla('login', direccion='right')

    def eliminar_cuenta(self):
        if self.usuario_actual and self.base_datos:
            try:
                user_id = self.usuario_actual.get("id") or self.usuario_actual.get("id_usuario", 1)
                self.base_datos.eliminar_usuario(user_id)
            except Exception as e:
                print(f"Nota: BD al eliminar usuario: {e}")

        try:
            inicio = self.gestor_pantallas.get_screen('inicio')
            if inicio:
                inicio._habitos_demo = []
        except Exception:
            pass

        self.cerrar_sesion()

    def aplicar_modo_tema(self, modo="Dark"):
        self.theme_cls.theme_style = modo
        if modo == "Light":
            self.bg_app = [0.95, 0.96, 0.98, 1]
            self.card_bg = [1.0, 1.0, 1.0, 0.98]
            self.card_item_bg = [0.91, 0.93, 0.96, 0.95]
            self.card_border = [0, 0, 0, 0.09]
            self.text_primary = [0.08, 0.10, 0.15, 1]
            self.text_secondary = [0.42, 0.48, 0.58, 1]
            self.nav_bg = [1.0, 1.0, 1.0, 0.98]
        else:
            self.bg_app = [0.03, 0.04, 0.07, 1]
            self.card_bg = [0.07, 0.09, 0.13, 0.95]
            self.card_item_bg = [0.08, 0.10, 0.15, 0.85]
            self.card_border = [1, 1, 1, 0.08]
            self.text_primary = [0.98, 0.98, 1.0, 1]
            self.text_secondary = [0.55, 0.60, 0.70, 1]
            self.nav_bg = [0.06, 0.08, 0.12, 0.95]

    def cambiar_acento(self, nombre_tema, palette_name, color_rgba):
        self.tema_nombre = nombre_tema
        self.theme_cls.primary_palette = palette_name
        self.color_acento = color_rgba
    
    def on_stop(self):
        if hasattr(self, 'base_datos') and self.base_datos:
            try:
                self.base_datos.cerrar_conexion()
            except Exception:
                pass
        return super().on_stop()

if __name__ == '__main__':
    HabitTrackerApp().run()