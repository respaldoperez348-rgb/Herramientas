-- Datos de prueba para verificar funcionamiento
INSERT INTO usuarios (nombre, correo, contrasena) VALUES
('Juan Perez', 'juan.perez@example.com', 'hash_pass_123'),
('Maria Lopez', 'maria.lopez@example.com', 'hash_pass_456');

INSERT INTO habitos (id_usuario, nombre, categoria, frecuencia) VALUES
(1, 'Beber 2L de agua', 'Salud', 'Diaria'),
(1, 'Leer 20 minutos', 'Estudio', 'Diaria');

INSERT INTO registros_habitos (id_habito, fecha, completado, comentario) VALUES
(1, CURRENT_DATE, TRUE, 'Meta cumplida');

INSERT INTO metas (id_usuario, id_habito, titulo, progreso_porcentaje) VALUES
(1, 1, 'Racha 30 dias', 10.00);

INSERT INTO recordatorios (id_habito, hora, dias_semana, mensaje) VALUES
(1, '08:00:00', 'Lunes a Viernes', 'Recordatorio de agua');