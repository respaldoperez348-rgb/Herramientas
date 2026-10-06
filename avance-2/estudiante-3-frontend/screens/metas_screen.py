from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivy.properties import StringProperty, NumericProperty, ListProperty
from datetime import datetime, timedelta


class MetaCard(MDCard):
    id_meta = NumericProperty(0)
    id_habito = NumericProperty(0)
    titulo = StringProperty("")
    nombre_habito = StringProperty("General")
    fecha_limite = StringProperty("")
    progreso_porcentaje = NumericProperty(0)
    estado = StringProperty("En progreso")

    color_porcentaje = ListProperty([0, 0.97, 1, 1])
    color_estado_fondo = ListProperty([0, 0.75, 1, 0.2])
    color_estado_texto = ListProperty([0, 0.97, 1, 1])

    def __init__(self, **kwargs):
        self.screen_padre = kwargs.pop('screen_padre', None)
        super().__init__(**kwargs)
        self.actualizar_colores()

    def actualizar_colores(self):
        pct = float(self.progreso_porcentaje)
        if pct >= 100.0 or self.estado == "Completado":
            self.color_porcentaje = [0.16, 0.85, 0.55, 1]
            self.color_estado_fondo = [0.16, 0.85, 0.55, 0.2]
            self.color_estado_texto = [0.2, 0.95, 0.6, 1]
            self.estado = "Completado"
        elif self.estado == "Expirada":
            self.color_porcentaje = [1, 0.3, 0.3, 1]
            self.color_estado_fondo = [1, 0.3, 0.3, 0.2]
            self.color_estado_texto = [1, 0.4, 0.4, 1]
        elif pct < 50.0:
            self.color_porcentaje = [1, 0.75, 0.2, 1]
            self.color_estado_fondo = [1, 0.75, 0.2, 0.2]
            self.color_estado_texto = [1, 0.8, 0.3, 1]
        else:
            self.color_porcentaje = [0, 0.97, 1, 1]
            self.color_estado_fondo = [0, 0.75, 1, 0.2]
            self.color_estado_texto = [0, 0.97, 1, 1]

    def sumar_progreso(self, delta):
        nuevo_valor = min(100.0, float(self.progreso_porcentaje) + float(delta))
        if self.screen_padre:
            self.screen_padre.actualizar_progreso_meta(self.id_meta, nuevo_valor)

    def completar_meta(self):
        if self.screen_padre:
            self.screen_padre.actualizar_progreso_meta(self.id_meta, 100.0)

    def eliminar_meta(self):
        if self.screen_padre:
            self.screen_padre.confirmar_eliminar_meta(self.id_meta, self.titulo)


