from kivy.lang import Builder
from kivymd.app import MDApp
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, SlideTransition
from kivy.core.text import LabelBase
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

Window.size = (380, 760)
Window.resizable = False

class HabitTrackerApp(MDApp):
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
            "nombre": "Manuel David",
            "nombre_usuario": "Manuel David",
            "correo": "david.tineo@email.com",
            "email": "david.tineo@email.com"
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
            DetalleHabitoScreen(name='detalle_habito')
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
            'detalle_habito_screen.kv'
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
    
    def on_stop(self):
        if hasattr(self, 'base_datos') and self.base_datos:
            try:
                self.base_datos.cerrar_conexion()
            except Exception:
                pass
        return super().on_stop()

if __name__ == '__main__':
    HabitTrackerApp().run()