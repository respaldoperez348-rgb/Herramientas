"""Generación del reporte de hábitos en XLSX, con respaldo CSV.

El writer no conoce PostgreSQL ni SQLite: solo consume el diccionario que
devuelve ``BaseDatos.obtener_datos_reporte()``. Si ``openpyxl`` no está
instalado se genera un CSV con BOM UTF-8 para que Excel abra los acentos bien.
"""

import csv
import os
import re
from datetime import datetime

try:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
    from openpyxl.utils import get_column_letter
except ImportError:
    Workbook = None
    Alignment = Border = Font = PatternFill = Side = None
    get_column_letter = None


CABECERAS_HABITOS = [
    "N°",
    "Hábito",
    "Categoría",
    "Objetivo diario (min)",
    "Sesiones completadas",
    "Minutos totales",
    "Racha actual (días)",
    "Metas vinculadas",
]

CABECERAS_METAS = [
    "Hábito",
    "Meta",
    "Progreso (%)",
    "Fecha límite",
    "Estado",
]

COLOR_CORAL = "E03D5C"
COLOR_CABECERA = "1F2937"
COLOR_TEXTO_SECUNDARIO = "64748B"
COLOR_FILA_PAR = "F8FAFC"
COLOR_TOTALES = "D1FAE5"


def _texto(valor, por_defecto="—"):
    if valor is None:
        return por_defecto
    texto = str(valor).strip()
    return texto if texto else por_defecto


def _entero(valor):
    try:
        return int(valor or 0)
    except (TypeError, ValueError):
        return 0


def _porcentaje(valor):
    try:
        return float(valor or 0)
    except (TypeError, ValueError):
        return 0.0


def _subtitulo(datos):
    usuario = datos.get("usuario") or {}
    nombre = _texto(usuario.get("nombre_usuario"), "Usuario")
    email = _texto(usuario.get("email"), "")
    sufijo_email = f" · {email}" if email != "—" else ""
    modo = _texto(datos.get("modo"), "desconocido").upper()
    fuente = _texto(datos.get("fuente_detalle"), "Base de datos real")
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    return (
        f"Usuario: {nombre}{sufijo_email} · Fecha: {fecha} · "
        f"Base de datos: {modo} · Fuente: {fuente}"
    )


def _metas_por_habito(metas, id_habito):
    objetivo = _entero(id_habito)
    return [
        meta for meta in metas
        if isinstance(meta, dict) and _entero(meta.get("id_habito")) == objetivo
    ]


def _resumen_metas(metas, id_habito):
    vinculadas = _metas_por_habito(metas, id_habito)
    if not vinculadas:
        return "—"
    return " | ".join(
        f"{_texto(meta.get('titulo'), 'Meta')} "
        f"({_porcentaje(meta.get('progreso_porcentaje')):.0f}%)"
        for meta in vinculadas
    )


def _filas_habitos(datos):
    habitos = [h for h in (datos.get("habitos") or []) if isinstance(h, dict)]
    habitos = sorted(
        habitos,
        key=lambda h: (
            str(h.get("categoria") or "").lower(),
            str(h.get("nombre") or "").lower(),
        ),
    )
    metas = [m for m in (datos.get("metas") or []) if isinstance(m, dict)]

    filas = []
    for indice, habito in enumerate(habitos, 1):
        total_segundos = _entero(habito.get("total_segundos"))
        filas.append([
            indice,
            _texto(habito.get("nombre"), "Sin nombre"),
            _texto(habito.get("categoria"), "Sin categoría"),
            _entero(habito.get("objetivo_minutos")),
            _entero(habito.get("sesiones_completadas")),
            total_segundos // 60,
            _entero(habito.get("racha_dias")),
            _resumen_metas(metas, habito.get("id_habito")),
        ])
    return filas


def _filas_metas(datos):
    metas = [m for m in (datos.get("metas") or []) if isinstance(m, dict)]
    metas = sorted(
        metas,
        key=lambda m: (
            str(m.get("nombre_habito") or "").lower(),
            str(m.get("fecha_limite") or ""),
        ),
    )
    return [
        [
            _texto(meta.get("nombre_habito"), "General"),
            _texto(meta.get("titulo"), "Meta"),
            _porcentaje(meta.get("progreso_porcentaje")),
            _texto(meta.get("fecha_limite"), "Sin fecha"),
            _texto(meta.get("estado"), "En progreso"),
        ]
        for meta in metas
    ]


