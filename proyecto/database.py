import os
import sqlite3
import bcrypt
from datetime import datetime, timedelta


try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None
    RealDictCursor = None



class BaseDatos:
    def __init__(self):
        db_host = os.getenv("DB_HOST", "localhost")
        db_name = os.getenv("DB_NAME", "habitos_bd")
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "12345")
        db_port = os.getenv("DB_PORT", "5432")

        self.conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port,
        )
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        print("Conectado a la base de datos")
        self._verificar_esquema_compatible()
        self.crear_tablas()

    def _verificar_esquema_compatible(self):
        """Verifica si existen tablas antiguas sin columna 'id' y limpia el esquema si es incompatible."""
        try:
            for tabla in ("usuarios", "habitos"):
                self.cursor.execute("""
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables 
                        WHERE table_schema = 'public' AND table_name = %s
                    ) AS existe_tabla
                """, (tabla,))
                if self.cursor.fetchone()["existe_tabla"]:
                    self.cursor.execute("""
                        SELECT EXISTS (
                            SELECT 1 FROM information_schema.columns 
                            WHERE table_schema = 'public' AND table_name = %s AND column_name = 'id'
                        ) AS tiene_id
                    """, (tabla,))
                    if not self.cursor.fetchone()["tiene_id"]:
                        print(f"Esquema antiguo detectado en '{tabla}'. Recreando tablas limpias...")
                        self.cursor.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
                        self.conn.commit()
                        break
        except Exception as e:
            self.conn.rollback()
            print(f"Error verificando esquema: {e}")

    def _conectar_postgres(self):
        if psycopg2 is None:
            print("Aviso: psycopg2 no está instalado.")
            return False

        configuraciones = [
            {
                "host": os.getenv("DB_HOST", "localhost"),
                "database": os.getenv("DB_NAME", "habitos_bd"),
                "user": os.getenv("DB_USER", "postgres"),
                "password": os.getenv("DB_PASSWORD", "123456"),
                "port": os.getenv("DB_PORT", "5432"),
            },
            {
                "host": "localhost",
                "database": "habitpulse_db",
                "user": "postgres",
                "password": "postgrespassword",
                "port": "5432",
            },
        ]

        for cfg in configuraciones:
            try:
                self.conn = psycopg2.connect(
                    host=cfg["host"],
                    database=cfg["database"],
                    user=cfg["user"],
                    password=cfg["password"],
                    port=cfg["port"],
                    connect_timeout=3,
                )
                self.conn.set_client_encoding("UTF8")
                self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
                self.modo = "postgres"
                print(f"Conectado a PostgreSQL ({cfg['database']})")
                return True
            except UnicodeDecodeError as ue:
                detalle = ue.object.decode("latin-1", errors="replace") if hasattr(ue, "object") else str(ue)
                print(f"Fallo PostgreSQL ({cfg['database']}): {detalle}")
            except Exception as e:
                print(f"Fallo PostgreSQL ({cfg['database']}): {e}")

        return False


    def _conectar_sqlite(self):
        self.modo = "sqlite"
        self.conn = sqlite3.connect(self.ruta_sqlite, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")
        print(f"PostgreSQL no disponible. Usando respaldo local SQLite: {self.ruta_sqlite}")


    def _q(self, sql):
        """Adapta marcadores de parámetros %s (PostgreSQL) a ? (SQLite)."""
        if self.modo == "sqlite":
            return sql.replace("%s", "?")
        return sql
    

    def _one(self):
        fila = self.cursor.fetchone()
        return dict(fila) if fila is not None else None


    def _all(self):
        return [dict(f) for f in self.cursor.fetchall()]

    def crear_tablas(self):
        try:
            if self.modo == "postgres":
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id SERIAL PRIMARY KEY,
                        nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
                        email VARCHAR(100) UNIQUE NOT NULL,
                        contrasena VARCHAR(255) NOT NULL,
                        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS habitos (
                        id SERIAL PRIMARY KEY,
                        usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                        nombre VARCHAR(100) NOT NULL,
                        descripcion TEXT,
                        objetivo_diario_minutos INTEGER DEFAULT 30,
                        categoria VARCHAR(50) DEFAULT 'Salud',
                        icono VARCHAR(50) DEFAULT 'run',
                        color VARCHAR(20) DEFAULT '#3b82f6',
                        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sesiones (
                        id SERIAL PRIMARY KEY,
                        habito_id INTEGER NOT NULL REFERENCES habitos(id) ON DELETE CASCADE,
                        fecha DATE NOT NULL DEFAULT CURRENT_DATE,
                        hora_inicio TIMESTAMP,
                        hora_fin TIMESTAMP,
                        duracion_segundos INTEGER NOT NULL,
                        completada BOOLEAN DEFAULT TRUE,
                        notas TEXT,
                        UNIQUE(habito_id, fecha, hora_inicio)
                    )
                """)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS recordatorios (
                        id SERIAL PRIMARY KEY,
                        habito_id INTEGER NOT NULL REFERENCES habitos(id) ON DELETE CASCADE,
                        activo BOOLEAN DEFAULT FALSE,
                        hora_inicio TIME,
                        hora_fin TIME
                    )
                """)
                self.cursor.execute("""
                    ALTER TABLE recordatorios
                        ADD COLUMN IF NOT EXISTS hora VARCHAR(10),
                        ADD COLUMN IF NOT EXISTS dias_semana VARCHAR(100) DEFAULT 'Lun, Mar, Mié, Jue, Vie, Sáb, Dom',
                        ADD COLUMN IF NOT EXISTS mensaje TEXT DEFAULT ''
                """)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS metas (
                        id SERIAL PRIMARY KEY,
                        usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                        habito_id INTEGER REFERENCES habitos(id) ON DELETE SET NULL,
                        titulo VARCHAR(150) NOT NULL,
                        progreso_porcentaje NUMERIC(5,2) DEFAULT 0.0,
                        fecha_limite DATE,
                        estado VARCHAR(30) DEFAULT 'En progreso',
                        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
            else:
                # Esquema equivalente en SQLite (fallback)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS usuarios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre_usuario TEXT UNIQUE NOT NULL,
                        email TEXT UNIQUE NOT NULL,
                        contrasena TEXT NOT NULL,
                        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS habitos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                        nombre TEXT NOT NULL,
                        descripcion TEXT,
                        objetivo_diario_minutos INTEGER DEFAULT 30,
                        categoria TEXT DEFAULT 'Salud',
                        icono TEXT DEFAULT 'run',
                        color TEXT DEFAULT '#3b82f6',
                        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sesiones (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        habito_id INTEGER NOT NULL REFERENCES habitos(id) ON DELETE CASCADE,
                        fecha DATE NOT NULL DEFAULT CURRENT_DATE,
                        hora_inicio TIMESTAMP,
                        hora_fin TIMESTAMP,
                        duracion_segundos INTEGER NOT NULL,
                        completada INTEGER DEFAULT 1,
                        notas TEXT
                    )
                """)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS recordatorios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        habito_id INTEGER NOT NULL REFERENCES habitos(id) ON DELETE CASCADE,
                        activo INTEGER DEFAULT 0,
                        hora_inicio TEXT,
                        hora_fin TEXT,
                        hora TEXT,
                        dias_semana TEXT DEFAULT 'Lun, Mar, Mié, Jue, Vie, Sáb, Dom',
                        mensaje TEXT DEFAULT ''
                    )
                """)
                self.cursor.execute("""
                    CREATE TABLE IF NOT EXISTS metas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
                        habito_id INTEGER REFERENCES habitos(id) ON DELETE SET NULL,
                        titulo TEXT NOT NULL,
                        progreso_porcentaje REAL DEFAULT 0.0,
                        fecha_limite TEXT,
                        estado TEXT DEFAULT 'En progreso',
                        fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_habitos_usuario ON habitos(usuario_id)")
            self.cursor.execute("CREATE INDEX IF NOT EXISTS idx_metas_usuario ON metas(usuario_id)")

            self.conn.commit()
            print(f"Tablas listas en modo {self.modo.upper()}")

        except Exception as e:
            self.conn.rollback()
            print(f"Error creando tablas: {e}")

    # =================== MÉTODOS DE USUARIOS ===================
    def encriptar_contrasena(self, contrasena):
        sal = bcrypt.gensalt()
        encriptada = bcrypt.hashpw(contrasena.encode("utf-8"), sal)
        return encriptada.decode("utf-8")

    def verificar_contrasena(self, contrasena, contrasena_encriptada):
        try:
            return bcrypt.checkpw(contrasena.encode("utf-8"), contrasena_encriptada.encode("utf-8"))
        except Exception:
            return False

    def registrar_usuario(self, nombre_usuario, email, contrasena):
        try:
            self.cursor.execute(
                self._q("SELECT id FROM usuarios WHERE nombre_usuario=%s OR email=%s"),
                (nombre_usuario, email),
            )
            if self._one():
                return {"exito": False, "mensaje": "Usuario o email ya existen"}

            contrasena_encriptada = self.encriptar_contrasena(contrasena)
            self.cursor.execute(
                self._q("""
                    INSERT INTO usuarios (nombre_usuario, email, contrasena)
                    VALUES (%s, %s, %s)
                """),
                (nombre_usuario, email, contrasena_encriptada),
            )
            self.conn.commit()

            self.cursor.execute(
                self._q("SELECT id, nombre_usuario, email, fecha_creacion FROM usuarios WHERE email=%s"),
                (email,),
            )
            usuario = self._one()
            if usuario:
                usuario["id_usuario"] = usuario["id"]
                usuario["nombre"] = usuario["nombre_usuario"]
                usuario["correo"] = usuario["email"]
            print(f"Usuario registrado: {nombre_usuario}")
            return {"exito": True, "usuario": usuario}
        except Exception as e:
            self.conn.rollback()
            return {"exito": False, "mensaje": str(e)}

        
    def iniciar_sesion(self, usuario_o_email, contrasena):
        try:
            self.cursor.execute(
                self._q("""
                    SELECT id, nombre_usuario, email, contrasena
                    FROM usuarios
                    WHERE nombre_usuario=%s OR email=%s
                """),
                (usuario_o_email, usuario_o_email),
            )
            usuario = self._one()
            if not usuario:
                return {"exito": False, "mensaje": "Usuario no encontrado"}

            if self.verificar_contrasena(contrasena, usuario["contrasena"]):
                return {
                    "exito": True,
                    "usuario": {
                        "id": usuario["id"],
                        "id_usuario": usuario["id"],
                        "nombre": usuario["nombre_usuario"],
                        "nombre_usuario": usuario["nombre_usuario"],
                        "correo": usuario["email"],
                        "email": usuario["email"],
                    },
                }
            return {"exito": False, "mensaje": "Contraseña incorrecta"}
        except Exception as e:
            return {"exito": False, "mensaje": str(e)}

        

    # =================== MÉTODOS DE HÁBITOS ===================
    def crear_habito(self, usuario_id, nombre, descripcion="", objetivo_minutos=30, categoria="Salud"):
        try:
            mapeo_categorias = {
                "Salud": {"icono": "dumbbell", "color": "#10b981"},
                "Aprendizaje": {"icono": "book-open", "color": "#3b82f6"},
                "Productividad": {"icono": "trending-up", "color": "#f59e0b"},
                "Bienestar": {"icono": "leaf", "color": "#06b6d4"}
            }
            
            categoria_info = mapeo_categorias.get(
                categoria, {"icono": "checkbox-blank-circle", "color": "#3b82f6"}
            )


            if self.modo == "postgres":
                self.cursor.execute(
                    """
                    INSERT INTO habitos (usuario_id, nombre, descripcion, objetivo_diario_minutos, categoria, icono, color)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, nombre, descripcion, objetivo_diario_minutos, categoria, icono, color, fecha_creacion
                    """,
                    (
                        usuario_id, nombre, descripcion, objetivo_minutos,
                        categoria, categoria_info["icono"], categoria_info["color"],
                    ),
                )
                habito = self._one()
            else:
 
                self.cursor.execute(
                    """
                    INSERT INTO habitos (usuario_id, nombre, descripcion, objetivo_diario_minutos, categoria, icono, color)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        usuario_id, nombre, descripcion, objetivo_minutos,
                        categoria, categoria_info["icono"], categoria_info["color"],
                    ),
                )
                nuevo_id = self.cursor.lastrowid
                self.cursor.execute(
                    "SELECT id, nombre, descripcion, objetivo_diario_minutos, categoria, icono, color, fecha_creacion FROM habitos WHERE id = ?",
                    (nuevo_id,),
                )
                habito = self._one()
            
            # Crear recordatorio por defecto 
            self.cursor.execute(
                self._q("INSERT INTO recordatorios (habito_id) VALUES (%s)"),
                (habito["id"],),
            )
            self.conn.commit()
            return habito
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error creando hábito: {e}")
            return None

    def obtener_habitos_usuario(self, usuario_id):
        try:
            self.cursor.execute(
                self._q("""
                    SELECT h.*,
                        COUNT(s.id) as total_sesiones,
                        COALESCE(SUM(s.duracion_segundos), 0) as total_segundos,
                        COALESCE(MAX(s.fecha), DATE(h.fecha_creacion)) as ultima_sesion
                    FROM habitos h
                    LEFT JOIN sesiones s ON h.id = s.habito_id
                    WHERE h.usuario_id = %s
                    GROUP BY h.id
                    ORDER BY h.id DESC
                """),
                (usuario_id,),
            )
            habitos = self._all()
            for habito in habitos:
                habito["racha_dias"] = self.calcular_racha_habito(habito["id"])
            return habitos

        except Exception as e:
            print(f"Error obteniendo hábitos: {e}")
            return []

    def obtener_habito_por_id(self, habito_id):
        try:
            self.cursor.execute(
                self._q("""
                    SELECT h.*,
                        COUNT(s.id) as total_sesiones,
                        COALESCE(SUM(s.duracion_segundos), 0) as total_segundos
                    FROM habitos h
                    LEFT JOIN sesiones s ON h.id = s.habito_id
                    WHERE h.id = %s
                    GROUP BY h.id
                """),
                (habito_id,),
            )
            habito = self._one()
            if habito:
                habito["racha_dias"] = self.calcular_racha_habito(habito_id)
                habito["promedio_minutos"] = self.calcular_promedio_minutos(habito_id)
                habito["minutos_hoy"] = self.obtener_minutos_hoy(habito_id)
            return habito

        except Exception as e:
            print(f"Error obteniendo hábito: {e}")
            return None

    def eliminar_habito(self, habito_id):
        try:
            self.cursor.execute(self._q("DELETE FROM habitos WHERE id = %s"), (habito_id,))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error eliminando hábito: {e}")
            return False

    # =================== MÉTODOS DE SESIONES ===================
    def registrar_sesion(self, habito_id, duracion_segundos, hora_inicio=None, hora_fin=None, notas=""):
        try:
            if hora_inicio is None:
                hora_inicio = datetime.now()

            if self.modo == "postgres":
                self.cursor.execute(
                    """
                    INSERT INTO sesiones (habito_id, fecha, hora_inicio, hora_fin, duracion_segundos, notas)
                    VALUES (%s, CURRENT_DATE, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (habito_id, hora_inicio, hora_fin, duracion_segundos, notas),
                )
                sesion = self._one()
            else:
                self.cursor.execute(
                    """
                    INSERT INTO sesiones (habito_id, fecha, hora_inicio, hora_fin, duracion_segundos, notas)
                    VALUES (?, CURRENT_DATE, ?, ?, ?, ?)
                    """,
                    (habito_id, str(hora_inicio), str(hora_fin) if hora_fin else None, duracion_segundos, notas),
                )
                sesion = {"id": self.cursor.lastrowid}

            self.conn.commit()
            return sesion

        except Exception as e:
            self.conn.rollback()
            print(f"Error registrando sesión: {e}")
            return None

    def obtener_sesiones_habito(self, habito_id, limite=7):
        try:
            self.cursor.execute(
                self._q("""
                    SELECT fecha, duracion_segundos, hora_inicio, hora_fin, notas
                    FROM sesiones
                    WHERE habito_id = %s
                    ORDER BY fecha DESC
                    LIMIT %s
                """),
                (habito_id, limite),
            )
            return self._all()
        except Exception as e:
            print(f"Error obteniendo sesiones: {e}")
            return []

    def obtener_minutos_hoy(self, habito_id):
        try:
            self.cursor.execute(
                self._q("""
                    SELECT SUM(duracion_segundos) as total_segundos
                    FROM sesiones
                    WHERE habito_id = %s AND fecha = CURRENT_DATE
                """),
                (habito_id,),
            )
            resultado = self._one()
            if resultado and resultado["total_segundos"]:
                return int(resultado["total_segundos"]) // 60
            return 0
        except Exception as e:
            print(f"Error obteniendo minutos hoy: {e}")
            return 0

    # =================== MÉTODOS DE ESTADÍSTICAS ===================
    @staticmethod
    def _a_fecha(valor):
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, str):
            return datetime.strptime(valor[:10], "%Y-%m-%d").date()
        return valor

    def calcular_racha_habito(self, habito_id):
        try:
            self.cursor.execute(
                self._q("""
                    SELECT DISTINCT fecha FROM sesiones
                    WHERE habito_id = %s
                    ORDER BY fecha DESC
                    LIMIT 7
                """),
                (habito_id,),
            )
            sesiones = self._all()
            if not sesiones:
                return 0

            hoy = datetime.now().date()
            racha = 0
            if self._a_fecha(sesiones[0]["fecha"]) == hoy:
                racha = 1
                for i in range(1, len(sesiones)):
                    fecha_esperada = hoy - timedelta(days=i)
                    if self._a_fecha(sesiones[i]["fecha"]) == fecha_esperada:
                        racha += 1
                    else:
                        break
            return racha
        except Exception as e:
            print(f"Error calculando racha: {e}")
            return 0

    def calcular_promedio_minutos(self, habito_id):
        try:
            self.cursor.execute(
                self._q("""
                    SELECT AVG(duracion_segundos) as promedio_segundos
                    FROM sesiones
                    WHERE habito_id = %s
                """),
                (habito_id,),
            )
            resultado = self._one()
            if resultado and resultado["promedio_segundos"]:
                return int(resultado["promedio_segundos"] // 60)
            return 0
        except Exception as e:
            print(f"Error calculando promedio: {e}")
            return 0

    def obtener_estadisticas_usuario(self, usuario_id):
        try:
            self.cursor.execute(
                self._q("""
                    SELECT
                        COUNT(DISTINCT h.id) as total_habitos,
                        COUNT(DISTINCT s.id) as total_sesiones,
                        COALESCE(SUM(s.duracion_segundos), 0) as total_segundos
                    FROM habitos h
                    LEFT JOIN sesiones s ON h.id = s.habito_id
                    WHERE h.usuario_id = %s
                """),
                (usuario_id,),
            )
            stats = self._one()
            if not stats:
                return {"total_habitos": 0, "total_sesiones": 0, "total_segundos": 0, "racha_total": 0}

            racha_total = self.calcular_racha_total(usuario_id)
            return {
                "total_habitos": stats["total_habitos"],
                "total_sesiones": stats["total_sesiones"],
                "total_segundos": stats["total_segundos"],
                "racha_total": self.calcular_racha_total(usuario_id),
            }
        except Exception as e:
            print(f"Error obteniendo estadísticas: {e}")
            return {"total_habitos": 0, "total_sesiones": 0, "total_segundos": 0, "racha_total": 0}

        
        
    def calcular_racha_total(self, usuario_id):
        try:
            self.cursor.execute(
                self._q("""
                    SELECT DISTINCT s.fecha
                    FROM sesiones s
                    JOIN habitos h ON s.habito_id = h.id
                    WHERE h.usuario_id = %s
                    ORDER BY s.fecha DESC
                    LIMIT 7
                """),
                (usuario_id,),
            )
            fechas_sesiones = self._all()
            if not fechas_sesiones:
                return 0

            hoy = datetime.now().date()
            racha = 0
            if self._a_fecha(fechas_sesiones[0]["fecha"]) == hoy:
                racha = 1
                for i in range(1, len(fechas_sesiones)):
                    fecha_esperada = hoy - timedelta(days=i)
                    if self._a_fecha(fechas_sesiones[i]["fecha"]) == fecha_esperada:
                        racha += 1
                    else:
                        break
            return racha
        except Exception as e:
            print(f"Error calculando racha total: {e}")
            return 0



    # =================== MÉTODOS DE METAS (metas_screen.py) ===================
    def obtener_metas_usuario(self, usuario_id):
        try:
            self.cursor.execute(
                self._q("""
                    SELECT
                        m.id AS id_meta,
                        m.usuario_id AS id_usuario,
                        COALESCE(m.habito_id, 0) AS id_habito,
                        COALESCE(h.nombre, 'General') AS nombre_habito,
                        m.titulo,
                        COALESCE(m.progreso_porcentaje, 0.0) AS progreso_porcentaje,
                        m.fecha_limite,
                        COALESCE(m.estado, 'En progreso') AS estado
                    FROM metas m
                    LEFT JOIN habitos h ON m.habito_id = h.id
                    WHERE m.usuario_id = %s
                    ORDER BY m.id DESC
                """),
                (usuario_id,),
            )
            metas = []
            for item in self._all():
                item["progreso_porcentaje"] = float(item["progreso_porcentaje"])
                item["fecha_limite"] = str(item["fecha_limite"])[:10] if item.get("fecha_limite") else "Sin fecha"
                metas.append(item)
            return metas

        except Exception as e:
            self.conn.rollback()
            print(f"Error obteniendo metas: {e}")
            return []


    def crear_meta(self, usuario_id, habito_id, titulo, progreso_porcentaje=0.0, fecha_limite=None):
        try:
            pct = min(100.0, max(0.0, float(progreso_porcentaje or 0.0)))
            estado = "Completado" if pct >= 100.0 else "En progreso"

            habito_valido = None
            if habito_id:
                self.cursor.execute(self._q("SELECT id FROM habitos WHERE id = %s"), (habito_id,))
                if self._one():
                    habito_valido = habito_id

            fecha_val = fecha_limite if fecha_limite else None

            if self.modo == "postgres":
                self.cursor.execute(
                    """
                    INSERT INTO metas (usuario_id, habito_id, titulo, progreso_porcentaje, fecha_limite, estado)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (usuario_id, habito_valido, titulo, pct, fecha_val, estado),
                )
                fila = self._one()
                nuevo_id = fila["id"] if fila else None
            else:
                self.cursor.execute(
                    """
                    INSERT INTO metas (usuario_id, habito_id, titulo, progreso_porcentaje, fecha_limite, estado)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (usuario_id, habito_valido, titulo, pct, fecha_val, estado),
                )
                nuevo_id = self.cursor.lastrowid

            self.conn.commit()
            return nuevo_id

        except Exception as e:
            self.conn.rollback()
            print(f"Error creando meta: {e}")
            return None
        

    def actualizar_progreso_meta(self, id_meta, nuevo_porcentaje, nuevo_estado=None):
        try:
            pct = min(100.0, max(0.0, float(nuevo_porcentaje)))
            estado = nuevo_estado or ("Completado" if pct >= 100.0 else "En progreso")

            self.cursor.execute(
                self._q("""
                    UPDATE metas
                    SET progreso_porcentaje = %s, estado = %s
                    WHERE id = %s
                """),
                (pct, estado, id_meta),
            )
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error actualizando progreso de meta: {e}")
            return False



    def eliminar_meta(self, id_meta):
        try:
            self.cursor.execute(self._q("DELETE FROM metas WHERE id = %s"), (id_meta,))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error eliminando meta: {e}")
            return False
    

    # =================== MÉTODOS DE RECORDATORIOS ===================
    def actualizar_recordatorio(self, habito_id, activo, hora_inicio=None, hora_fin=None):
        try:
            val_activo = bool(activo) if self.modo == "postgres" else int(bool(activo))
            self.cursor.execute(
                self._q("""
                    UPDATE recordatorios
                    SET activo = %s, hora_inicio = %s, hora_fin = %s
                    WHERE habito_id = %s
                """),
                (val_activo, hora_inicio, hora_fin, habito_id),
            )
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error actualizando recordatorio: {e}")
            return False

    def obtener_recordatorio(self, habito_id):
        try:
            self.cursor.execute(
                self._q("""
                    SELECT activo, hora_inicio, hora_fin
                    FROM recordatorios
                    WHERE habito_id = %s
                """),
                (habito_id,),
            )
            return self._one()
        except Exception as e:
            print(f"Error obteniendo recordatorio: {e}")
            return None



    def obtener_recordatorios_usuario(self, usuario_id):
        try:
            condicion_activo = "r.activo = TRUE" if self.modo == "postgres" else "r.activo = 1"
            default_activo = "FALSE" if self.modo == "postgres" else "0"
            self.cursor.execute(
                self._q(f"""
                    SELECT
                        r.id AS id_recordatorio,
                        r.habito_id AS id_habito,
                        h.nombre AS nombre_habito,
                        r.hora,
                        r.hora_inicio,
                        COALESCE(r.dias_semana, 'Lun, Mar, Mié, Jue, Vie, Sáb, Dom') AS dias_semana,
                        COALESCE(r.activo, {default_activo}) AS activo,
                        COALESCE(r.mensaje, '') AS mensaje
                    FROM recordatorios r
                    JOIN habitos h ON r.habito_id = h.id
                    WHERE h.usuario_id = %s
                      AND (r.hora IS NOT NULL OR r.hora_inicio IS NOT NULL OR {condicion_activo})
                    ORDER BY r.id DESC
                """),
                (usuario_id,),
            )
            lista = []
            for r in self._all():
                hora_str = r.get("hora") or (str(r["hora_inicio"])[:5] if r.get("hora_inicio") else "08:00")
                lista.append({
                    "id_recordatorio": r["id_recordatorio"],
                    "id_habito": r["id_habito"],
                    "nombre_habito": r["nombre_habito"],
                    "hora": str(hora_str)[:5],
                    "dias_semana": r["dias_semana"],
                    "activo": bool(r["activo"]),
                    "mensaje": r["mensaje"],
                })
            return lista
        except Exception as e:
            self.conn.rollback()
            print(f"Error obteniendo recordatorios del usuario: {e}")
            return []



    def crear_recordatorio_v2(self, habito_id, hora, dias_semana, activo=True, mensaje=""):
        try:
            self.cursor.execute(self._q("SELECT id FROM habitos WHERE id = %s"), (habito_id,))
            if not self._one():
                self.cursor.execute("SELECT id FROM habitos ORDER BY id ASC LIMIT 1")
                primero = self._one()
                if not primero:
                    print("No existen hábitos registrados para asociar el recordatorio.")
                    return None
                habito_id = primero["id"]

            hora_limpia = (hora or "08:00").strip()[:5]
            hora_inicio_sql = None
            try:
                datetime.strptime(hora_limpia, "%H:%M")
                hora_inicio_sql = hora_limpia
            except ValueError:
                hora_inicio_sql = None

            val_activo = bool(activo) if self.modo == "postgres" else int(bool(activo))

            if self.modo == "postgres":
                self.cursor.execute(
                    """
                    INSERT INTO recordatorios (habito_id, activo, hora_inicio, hora, dias_semana, mensaje)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (habito_id, val_activo, hora_inicio_sql, hora_limpia, dias_semana, mensaje),
                )
                fila = self._one()
                nuevo_id = fila["id"] if fila else None
            else:
                self.cursor.execute(
                    """
                    INSERT INTO recordatorios (habito_id, activo, hora_inicio, hora, dias_semana, mensaje)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (habito_id, val_activo, hora_inicio_sql, hora_limpia, dias_semana, mensaje),
                )
                nuevo_id = self.cursor.lastrowid

            self.conn.commit()
            return nuevo_id

        except Exception as e:
            self.conn.rollback()
            print(f"Error creando recordatorio V2: {e}")
            return None


    def actualizar_recordatorio_v2(self, id_recordatorio, activo):
        try:
            val_activo = bool(activo) if self.modo == "postgres" else int(bool(activo))
            self.cursor.execute(
                self._q("""
                    UPDATE recordatorios
                    SET activo = %s
                    WHERE id = %s
                """),
                (val_activo, id_recordatorio),
            )
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error actualizando estado de recordatorio: {e}")
            return False



    def eliminar_recordatorio(self, id_recordatorio):
        try:
            self.cursor.execute(self._q("DELETE FROM recordatorios WHERE id = %s"), (id_recordatorio,))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error eliminando recordatorio: {e}")
            return False

        
    
    # =================== AUDITORÍA DE DESERCIÓN (asistente_screen.py) ===================
    def obtener_habitos_en_riesgo(self, usuario_id, dias=7, umbral=50.0):
        try:
            dias_eval = max(1, int(dias))
            fecha_limite_eval = (datetime.now().date() - timedelta(days=dias_eval - 1)).strftime("%Y-%m-%d")

            self.cursor.execute(
                self._q("""
                    SELECT
                        h.id AS id_habito,
                        h.nombre,
                        h.objetivo_diario_minutos,
                        COUNT(DISTINCT s.fecha) AS dias_cumplidos
                    FROM habitos h
                    LEFT JOIN sesiones s
                        ON h.id = s.habito_id AND s.fecha >= %s
                    WHERE h.usuario_id = %s
                    GROUP BY h.id, h.nombre, h.objetivo_diario_minutos
                    ORDER BY dias_cumplidos ASC, h.id ASC
                """),
                (fecha_limite_eval, usuario_id),
            )

            en_riesgo = []
            for f in self._all():
                cumplidos = int(f["dias_cumplidos"] or 0)
                porcentaje = round((cumplidos / dias_eval) * 100.0, 1)
                if porcentaje < float(umbral):
                    obj_min = int(f["objetivo_diario_minutos"] or 30)
                    obj_sugerido = max(5, obj_min // 2)
                    en_riesgo.append({
                        "id_habito": f["id_habito"],
                        "nombre": f["nombre"],
                        "porcentaje": porcentaje,
                        "dias_evaluados": dias_eval,
                        "dias_cumplidos": cumplidos,
                        "diagnostico": (
                            f"Detectado {porcentaje:.0f}% de completitud en los últimos {dias_eval} días "
                            f"({cumplidos} de {dias_eval} días completados)."
                        ),
                        "recomendacion": (
                            f"Reajuste sugerido: reduce temporalmente el objetivo de {obj_min} min "
                            f"a {obj_sugerido} min diarios y activa un recordatorio diario."
                        ),
                    })
            return en_riesgo

        except Exception as e:
            self.conn.rollback()
            print(f"Error auditando hábitos en riesgo: {e}")
            return []



    def cerrar_conexion(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        print("Conexión cerrada")