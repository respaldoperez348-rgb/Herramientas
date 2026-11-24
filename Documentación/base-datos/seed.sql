-- Esquema base HabitPulse
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    nombre_usuario VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    contrasena VARCHAR(255) NOT NULL,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
);

CREATE TABLE IF NOT EXISTS sesiones (
    id SERIAL PRIMARY KEY,
    habito_id INTEGER NOT NULL REFERENCES habitos(id) ON DELETE CASCADE,
    fecha DATE NOT NULL DEFAULT CURRENT_DATE,
    hora_inicio TIMESTAMP,
    hora_fin TIMESTAMP,
    duracion_segundos INTEGER NOT NULL,
    completada BOOLEAN DEFAULT TRUE,
    notas TEXT
);

CREATE TABLE IF NOT EXISTS recordatorios (
    id SERIAL PRIMARY KEY,
    habito_id INTEGER NOT NULL REFERENCES habitos(id) ON DELETE CASCADE,
    activo BOOLEAN DEFAULT FALSE,
    hora_inicio TIME,
    hora_fin TIME,
    hora VARCHAR(10),
    dias_semana VARCHAR(100) DEFAULT 'Lun, Mar, Mié, Jue, Vie, Sáb, Dom',
    mensaje TEXT DEFAULT ''
);

CREATE TABLE IF NOT EXISTS metas (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id) ON DELETE CASCADE,
    habito_id INTEGER REFERENCES habitos(id) ON DELETE SET NULL,
    titulo VARCHAR(150) NOT NULL,
    progreso_porcentaje NUMERIC(5,2) DEFAULT 0.0,
    fecha_limite DATE,
    estado VARCHAR(30) DEFAULT 'En progreso',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 1. Usuario demo (contraseña: secret)
INSERT INTO usuarios (nombre_usuario, email, contrasena)
VALUES ('demo', 'demo@habitpulse.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW')
ON CONFLICT (email) DO NOTHING;

-- 2. 4 hábitos en distintas categorías
INSERT INTO habitos (usuario_id, nombre, descripcion, objetivo_diario_minutos, categoria, icono, color)
VALUES
    (1, 'Beber 2L de agua', 'Hidratación constante durante el día', 15, 'Salud', 'dumbbell', '#10b981'),
    (1, 'Lectura técnica 30 min', 'Estudio de arquitectura y desarrollo', 30, 'Aprendizaje', 'book-open', '#3b82f6'),
    (1, 'Planificación diaria', 'Definir las 3 prioridades del día', 15, 'Productividad', 'trending-up', '#f59e0b'),
    (1, 'Meditación guiada', 'Respiración consciente antes de dormir', 10, 'Bienestar', 'leaf', '#06b6d4');

-- 3. Registros históricos de la última semana
INSERT INTO sesiones (habito_id, fecha, duracion_segundos, completada, notas)
VALUES
    (1, CURRENT_DATE - INTERVAL '6 days', 900, TRUE, 'Meta cumplida'),
    (1, CURRENT_DATE - INTERVAL '4 days', 900, TRUE, 'Meta cumplida'),
    (1, CURRENT_DATE - INTERVAL '2 days', 900, TRUE, 'Meta cumplida'),
    (1, CURRENT_DATE - INTERVAL '1 day', 900, TRUE, 'Meta cumplida'),
    (1, CURRENT_DATE, 900, TRUE, 'Hoy completado'),
    (2, CURRENT_DATE - INTERVAL '5 days', 1800, TRUE, 'Capítulo 1'),
    (2, CURRENT_DATE - INTERVAL '2 days', 1800, TRUE, 'Capítulo 2'),
    (3, CURRENT_DATE - INTERVAL '3 days', 900, TRUE, 'Tareas organizadas'),
    (3, CURRENT_DATE, 900, TRUE, 'Agenda lista'),
    (4, CURRENT_DATE - INTERVAL '1 day', 600, TRUE, 'Sesión nocturna');