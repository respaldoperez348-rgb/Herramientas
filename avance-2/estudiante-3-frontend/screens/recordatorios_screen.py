from kivymd.uix.screen import MDScreen
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton, MDFillRoundFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.pickers import MDTimePicker
from kivy.properties import StringProperty, BooleanProperty, NumericProperty
from datetime import time


class RecordatorioCard(MDCard):
    id_recordatorio = NumericProperty(0)
    id_habito = NumericProperty(0)
    nombre_habito = StringProperty("Hábito")
    hora = StringProperty("08:00")
    dias_semana = StringProperty("Lun, Mar, Mié, Jue, Vie")
    activo = BooleanProperty(True)
    mensaje = StringProperty("")

    def __init__(self, **kwargs):
        self.screen_padre = kwargs.pop('screen_padre', None)
        super().__init__(**kwargs)

    def cambiar_estado_switch(self, nuevo_estado):
        if self.activo != nuevo_estado:
            self.activo = nuevo_estado
            if self.screen_padre:
                self.screen_padre.cambiar_estado_recordatorio(self.id_recordatorio, nuevo_estado)

    def eliminar_recordatorio(self):
        if self.screen_padre:
            self.screen_padre.confirmar_eliminar_recordatorio(self.id_recordatorio, self.nombre_habito)


