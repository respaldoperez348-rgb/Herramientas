import os
import subprocess
import datetime
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.card import MDCard
from kivymd.uix.label import MDLabel
from kivy.properties import StringProperty, BooleanProperty
from kivy.metrics import dp
from kivy.uix.scrollview import ScrollView

from gamificacion import SistemaGamificacion
from screens.inicio_screen import LogrosModalContent, InsigniaCardItem


class AvatarItemCard(MDCard):
    icono = StringProperty("lightning-bolt")
    nombre = StringProperty("Rayo")
    es_activo = BooleanProperty(False)

    def __init__(self, on_select_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.on_select_callback = on_select_callback

    def trigger_select(self):
        if self.on_select_callback:
            self.on_select_callback(self.icono)


class PerfilScreen(MDScreen):
    avatar_actual = StringProperty("lightning-bolt")
    nombre_usuario = StringProperty("David.tineo")
    email_usuario = StringProperty("david.tineo@email.com")
    rango_usuario = StringProperty("Nvl 4 Titán de la Rutina • 935 / 1300 XP")
    tema_actual_nombre = StringProperty("Crimson")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.dialog = None

    def on_pre_enter(self):
        self.actualizar_datos_usuario()

    def actualizar_datos_usuario(self):
        if not self.app:
            return

        usuario = getattr(self.app, 'usuario_actual', None) or {}
        self.nombre_usuario = (
            usuario.get("nombre_usuario")
            or usuario.get("nombre")
            or "David.tineo"
        )
        self.email_usuario = (
            usuario.get("email")
            or usuario.get("correo")
            or "david.tineo@email.com"
        )
        self.avatar_actual = usuario.get("avatar", "lightning-bolt")

        # Obtener hábitos para cálculo de RPG
        habitos = self._obtener_habitos()
        minutos_totales = sum((h.get('total_segundos', 0) // 60) for h in habitos)
        estado_rpg = SistemaGamificacion.calcular_estado_rpg(habitos, minutos_temporizador=minutos_totales)

        self.rango_usuario = f"Nivel {estado_rpg['nivel']} • {estado_rpg['rango']} • {estado_rpg['xp_total']} XP"

        if hasattr(self.ids, 'perfil_avatar_icon'):
            self.ids.perfil_avatar_icon.icon = self.avatar_actual

    def _obtener_habitos(self):
        if self.app:
            try:
                inicio = self.app.gestor_pantallas.get_screen('inicio')
                if inicio and hasattr(inicio, '_habitos_demo'):
                    return inicio._habitos_demo
            except Exception:
                pass
        return []

    def volver(self):
        if self.app:
            self.app.cambiar_pantalla('inicio', direccion='right')

    # =================== 1. SELECTOR DE AVATARES ===================
    def abrir_selector_avatares(self):
        avatares = [
            {"icono": "lightning-bolt", "nombre": "Rayo"},
            {"icono": "fire", "nombre": "Fuego"},
            {"icono": "robot", "nombre": "Cyborg"},
            {"icono": "crown", "nombre": "Corona"},
            {"icono": "shield-star", "nombre": "Guardián"},
            {"icono": "star", "nombre": "Estrella"},
            {"icono": "rocket-launch", "nombre": "Cohete"},
            {"icono": "meditation", "nombre": "Zen"},
            {"icono": "sword-cross", "nombre": "Guerrero"},
            {"icono": "heart-pulse", "nombre": "Vital"},
            {"icono": "trophy", "nombre": "Trofeo"},
            {"icono": "account", "nombre": "Clásico"},
        ]

        contenedor = MDBoxLayout(
            orientation='vertical',
            spacing=dp(8),
            size_hint_y=None,
            height=dp(280),
            padding=[dp(4), dp(4), dp(4), dp(4)]
        )

        grid = MDGridLayout(
            cols=3,
            spacing=dp(10),
            size_hint_y=None,
            padding=dp(4)
        )
        grid.bind(minimum_height=grid.setter('height'))

        scroll = ScrollView(size_hint=(1, 1), do_scroll_x=False)
        scroll.add_widget(grid)
        contenedor.add_widget(scroll)

        for av in avatares:
            es_act = (av["icono"] == self.avatar_actual)
            card = AvatarItemCard(
                icono=av["icono"],
                nombre=av["nombre"],
                es_activo=es_act,
                on_select_callback=self.seleccionar_avatar,
                size_hint=(None, None),
                size=(dp(70), dp(70))
            )
            grid.add_widget(card)

        self.dialog = MDDialog(
            title="Seleccionar Avatar",
            type="custom",
            content_cls=contenedor,
            buttons=[
                MDFlatButton(
                    text="Cerrar",
                    on_release=lambda x: self.dialog.dismiss()
                )
            ],
            size_hint=(0.90, None)
        )
        self.dialog.open()

    def seleccionar_avatar(self, icono):
        self.avatar_actual = icono
        if self.app and self.app.usuario_actual:
            self.app.usuario_actual["avatar"] = icono

        if hasattr(self.ids, 'perfil_avatar_icon'):
            self.ids.perfil_avatar_icon.icon = icono

        # Actualizar en Inicio
        try:
            inicio = self.app.gestor_pantallas.get_screen('inicio')
            if inicio:
                if hasattr(inicio, 'avatar_icono'):
                    inicio.avatar_icono = icono
                if hasattr(inicio.ids, 'avatar_icon'):
                    inicio.ids.avatar_icon.icon = icono
        except Exception:
            pass

        if self.dialog:
            self.dialog.dismiss()

    # =================== 2. CAJA AVANCE: GAMIFICACIÓN & REPORTES ===================
    def abrir_muro_logros(self):
        habitos = self._obtener_habitos()
        minutos_totales = sum((h.get('total_segundos', 0) // 60) for h in habitos)
        estado_rpg = SistemaGamificacion.calcular_estado_rpg(habitos, minutos_temporizador=minutos_totales)

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
            title="Muro de Logros e Insignias",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(
                    text="Cerrar",
                    md_bg_color=(0.14, 0.18, 0.26, 1),
                    on_release=lambda x: self.dialog.dismiss()
                )
            ],
            size_hint=(0.92, None)
        )
        self.dialog.open()

    def exportar_reportes(self):
        habitos = self._obtener_habitos()
        minutos_totales = sum((h.get('total_segundos', 0) // 60) for h in habitos)
        estado_rpg = SistemaGamificacion.calcular_estado_rpg(habitos, minutos_temporizador=minutos_totales)

        total_habitos = len(habitos)
        completados = sum(1 for h in habitos if h.get('completado_hoy'))
        porcentaje_dia = (completados / total_habitos * 100) if total_habitos > 0 else 0
        racha_max = max((h.get('racha_dias', 0) for h in habitos), default=0)
        sesiones_totales = sum(h.get('total_sesiones', 0) for h in habitos)
        fecha_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

        # Texto del reporte
        lineas_reporte = [
            "============================================================",
            "           HABITPULSE - REPORTE EJECUTIVO DE HÁBITOS",
            "============================================================",
            f"Fecha de emisión: {fecha_str}",
            f"Usuario: {self.nombre_usuario} ({self.email_usuario})",
            f"Rango RPG: Nivel {estado_rpg['nivel']} - {estado_rpg['rango']} ({estado_rpg['xp_total']} XP)",
            "",
            "------------------------------------------------------------",
            "MÉTRICAS CLAVE DE RENDIMIENTO",
            "------------------------------------------------------------",
            f"• Hábitos Registrados: {total_habitos}",
            f"• Cumplimiento Hoy: {completados}/{total_habitos} ({porcentaje_dia:.1f}%)",
            f"• Racha Máxima Actual: {racha_max} días consecutivos",
            f"• Tiempo Total de Enfoque: {minutos_totales} minutos",
            f"• Sesiones Acumuladas: {sesiones_totales}",
            f"• Logros Desbloqueados: {estado_rpg['desbloqueadas_count']} de {estado_rpg['total_insignias']}",
            "",
            "------------------------------------------------------------",
            "DESGLOSE DE HÁBITOS ACTIVOS",
            "------------------------------------------------------------"
        ]

        for i, h in enumerate(habitos, 1):
            comp = "SÍ" if h.get('completado_hoy') else "NO"
            lineas_reporte.append(
                f"{i}. {h.get('nombre')} [{h.get('categoria', 'General')}]\n"
                f"   - Horario: {h.get('horario', 'No fijado')} | Objetivo: {h.get('objetivo_diario_minutos', 30)}m\n"
                f"   - Racha: {h.get('racha_dias', 0)}d | Sesiones: {h.get('total_sesiones', 0)} | Cumplido Hoy: {comp}"
            )

        lineas_reporte.extend([
            "",
            "------------------------------------------------------------",
            "MURO DE INSIGNIAS Y LOGROS",
            "------------------------------------------------------------"
        ])

        for ins in estado_rpg['insignias']:
            estado = "[DESBLOQUEADO]" if ins['desbloqueado'] else "[EN PROGRESO]"
            lineas_reporte.append(f"{estado} {ins['titulo']}: {ins['progreso_texto']} (+{ins['xp']} XP)")

        lineas_reporte.extend([
            "",
            "============================================================",
            "HabitPulse Architecture - Documento generado automáticamente",
            "============================================================"
        ])

        reporte_texto = "\n".join(lineas_reporte)

        # Guardar en ~/Descargas
        descargas_dir = os.path.expanduser("~/Descargas")
        os.makedirs(descargas_dir, exist_ok=True)
        ruta_txt = os.path.join(descargas_dir, "Reporte_Ejecutivo_Habitos.word")
        ruta_docx = os.path.join(descargas_dir, "Reporte_Ejecutivo_Habitos.pdf")

        with open(ruta_txt, "w", encoding="utf-8") as f:
            f.write(reporte_texto)

        # Generar versión Word .docx si create-word está disponible
        try:
            cmd = [
                "create-word",
                "--title", f"HabitPulse: Reporte Ejecutivo de {self.nombre_usuario}",
                "--text", reporte_texto,
                "--output", ruta_pdf
            ]
            subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass

        # Mostrar diálogo de confirmación
        box = MDBoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None, height=dp(130), padding=dp(6))
        box.add_widget(MDLabel(
            text=f"• Cumplimiento: {porcentaje_dia:.1f}%\n• Racha Activa: {racha_max} días\n• Tiempo Enfoque: {minutos_totales} min\n• Logros: {estado_rpg['desbloqueadas_count']}/{estado_rpg['total_insignias']}",
            font_size="11sp",
            theme_text_color="Custom",
            text_color=(0.75, 0.8, 0.9, 1)
        ))
        box.add_widget(MDLabel(
            text="Archivos guardados en tu carpeta Descargas:\n• Reporte_Ejecutivo_Habitos.txt\n• Reporte_Ejecutivo_Habitos.pdf",
            font_size="10.5sp",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.2, 0.8, 0.5, 1)
        ))

        self.dialog = MDDialog(
            title="Reporte Generado",
            type="custom",
            content_cls=box,
            buttons=[
                MDRaisedButton(
                    text="Aceptar",
                    md_bg_color=(0.14, 0.18, 0.26, 1),
                    on_release=lambda x: self.dialog.dismiss()
                )
            ],
            size_hint=(0.90, None)
        )
        self.dialog.open()

    # =================== 3. CAJA APARIENCIA & TEMAS ===================
    def cambiar_tema(self, nombre_tema, palette_name):
        if not self.app:
            return
        colores = {
            "Crimson": (0.88, 0.11, 0.28, 1),
            "Índigo": (0.45, 0.40, 0.95, 1),
            "Cyan": (0.05, 0.75, 0.88, 1),
            "Esmeralda": (0.10, 0.75, 0.50, 1),
            "Slate": (0.50, 0.55, 0.65, 1)
        }
        color_rgba = colores.get(nombre_tema, (0.88, 0.11, 0.28, 1))
        self.app.cambiar_acento(nombre_tema, palette_name, color_rgba)
        self.tema_actual_nombre = nombre_tema

        if hasattr(self.ids, 'label_tema_activo'):
            self.ids.label_tema_activo.text = nombre_tema

    def toggle_modo_oscuro(self):
        if not self.app:
            return
        estilo_actual = self.app.theme_cls.theme_style
        nuevo_estilo = "Light" if estilo_actual == "Dark" else "Dark"
        self.app.aplicar_modo_tema(nuevo_estilo)

        if hasattr(self.ids, 'row_estilo_modo'):
            self.ids.row_estilo_modo.subtitulo = f"Modo activo: {nuevo_estilo}"

    # =================== 4. CAJA GESTIÓN DE CUENTA ===================
    def confirmar_cerrar_sesion(self):
        self.dialog = MDDialog(
            title="Cerrar Sesión",
            text=f"¿Deseas cerrar la sesión activa de {self.nombre_usuario}?",
            buttons=[
                MDFlatButton(
                    text="Cancelar",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Cerrar Sesión",
                    md_bg_color=(0.18, 0.22, 0.32, 1),
                    on_release=lambda x: self._ejecutar_cerrar_sesion()
                )
            ],
            size_hint=(0.88, None)
        )
        self.dialog.open()

    def _ejecutar_cerrar_sesion(self):
        if self.dialog:
            self.dialog.dismiss()
        if self.app:
            self.app.cerrar_sesion()

    def confirmar_eliminar_cuenta(self):
        self.dialog = MDDialog(
            title="Eliminar Cuenta",
            text=(
                f"Esta acción borrará permanentemente la cuenta de {self.nombre_usuario}, "
                "incluyendo hábitos, metas y registros de progreso.\n\n"
                "¿Deseas confirmar la eliminación?"
            ),
            buttons=[
                MDFlatButton(
                    text="Cancelar",
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="Eliminar Cuenta",
                    md_bg_color=(0.75, 0.18, 0.22, 1),
                    on_release=lambda x: self._ejecutar_eliminar_cuenta()
                )
            ],
            size_hint=(0.90, None)
        )
        self.dialog.open()

    def _ejecutar_eliminar_cuenta(self):
        if self.dialog:
            self.dialog.dismiss()
        if self.app:
            if hasattr(self.app, 'eliminar_cuenta'):
                self.app.eliminar_cuenta()
            else:
                self.app.cerrar_sesion()
