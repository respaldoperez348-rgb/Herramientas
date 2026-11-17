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

Window.size = (1080, 680)
Window.resizable = True

class HabitTrackerApp(MDApp):
    # Propiedades dinámicas reactivas para todo el sistema de interfaz (Tokens calibrados)
    bg_app = ColorProperty([0.043, 0.059, 0.090, 1])        # #0B0F17 Slate oscuro
    card_bg = ColorProperty([0.075, 0.098, 0.141, 0.98])    # #131924 Tarjeta
    card_item_bg = ColorProperty([0.094, 0.122, 0.173, 0.95])# #181F2C Sub-tarjeta
    card_border = ColorProperty([0.133, 0.169, 0.235, 1])   # #222B3C Borde sutil
    text_primary = ColorProperty([0.96, 0.97, 0.99, 1])     # #F8FAFC Texto principal
    text_secondary = ColorProperty([0.55, 0.60, 0.70, 1])   # #8C99B3 Texto secundario
    nav_bg = ColorProperty([0.035, 0.051, 0.078, 1])        # #090D14
    color_acento = ColorProperty([0.88, 0.24, 0.36, 1])     # #E03D5C Coral sobrio (no neón)
    color_progreso = ColorProperty([0.06, 0.76, 0.52, 1])   # #10B981 Esmeralda / Menta
    track_bg = ColorProperty([0.12, 0.15, 0.22, 1])         # Fondo de tracks y anillos
    tema_nombre = StringProperty("Coral")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.base_datos = None
        if BaseDatos:
            try:
                self.base_datos = BaseDatos()
                print(f"Base de datos activa en modo: {self.base_datos.modo.upper()}")
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
            'sidebar_nav.kv',
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
            # Buscar en screens/kv/ y fallback a screens/
            ruta_kv = os.path.join(base_dir, 'screens', 'kv', kv)
            if not os.path.exists(ruta_kv):
                ruta_kv = os.path.join(base_dir, 'screens', kv)

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
            self.bg_app = [0.97, 0.98, 0.99, 1]          # #F8FAFC Blanco slate limpio
            self.card_bg = [1.0, 1.0, 1.0, 1.0]           # #FFFFFF Tarjeta nítida
            self.card_item_bg = [0.95, 0.96, 0.98, 1.0]  # #F1F5F9 Elemento interno
            self.card_border = [0.88, 0.90, 0.94, 1.0]   # #E2E8F0 Borde con contraste
            self.text_primary = [0.06, 0.09, 0.16, 1.0]  # #0F172A Texto oscuro nítido
            self.text_secondary = [0.40, 0.46, 0.56, 1.0]# #64748B Texto secundario legible
            self.nav_bg = [1.0, 1.0, 1.0, 1.0]
            self.track_bg = [0.88, 0.90, 0.94, 1.0]      # Fondo claro para progreso
            self.color_progreso = [0.02, 0.62, 0.44, 1.0]# #059669 Verde esmeralda con contraste
        else:
            self.bg_app = [0.043, 0.059, 0.090, 1]
            self.card_bg = [0.075, 0.098, 0.141, 0.98]
            self.card_item_bg = [0.094, 0.122, 0.173, 0.95]
            self.card_border = [0.133, 0.169, 0.235, 1]
            self.text_primary = [0.96, 0.97, 0.99, 1]
            self.text_secondary = [0.55, 0.60, 0.70, 1]
            self.nav_bg = [0.035, 0.051, 0.078, 1]
            self.track_bg = [0.12, 0.15, 0.22, 1]
            self.color_progreso = [0.06, 0.76, 0.52, 1]

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