class FormularioNuevaMeta(MDBoxLayout):
    def __init__(self, lista_habitos, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = "12dp"
        self.size_hint_y = None
        self.height = "260dp"

        self.habitos = lista_habitos
        self.habito_seleccionado_id = self.habitos[0]['id'] if self.habitos else 1
        self.habito_seleccionado_nombre = self.habitos[0]['nombre'] if self.habitos else "General"

        # Campo Título
        self.campo_titulo = MDTextField(
            hint_text="Título de la meta (ej. 30 días de hidratación)",
            helper_text="Describe tu objetivo claro",
            helper_text_mode="on_focus",
            mode="rectangle"
        )
        self.add_widget(self.campo_titulo)

        # Botón / Selector de Hábito Vinculado
        self.btn_habito = MDRaisedButton(
            text=f"Hábito: {self.habito_seleccionado_nombre}",
            size_hint_x=1,
            md_bg_color=(0.15, 0.20, 0.30, 1),
            on_release=self.abrir_menu_habitos
        )
        self.add_widget(self.btn_habito)

        # Menú desplegable para hábitos
        menu_items = [
            {
                "text": h['nombre'],
                "viewclass": "OneLineListItem",
                "on_release": lambda x=h: self.seleccionar_habito(x),
            } for h in self.habitos
        ] if self.habitos else []
        self.menu_habitos = MDDropdownMenu(
            caller=self.btn_habito,
            items=menu_items,
            width_mult=4
        )

        # Campo Fecha Límite
        fecha_default = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        self.campo_fecha = MDTextField(
            text=fecha_default,
            hint_text="Fecha límite (AAAA-MM-DD)",
            mode="rectangle"
        )
        self.add_widget(self.campo_fecha)

        # Campo Porcentaje inicial
        self.campo_porcentaje = MDTextField(
            text="0",
            hint_text="Porcentaje inicial (0 - 100)",
            input_filter="int",
            mode="rectangle"
        )
        self.add_widget(self.campo_porcentaje)

    def abrir_menu_habitos(self, *args):
        if self.menu_habitos:
            self.menu_habitos.open()

    def seleccionar_habito(self, habito):
        self.habito_seleccionado_id = habito['id']
        self.habito_seleccionado_nombre = habito['nombre']
        self.btn_habito.text = f"Hábito: {habito['nombre']}"
        self.menu_habitos.dismiss()


class MetasScreen(MDScreen):
    filtro_actual = StringProperty("Todas")

    # Almacén de fallback con datos simulados alineados a PostgreSQL V2 / seed.sql
    _metas_locales = [
        {
            "id_meta": 1,
            "id_usuario": 1,
            "id_habito": 1,
            "nombre_habito": "Beber 2L de agua",
            "titulo": "Hábito 21 días de hidratación constante",
            "progreso_porcentaje": 70.0,
            "fecha_limite": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d"),
            "estado": "En progreso"
        },
        {
            "id_meta": 2,
            "id_usuario": 1,
            "id_habito": 2,
            "nombre_habito": "Lectura técnica 30 min",
            "titulo": "Terminar libro 'Clean Architecture'",
            "progreso_porcentaje": 35.0,
            "fecha_limite": (datetime.now() + timedelta(days=12)).strftime("%Y-%m-%d"),
            "estado": "En progreso"
        },
        {
            "id_meta": 3,
            "id_usuario": 1,
            "id_habito": 3,
            "nombre_habito": "Rutina de pesas",
            "titulo": "Completar 16 sesiones de fuerza este mes",
            "progreso_porcentaje": 100.0,
            "fecha_limite": (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d"),
            "estado": "Completado"
        }
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.dialog = None

    def on_pre_enter(self):
        self.cargar_metas()

    def obtener_lista_habitos(self):
        """Obtiene la lista de hábitos del usuario actual para vincular con metas."""
        if self.app and hasattr(self.app, 'base_datos') and self.app.usuario_actual:
            try:
                user_id = self.app.usuario_actual.get('id') or self.app.usuario_actual.get('id_usuario', 1)
                habitos = self.app.base_datos.obtener_habitos_usuario(user_id)
                if habitos:
                    return habitos
            except Exception as e:
                print(f"Nota: Usando hábitos locales para metas: {e}")

        return [
            {"id": 1, "nombre": "Beber 2L de agua", "categoria": "Salud"},
            {"id": 2, "nombre": "Lectura técnica 30 min", "categoria": "Estudio"},
            {"id": 3, "nombre": "Rutina de pesas", "categoria": "Deporte"}
        ]

    def cargar_metas(self):
        """Carga las metas desde PostgreSQL o desde el almacén local del avance."""
        metas = []
        user_id = 1
        if self.app and getattr(self.app, 'usuario_actual', None):
            user_id = self.app.usuario_actual.get('id') or self.app.usuario_actual.get('id_usuario', 1)

        # Si el modelo de BD tiene obtener_metas_usuario, usarlo
        if self.app and hasattr(self.app, 'base_datos') and hasattr(self.app.base_datos, 'obtener_metas_usuario'):
            try:
                metas = self.app.base_datos.obtener_metas_usuario(user_id)
            except Exception as e:
                print(f"Error consultando metas en BD: {e}")
                metas = self._metas_locales
        else:
            metas = self._metas_locales

        # Calcular métricas globales
        total = len(metas)
        en_progreso = sum(1 for m in metas if m.get('estado') == 'En progreso')
        completadas = sum(1 for m in metas if m.get('estado') == 'Completado' or float(m.get('progreso_porcentaje', 0)) >= 100.0)
        promedio = (sum(float(m.get('progreso_porcentaje', 0)) for m in metas) / total) if total > 0 else 0.0

        if hasattr(self.ids, 'count_en_progreso'):
            self.ids.count_en_progreso.text = str(en_progreso)
        if hasattr(self.ids, 'count_completadas'):
            self.ids.count_completadas.text = str(completadas)
        if hasattr(self.ids, 'avg_porcentaje'):
            self.ids.avg_porcentaje.text = f"{int(promedio)}%"

        # Filtrar metas según la pestaña activa
        metas_filtradas = []
        for m in metas:
            est = m.get('estado', 'En progreso')
            pct = float(m.get('progreso_porcentaje', 0))
            if pct >= 100.0:
                est = "Completado"

            if self.filtro_actual == "Todas":
                metas_filtradas.append(m)
            elif self.filtro_actual == "En progreso" and est == "En progreso":
                metas_filtradas.append(m)
            elif self.filtro_actual == "Completado" and est == "Completado":
                metas_filtradas.append(m)

        # Renderizar en el contenedor
        container = self.ids.metas_container
        container.clear_widgets()

        for m in metas_filtradas:
            pct = float(m.get('progreso_porcentaje', 0))
            est = "Completado" if pct >= 100.0 else m.get('estado', 'En progreso')

            card = MetaCard(
                id_meta=m.get('id_meta', 0),
                id_habito=m.get('id_habito', 0),
                titulo=m.get('titulo', 'Meta sin título'),
                nombre_habito=m.get('nombre_habito', 'Hábito vinculado'),
                fecha_limite=str(m.get('fecha_limite', 'Sin fecha')),
                progreso_porcentaje=pct,
                estado=est,
                screen_padre=self
            )
            container.add_widget(card)

    def aplicar_filtro(self, nombre_filtro):
        self.filtro_actual = nombre_filtro
        self.cargar_metas()

    def actualizar_progreso_meta(self, id_meta, nuevo_porcentaje):
        """Actualiza el porcentaje de una meta en BD o localmente."""
        nuevo_porcentaje = min(100.0, max(0.0, float(nuevo_porcentaje)))
        nuevo_estado = "Completado" if nuevo_porcentaje >= 100.0 else "En progreso"

        actualizado_en_bd = False
        if self.app and hasattr(self.app, 'base_datos') and hasattr(self.app.base_datos, 'actualizar_progreso_meta'):
            try:
                self.app.base_datos.actualizar_progreso_meta(id_meta, nuevo_porcentaje, nuevo_estado)
                actualizado_en_bd = True
            except Exception as e:
                print(f"Error actualizando en BD: {e}")

        # Actualizar en memoria local
        for m in self._metas_locales:
            if m.get('id_meta') == id_meta:
                m['progreso_porcentaje'] = nuevo_porcentaje
                m['estado'] = nuevo_estado
                break

        self.cargar_metas()

    def confirmar_eliminar_meta(self, id_meta, titulo):
        def _eliminar(*args):
            if self.dialog:
                self.dialog.dismiss()
            self._eliminar_meta_ejecutar(id_meta)

        self.dialog = MDDialog(
            title="¿Eliminar Meta?",
            text=f"¿Estás seguro de que deseas eliminar '{titulo}'?",
            buttons=[
                MDFlatButton(text="Cancelar", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Eliminar", md_bg_color=(0.9, 0.25, 0.25, 1), on_release=_eliminar)
            ]
        )
        self.dialog.open()

    def _eliminar_meta_ejecutar(self, id_meta):
        if self.app and hasattr(self.app, 'base_datos') and hasattr(self.app.base_datos, 'eliminar_meta'):
            try:
                self.app.base_datos.eliminar_meta(id_meta)
            except Exception as e:
                print(f"Error eliminando de BD: {e}")

        self._metas_locales = [m for m in self._metas_locales if m.get('id_meta') != id_meta]
        self.cargar_metas()

    def mostrar_dialogo_nueva_meta(self):
        habitos = self.obtener_lista_habitos()
        self.form_nueva_meta = FormularioNuevaMeta(habitos)

        def _guardar(*args):
            titulo = self.form_nueva_meta.campo_titulo.text.strip()
            if not titulo:
                self.form_nueva_meta.campo_titulo.error = True
                return

            fecha = self.form_nueva_meta.campo_fecha.text.strip()
            try:
                pct = float(self.form_nueva_meta.campo_porcentaje.text or 0)
            except ValueError:
                pct = 0.0

            id_hab = self.form_nueva_meta.habito_seleccionado_id
            nom_hab = self.form_nueva_meta.habito_seleccionado_nombre

            self.guardar_nueva_meta(titulo, id_hab, nom_hab, fecha, pct)
            if self.dialog:
                self.dialog.dismiss()

        self.dialog = MDDialog(
            title="Nueva Meta de Hábito",
            type="custom",
            content_cls=self.form_nueva_meta,
            buttons=[
                MDFlatButton(text="Cancelar", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Crear Meta", md_bg_color=(0, 0.7, 0.9, 1), on_release=_guardar)
            ]
        )
        self.dialog.open()

    def guardar_nueva_meta(self, titulo, id_habito, nombre_habito, fecha_limite, porcentaje):
        user_id = 1
        if self.app and getattr(self.app, 'usuario_actual', None):
            user_id = self.app.usuario_actual.get('id') or self.app.usuario_actual.get('id_usuario', 1)

        estado = "Completado" if porcentaje >= 100.0 else "En progreso"

        nueva_meta_dict = {
            "id_meta": len(self._metas_locales) + 1,
            "id_usuario": user_id,
            "id_habito": id_habito,
            "nombre_habito": nombre_habito,
            "titulo": titulo,
            "progreso_porcentaje": porcentaje,
            "fecha_limite": fecha_limite,
            "estado": estado
        }

        if self.app and hasattr(self.app, 'base_datos') and hasattr(self.app.base_datos, 'crear_meta'):
            try:
                nuevo_id = self.app.base_datos.crear_meta(user_id, id_habito, titulo, porcentaje, fecha_limite)
                if nuevo_id:
                    nueva_meta_dict["id_meta"] = nuevo_id
            except Exception as e:
                print(f"Error creando meta en BD: {e}")

        self._metas_locales.append(nueva_meta_dict)
        self.cargar_metas()
