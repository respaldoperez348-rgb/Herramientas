import psycopg2
from psycopg2.extras import RealDictCursor

class DatabaseExtension:


    def __init__(self):
        self.conn = psycopg2.connect(
            host="localhost",
            database="control_habitos",
            user="postgres",
            password="123456",
            port="5432",
        )
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        print("Conectado a la BD desde la extension")
        self.crear_tablas_adicionales()



    def crear_tablas_adicionales(self):
        try:
            #Tabla para la pantalla de Metas de Hábitos
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS metas (
                    id SERIAL PRIMARY KEY,
                    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
                    titulo VARCHAR(100) NOT NULL,
                    progreso_inicial INTEGER DEFAULT 0,
                    dias_vencimiento INTEGER DEFAULT 30,
                    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)


            
            #Tabla para la pantalla de Alarmas Inteligentes
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS alarmas (
                    id SERIAL PRIMARY KEY,
                    id_usuario INTEGER NOT NULL REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
                    titulo VARCHAR(100) NOT NULL,
                    hora_exacta TIME NOT NULL,
                    dias_activos VARCHAR(50) DEFAULT 'Lunes - Viernes',
                    activa BOOLEAN DEFAULT TRUE
                )
            """)
            self.conn.commit()
            print("Tablas adicionales de Metas y Alarmas creadas exitosamente")
        except Exception as e:
            self.conn.rollback()
            print(f"Error creando tablas adicionales: {e}")



    def obtener_perfil_gamificacion(self, usuario_id):
        try:
            self.cursor.execute("""
                SELECT nivel, xp_total, racha_actual, mejor_racha 
                FROM perfil_gamificacion 
                WHERE id_usuario = %s
            """, (usuario_id,))
            
            perfil = self.cursor.fetchone()
            
            #Si el usuario es nuevo, devolvemos los valores iniciales
            if not perfil:
                return {"nivel": 1, "xp_total": 0, "racha_actual": 0, "mejor_racha": 0}  
            return perfil
        except Exception as e:
            print(f"Error obteniendo datos de gamificacion: {e}")
            return {"nivel": 1, "xp_total": 0, "racha_actual": 0, "mejor_racha": 0}



    def registrar_habito_gamificado(self, id_habito, completado=True, comentario=""):
        try:
            self.cursor.execute("""
                INSERT INTO registros_habitos (id_habito, fecha, completado, comentario)
                VALUES (%s, CURRENT_DATE, %s, %s)
                RETURNING id_registro
            """, (id_habito, completado, comentario))
            
            registro = self.cursor.fetchone()
            self.conn.commit()
            
            return {"exito": True, "registro": registro}
            
        except Exception as e:
            self.conn.rollback()
            print(f"Error insertando registro: {e}")
            return {"exito": False, "mensaje": str(e)}



    def cerrar_conexion(self):
        self.cursor.close()
        self.conn.close()
        print("Conexion de extension cerrada")



if __name__ == "__main__":
    db = DatabaseExtension()
    db.cerrar_conexion()