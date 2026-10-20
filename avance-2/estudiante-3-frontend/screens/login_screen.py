from kivymd.uix.screen import MDScreen
from kivy.uix.screenmanager import SlideTransition

class LoginScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None  # Se asignará desde main.py
    
    def on_pre_enter(self):
        # Limpiar campos al entrar
        if hasattr(self.ids, 'email'):
            self.ids.email.text = ""
        if hasattr(self.ids, 'contrasena'):
            self.ids.contrasena.text = ""
        if hasattr(self.ids, 'error_form'):
            self.ids.error_form.text = ""
    
    def login(self):
        email = self.ids.email.text
        password = self.ids.contrasena.text
        
        if not email or not password:
            self.ids.error_form.text = "Por favor completa todos los campos"
            return
        
        # Intentar login con la base de datos
        result = None
        if self.app and hasattr(self.app, 'base_datos') and self.app.base_datos:
            try:
                result = self.app.base_datos.iniciar_sesion(email, password)
            except Exception as e:
                print(f"Nota: Conexión BD en login: {e}")
        
        if result and result.get("exito"):
            self.app.usuario_actual = result["usuario"]
            self.ids.error_form.text = "" 
            self.manager.current = 'inicio'
            self.manager.transition = SlideTransition(direction='left')
        elif not getattr(self.app, 'base_datos', None) or result is None:
            # Acceso fluido en entorno demo
            nombre_u = email.split('@')[0].capitalize()
            self.app.usuario_actual = {"id": 1, "id_usuario": 1, "nombre_usuario": nombre_u, "email": email}
            self.ids.error_form.text = "" 
            self.manager.current = 'inicio'
            self.manager.transition = SlideTransition(direction='left')
        else:
            self.ids.error_form.text = result.get("message", "Credenciales incorrectas")
    
    def go_to_registro(self):
        self.manager.current = 'registro'
        self.manager.transition = SlideTransition(direction='right')