def sanear_nombre(nombre):
    """Deja un nombre de archivo seguro para Windows, macOS y Linux."""
    texto = re.sub(r'[<>:"/\\|?*]', "", str(nombre or "usuario"))
    texto = re.sub(r"\s+", " ", texto).strip(" .")
    return texto[:40] or "usuario"


def ruta_reporte(nombre_usuario, extension=".xlsx"):
    """Devuelve una ruta única en Descargas (o en la carpeta de la app)."""
    if not extension.startswith("."):
        extension = "." + extension

    carpeta = os.path.join(os.path.expanduser("~"), "Downloads")
    if not os.path.isdir(carpeta):
        carpeta = os.path.dirname(os.path.abspath(__file__))

    sello = datetime.now().strftime("%Y%m%d_%H%M")
    nombre = f"reporte_habitos_{sanear_nombre(nombre_usuario)}_{sello}{extension}"
    ruta = os.path.join(carpeta, nombre)

    contador = 2
    while os.path.exists(ruta):
        raiz, ext = os.path.splitext(nombre)
        ruta = os.path.join(carpeta, f"{raiz}_{contador}{ext}")
        contador += 1
    return ruta


def _aplicar_titulo(hoja, ultima_columna, titulo, subtitulo):
    for columna in range(1, ultima_columna + 1):
        hoja.cell(row=1, column=columna).fill = PatternFill("solid", fgColor=COLOR_CORAL)
    hoja.merge_cells(start_row=1, start_column=1, end_row=1, end_column=ultima_columna)
    celda = hoja.cell(row=1, column=1, value=titulo)
    celda.font = Font(size=14, bold=True, color="FFFFFF")
    celda.alignment = Alignment(vertical="center", horizontal="left", indent=1)
    hoja.row_dimensions[1].height = 28

    celda = hoja.cell(row=2, column=1, value=subtitulo)
    celda.font = Font(size=10, italic=True, color=COLOR_TEXTO_SECUNDARIO)
    celda.alignment = Alignment(vertical="center", horizontal="left", indent=1)
    hoja.row_dimensions[2].height = 20


def _aplicar_cabecera(hoja, fila, cabeceras):
    for columna, texto in enumerate(cabeceras, 1):
        celda = hoja.cell(row=fila, column=columna, value=texto)
        celda.font = Font(bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor=COLOR_CABECERA)
        celda.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        celda.border = Border(bottom=Side(style="thin", color=COLOR_CORAL))
    hoja.row_dimensions[fila].height = 32


def _aplicar_fila(hoja, fila, valores, columna_envuelta=None):
    borde = Border(bottom=Side(style="hair", color="D8DEE9"))
    for columna, valor in enumerate(valores, 1):
        celda = hoja.cell(row=fila, column=columna, value=valor)
        celda.border = borde
        celda.alignment = Alignment(
            horizontal="left" if columna in (2, 3, 8) else "center",
            vertical="top",
            wrap_text=(columna == columna_envuelta),
        )
        if fila % 2 == 0:
            celda.fill = PatternFill("solid", fgColor=COLOR_FILA_PAR)


def _mensaje_vacio(hoja, fila, ultima_columna, mensaje):
    hoja.merge_cells(
        start_row=fila, start_column=1, end_row=fila, end_column=ultima_columna
    )
    celda = hoja.cell(row=fila, column=1, value=mensaje)
    celda.font = Font(italic=True, color=COLOR_TEXTO_SECUNDARIO)
    celda.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    hoja.row_dimensions[fila].height = 24


def _aviso_fuente(hoja, fila, ultima_columna, texto):
    for columna in range(1, ultima_columna + 1):
        hoja.cell(row=fila, column=columna).fill = PatternFill("solid", fgColor="FEF3C7")
    hoja.merge_cells(
        start_row=fila, start_column=1, end_row=fila, end_column=ultima_columna
    )
    celda = hoja.cell(row=fila, column=1, value=texto)
    celda.font = Font(bold=True, color="92400E")
    celda.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    hoja.row_dimensions[fila].height = 22


