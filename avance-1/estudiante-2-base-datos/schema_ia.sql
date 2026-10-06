--Tabla de preferencias del asistente para cada usuario
CREATE TABLE IF NOT EXISTS preferencias_ia(
    id_preferencia SERIAL PRIMARY KEY,
    id_usuario INT NOT NULL UNIQUE,
    rango_horario_optimo VARCHAR(100),
    CONSTRAINT fk_preferencias_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
);

--Tabla de historial de recomendaciones y alertas IA
CREATE TABLE IF NOT EXISTS recomendaciones_ia(
    id_recomendacion SERIAL PRIMARY KEY,
    id_usuario INT NOT NULL,
    id_habito INT,
    tipo_alerta VARCHAR(50) NOT NULL,
    mensaje_sugerido TEXT NOT NULL,
    fecha_generacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    aplicada BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_recomendaciones_usuario FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    CONSTRAINT fk_recomendaciones_habito FOREIGN KEY (id_habito) REFERENCES habito(id_habito) ON DELETE CASCADE
);

--Modificar la tabla actual de recordatorios para hacerlos "inteligentes"
ALTER TABLE recordatorios
ADD COLUMN IF NOT EXISTS es_inteligente BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS id_recomendacion INT NULL,
ADD CONSTRAINT fk_recordatorio_recomendacion FOREIGN KEY (id_recomendacion) REFERENCES recomendaciones_ia(id_recomendacion) ON DELETE SET NULL;