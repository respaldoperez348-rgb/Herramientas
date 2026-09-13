CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS habitos (
    id_habito SERIAL PRIMARY KEY,
    id_usuario INT NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    frecuencia VARCHAR(30) NOT NULL,
    CONSTRAINT fk_habitos_usuario FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS registros_habitos (
    id_registro SERIAL PRIMARY KEY,
    id_habito INT NOT NULL,
    fecha DATE NOT NULL,
    completado BOOLEAN DEFAULT FALSE,
    comentario VARCHAR(255),
    CONSTRAINT fk_registros_habitos FOREIGN KEY (id_habito) REFERENCES habitos (id_habito) ON DELETE CASCADE, 
    CONSTRAINT uq_habito_fecha UNIQUE (id_habito, fecha)
);