def _exportar_xlsx(datos, ruta):
    libro = Workbook()
    subtitulo = _subtitulo(datos)

    hoja = libro.active
    hoja.title = "Resumen hábitos"
    ultima_columna = len(CABECERAS_HABITOS)
    _aplicar_titulo(hoja, ultima_columna, "REPORTE DE HÁBITOS · HabitPulse", subtitulo)
    if datos.get("fuente") == "demo":
        _aviso_fuente(
            hoja,
            3,
            ultima_columna,
            "AVISO: la BD no devolvió hábitos; se exportan los hábitos visibles en Inicio (demo).",
        )
    _aplicar_cabecera(hoja, 4, CABECERAS_HABITOS)

    filas = _filas_habitos(datos)
    if filas:
        for numero, valores in enumerate(filas, 5):
            _aplicar_fila(hoja, numero, valores, columna_envuelta=8)
        ultima_fila = 4 + len(filas)

        fila_total = ultima_fila + 1
        for columna in range(1, ultima_columna + 1):
            hoja.cell(row=fila_total, column=columna).fill = PatternFill(
                "solid", fgColor=COLOR_TOTALES
            )
        etiqueta = hoja.cell(row=fila_total, column=1, value="TOTALES")
        etiqueta.font = Font(bold=True, color="047857")
        hoja.cell(row=fila_total, column=5, value=sum(f[4] for f in filas))
        hoja.cell(row=fila_total, column=6, value=sum(f[5] for f in filas))
        hoja.auto_filter.ref = f"A4:H{ultima_fila}"
    else:
        _mensaje_vacio(
            hoja, 5, ultima_columna, "No hay hábitos registrados para este usuario."
        )

    hoja.freeze_panes = "A5"
    for columna, ancho in enumerate([6, 26, 18, 18, 19, 15, 18, 46], 1):
        hoja.column_dimensions[get_column_letter(columna)].width = ancho

    hoja_metas = libro.create_sheet("Metas vinculadas")
    ultima_columna_metas = len(CABECERAS_METAS)
    _aplicar_titulo(
        hoja_metas,
        ultima_columna_metas,
        "METAS VINCULADAS · HabitPulse",
        subtitulo,
    )
    if datos.get("fuente") == "demo":
        _aviso_fuente(
            hoja_metas,
            3,
            ultima_columna_metas,
            "AVISO: la BD no devolvió hábitos; las metas se muestran sin vínculo de hábito.",
        )
    _aplicar_cabecera(hoja_metas, 4, CABECERAS_METAS)

    filas_metas = _filas_metas(datos)
    if filas_metas:
        for numero, valores in enumerate(filas_metas, 5):
            _aplicar_fila(hoja_metas, numero, valores, columna_envuelta=2)
            hoja_metas.cell(row=numero, column=3).number_format = '0.0"%"'
        hoja_metas.auto_filter.ref = f"A4:E{4 + len(filas_metas)}"
    else:
        _mensaje_vacio(
            hoja_metas, 5, ultima_columna_metas, "No hay metas registradas para este usuario."
        )

    hoja_metas.freeze_panes = "A5"
    for columna, ancho in enumerate([26, 40, 14, 16, 18], 1):
        hoja_metas.column_dimensions[get_column_letter(columna)].width = ancho

    libro.save(ruta)


def _exportar_csv(datos, ruta):
    filas = _filas_habitos(datos)
    filas_metas = _filas_metas(datos)

    with open(ruta, "w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(["REPORTE DE HÁBITOS · HabitPulse"])
        escritor.writerow([_subtitulo(datos)])
        escritor.writerow([])
        escritor.writerow(CABECERAS_HABITOS)

        if filas:
            escritor.writerows(filas)
            escritor.writerow([
                "TOTALES", "", "", "",
                sum(f[4] for f in filas),
                sum(f[5] for f in filas),
                "", "",
            ])
        else:
            escritor.writerow(["No hay hábitos registrados para este usuario."])

        escritor.writerow([])
        escritor.writerow(["METAS VINCULADAS"])
        escritor.writerow(CABECERAS_METAS)
        if filas_metas:
            for fila in filas_metas:
                escritor.writerow([
                    fila[0], fila[1], f"{fila[2]:.1f}%", fila[3], fila[4]
                ])
        else:
            escritor.writerow(["No hay metas registradas para este usuario."])


def exportar_reporte(datos, ruta=None):
    """Escribe el reporte y devuelve ``{'ruta', 'formato', 'hojas'}``."""
    datos = datos if isinstance(datos, dict) else {}
    usuario = datos.get("usuario") or {}
    nombre_usuario = usuario.get("nombre_usuario") if isinstance(usuario, dict) else "usuario"

    if ruta is None:
        ruta = ruta_reporte(nombre_usuario, ".xlsx")
    ruta = str(ruta)

    if Workbook is not None and ruta.lower().endswith(".xlsx"):
        _exportar_xlsx(datos, ruta)
        return {"ruta": ruta, "formato": "xlsx", "hojas": 2}

    ruta_csv = os.path.splitext(ruta)[0] + ".csv"
    _exportar_csv(datos, ruta_csv)
    return {"ruta": ruta_csv, "formato": "csv", "hojas": 1}