class FormularioNuevoRecordatorio(MDBoxLayout):
    def __init__(self, lista_habitos, abrir_time_picker_callback, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = "10dp"
        self.size_hint_y = None
        self.height = "320dp"

        self.habitos = lista_habitos
        self.habito_seleccionado_id = self.habitos[0]['id'] if self.habitos else 1
        self.habito_seleccionado_nombre = self.habitos[0]['nombre'] if self.habitos else "General"
        self.hora_seleccionada = "08:00"
        self.dias_activos = ["Lun", "Mar", "Mié", "Jue", "Vie"]

        # 1. Selector de Hábito
        self.btn_habito = MDRaisedButton(
            text=f"Hábito: {self.habito_seleccionado_nombre}",
            size_hint_x=1,
            md_bg_color=(0.15, 0.20, 0.30, 1),
            on_release=self.abrir_menu_habitos
        )
        self.add_widget(self.btn_habito)

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

        # 2. Selector de Hora con TimePicker
        box_hora = MDBoxLayout(orientation='horizontal', spacing="8dp", size_hint_y=None, height="38dp")
        self.btn_hora = MDRaisedButton(
            text=f"Hora: {self.hora_seleccionada}",
            size_hint_x=0.6,
            md_bg_color=(0.18, 0.23, 0.33, 1),
            on_release=lambda x: abrir_time_picker_callback(self.actualizar_hora)
        )
        box_hora.add_widget(self.btn_hora)

        self.campo_hora_manual = MDTextField(
            text=self.hora_seleccionada,
            hint_text="HH:MM",
            size_hint_x=0.4,
            mode="rectangle"
        )
        box_hora.add_widget(self.campo_hora_manual)
        self.add_widget(box_hora)

        # 3. Días de la semana interactivos
        box_dias = MDBoxLayout(orientation='horizontal', spacing="4dp", size_hint_y=None, height="36dp")
        self.botones_dias = {}
        todos_dias = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
        for dia in todos_dias:
            activo = dia in self.dias_activos
            btn = MDFillRoundFlatButton(
                text=dia[0],
                font_size="10sp",
                size_hint_x=1.0 / 7.0,
                md_bg_color=(0, 0.75, 1, 0.9) if activo else (0.15, 0.18, 0.25, 1),
                text_color=(1, 1, 1, 1) if activo else (0.6, 0.65, 0.75, 1)
            )
            btn.bind(on_release=lambda instance, d=dia: self.toggle_dia(d))
            self.botones_dias[dia] = btn
            box_dias.add_widget(btn)
        self.add_widget(box_dias)

        # 4. Mensaje personalizado
        self.campo_mensaje = MDTextField(
            hint_text="Mensaje del recordatorio",
            text="¡Momento de tu hábito!",
            mode="rectangle"
        )
        self.add_widget(self.campo_mensaje)

        # 5. Switch Activo
        box_switch = MDBoxLayout(orientation='horizontal', size_hint_y=None, height="34dp", spacing="10dp")
        self.switch_activo = MDSwitch(active=True, size_hint=(None, None), size=("40dp", "24dp"))
        box_switch.add_widget(self.switch_activo)
        self.add_widget(box_switch)

    def abrir_menu_habitos(self, *args):
        if self.menu_habitos:
            self.menu_habitos.open()

    def seleccionar_habito(self, habito):
        self.habito_seleccionado_id = habito['id']
        self.habito_seleccionado_nombre = habito['nombre']
        self.btn_habito.text = f"Hábito: {habito['nombre']}"
        self.menu_habitos.dismiss()

    def actualizar_hora(self, nueva_hora_str):
        self.hora_seleccionada = nueva_hora_str
        self.btn_hora.text = f"Hora: {nueva_hora_str}"
        self.campo_hora_manual.text = nueva_hora_str

    def toggle_dia(self, dia):
        if dia in self.dias_activos:
            self.dias_activos.remove(dia)
            self.botones_dias[dia].md_bg_color = (0.15, 0.18, 0.25, 1)
            self.botones_dias[dia].text_color = (0.6, 0.65, 0.75, 1)
        else:
            self.dias_activos.append(dia)
            self.botones_dias[dia].md_bg_color = (0, 0.75, 1, 0.9)
            self.botones_dias[dia].text_color = (1, 1, 1, 1)


class RecordatoriosScreen(MDScreen):
    # Datos iniciales simulados alineados a PostgreSQL V2 / seed.sql
    _recordatorios_locales = [
        {
            "id_recordatorio": 1,
            "id_habito": 1,
            "nombre_habito": "Beber 2L de agua",
            "hora": "08:30",
            "dias_semana": "Lun, Mar, Mié, Jue, Vie, Sáb, Dom",
            "activo": True,
            "mensaje": "¡Toma un vaso grande de agua fresca para iniciar el día con energía!"
        },
        {
            "id_recordatorio": 2,
            "id_habito": 2,
            "nombre_habito": "Lectura técnica 30 min",
            "hora": "19:00",
            "dias_semana": "Lun, Mar, Mié, Jue, Vie",
            "activo": True,
            "mensaje": "Momento de avanzar 1 capítulo de arquitectura limpia antes de cenar."
        },
        {
            "id_recordatorio": 3,
            "id_habito": 3,
            "nombre_habito": "Rutina de pesas",
            "hora": "18:00",
            "dias_semana": "Lun, Mié, Vie",
            "activo": False,
            "mensaje": "Prepara tu ropa deportiva y calienta 5 minutos."
        }
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = None
        self.dialog = None
        self.time_picker_callback_target = None

    def on_pre_enter(self):
        self.cargar_recordatorios()

    def obtener_lista_habitos(self):
        if self.app and hasattr(self.app, 'base_datos') and getattr(self.app, 'usuario_actual', None):
            try:
                user_id = self.app.usuario_actual.get('id') or self.app.usuario_actual.get('id_usuario', 1)
                habitos = self.app.base_datos.obtener_habitos_usuario(user_id)
                if habitos:
                    return habitos
            except Exception as e:
                print(f"Nota: Usando hábitos locales para recordatorios: {e}")

        return [
            {"id": 1, "nombre": "Beber 2L de agua", "categoria": "Salud"},
            {"id": 2, "nombre": "Lectura técnica 30 min", "categoria": "Estudio"},
            {"id": 3, "nombre": "Rutina de pesas", "categoria": "Deporte"}
        ]

    def cargar_recordatorios(self):
        recordatorios = []
        user_id = 1
        if self.app and getattr(self.app, 'usuario_actual', None):
            user_id = self.app.usuario_actual.get('id') or self.app.usuario_actual.get('id_usuario', 1)

        # Consultar BD si tiene método para listar recordatorios V2
        if self.app and hasattr(self.app, 'base_datos') and hasattr(self.app.base_datos, 'obtener_recordatorios_usuario'):
            try:
                recordatorios = self.app.base_datos.obtener_recordatorios_usuario(user_id)
            except Exception as e:
                print(f"Error consultando recordatorios en BD: {e}")
                recordatorios = self._recordatorios_locales
        else:
            recordatorios = self._recordatorios_locales

        # Actualizar banner de conteo
        activos_count = sum(1 for r in recordatorios if r.get('activo', False))
        if hasattr(self.ids, 'texto_recordatorios_activos'):
            self.ids.texto_recordatorios_activos.text = f"{activos_count} recordatorios activos hoy"

        # Poblar contenedor
        container = self.ids.recordatorios_container
        container.clear_widgets()

        for r in recordatorios:
            card = RecordatorioCard(
                id_recordatorio=r.get('id_recordatorio', 0),
                id_habito=r.get('id_habito', 0),
                nombre_habito=r.get('nombre_habito', 'Hábito'),
                hora=str(r.get('hora', '08:00'))[:5],
                dias_semana=r.get('dias_semana', 'Diario'),
                activo=bool(r.get('activo', True)),
                mensaje=r.get('mensaje', ''),
                screen_padre=self
            )
            container.add_widget(card)

    def cambiar_estado_recordatorio(self, id_recordatorio, nuevo_activo):
        if self.app and hasattr(self.app, 'base_datos') and hasattr(self.app.base_datos, 'actualizar_recordatorio_v2'):
            try:
                self.app.base_datos.actualizar_recordatorio_v2(id_recordatorio, nuevo_activo)
            except Exception as e:
                print(f"Error actualizando estado recordatorio en BD: {e}")

        for r in self._recordatorios_locales:
            if r.get('id_recordatorio') == id_recordatorio:
                r['activo'] = nuevo_activo
                break

        # Actualizar conteo en banner
        activos_count = sum(1 for r in self._recordatorios_locales if r.get('activo', False))
        if hasattr(self.ids, 'texto_recordatorios_activos'):
            self.ids.texto_recordatorios_activos.text = f"{activos_count} recordatorios activos hoy"

    def confirmar_eliminar_recordatorio(self, id_recordatorio, nombre_habito):
        def _eliminar(*args):
            if self.dialog:
                self.dialog.dismiss()
            self._eliminar_recordatorio_ejecutar(id_recordatorio)

        self.dialog = MDDialog(
            title="¿Eliminar Recordatorio?",
            text=f"¿Deseas eliminar la alerta para '{nombre_habito}'?",
            buttons=[
                MDFlatButton(text="Cancelar", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Eliminar", md_bg_color=(0.9, 0.25, 0.25, 1), on_release=_eliminar)
            ]
        )
        self.dialog.open()

    def _eliminar_recordatorio_ejecutar(self, id_recordatorio):
        if self.app and hasattr(self.app, 'base_datos') and hasattr(self.app.base_datos, 'eliminar_recordatorio'):
            try:
                self.app.base_datos.eliminar_recordatorio(id_recordatorio)
            except Exception as e:
                print(f"Error eliminando recordatorio de BD: {e}")

        self._recordatorios_locales = [r for r in self._recordatorios_locales if r.get('id_recordatorio') != id_recordatorio]
        self.cargar_recordatorios()

    def abrir_time_picker(self, callback_destino):
        self.time_picker_callback_target = callback_destino
        try:
            time_dialog = MDTimePicker()
            time_dialog.bind(time=self._on_time_picker_selected)
            time_dialog.open()
        except Exception as e:
            print(f"TimePicker nativo no disponible o en entorno sin display: {e}")

    def _on_time_picker_selected(self, instance, time_obj):
        hora_str = time_obj.strftime("%H:%M")
        if self.time_picker_callback_target:
            self.time_picker_callback_target(hora_str)

    def mostrar_dialogo_nuevo_recordatorio(self):
        habitos = self.obtener_lista_habitos()
        self.form_recordatorio = FormularioNuevoRecordatorio(habitos, self.abrir_time_picker)

        def _guardar(*args):
            id_hab = self.form_recordatorio.habito_seleccionado_id
            nom_hab = self.form_recordatorio.habito_seleccionado_nombre
            hora = self.form_recordatorio.campo_hora_manual.text.strip() or self.form_recordatorio.hora_seleccionada
            dias_str = ", ".join(self.form_recordatorio.dias_activos) if self.form_recordatorio.dias_activos else "Diario"
            mensaje = self.form_recordatorio.campo_mensaje.text.strip()
            activo = self.form_recordatorio.switch_activo.active

            self.guardar_nuevo_recordatorio(id_hab, nom_hab, hora, dias_str, mensaje, activo)
            if self.dialog:
                self.dialog.dismiss()

        self.dialog = MDDialog(
            title="Programar Horario de Hábito",
            type="custom",
            content_cls=self.form_recordatorio,
            buttons=[
                MDFlatButton(text="Cancelar", on_release=lambda x: self.dialog.dismiss()),
                MDRaisedButton(text="Guardar Horario", md_bg_color=(0, 0.7, 0.9, 1), on_release=_guardar)
            ]
        )
        self.dialog.open()

    def guardar_nuevo_recordatorio(self, id_habito, nombre_habito, hora, dias_semana, mensaje, activo):
        nuevo_rec_dict = {
            "id_recordatorio": len(self._recordatorios_locales) + 1,
            "id_habito": id_habito,
            "nombre_habito": nombre_habito,
            "hora": hora,
            "dias_semana": dias_semana,
            "activo": activo,
            "mensaje": mensaje
        }

        if self.app and hasattr(self.app, 'base_datos') and hasattr(self.app.base_datos, 'crear_recordatorio_v2'):
            try:
                nuevo_id = self.app.base_datos.crear_recordatorio_v2(id_habito, hora, dias_semana, activo, mensaje)
                if nuevo_id:
                    nuevo_rec_dict["id_recordatorio"] = nuevo_id
            except Exception as e:
                print(f"Error creando recordatorio en BD: {e}")

        self._recordatorios_locales.append(nuevo_rec_dict)
        self.cargar_recordatorios()
