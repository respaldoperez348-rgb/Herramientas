TRUNCATE TABLE recordatorios, metas, registros_habitos, habitos, usuarios RESTART IDENTITY CASCADE;

--Usuarios simulados
INSERT INTO usuarios (nombre, correo, contrasena) VALUES
('Carlos Mendoza', 'carlos.mendoza@email.com', '$2b$12$e8Y...hashSimulado1'),
('Lucia Torres', 'lucia.torres@email.com', '$2b$12$k9P...hashSimulado2');

--Habitos definidos
INSERT INTO habitos (id_usuario, nombre, categoria, frecuencia) VALUES
(1, 'Beber 2L de agua', 'Salud', 'Diaria'),
(1, 'Lectura tecnica 30 min', 'Estudio', 'Diaria'),
(1, 'Rutina de pesas', 'Deporte', 'Lunes a Viernes'),
(2, 'Meditacion guiada', 'Bienestar', 'Diaria'),
(2, 'Repasar ingles', 'Estudio', 'Lunes a Sabado');

INSERT INTO registros_habitos (id_habito, fecha, completado, comentario) VALUES
--Carlos:Racha positiva en agua
(1, CURRENT_DATE - INTERVAL '3 days', TRUE, 'Completado sin problema'),
(1, CURRENT_DATE - INTERVAL '2 days', TRUE, 'Botella termica recargada 3 veces'),
(1, CURRENT_DATE - INTERVAL '1 day', TRUE, 'Meta lograda por la tarde'),
(1, CURRENT_DATE, TRUE, 'Objetivo diario cumplido'),

--Carlos:Cumplimiento irregular en lectura
(2, CURRENT_DATE - INTERVAL '2 days', TRUE, 'Capitulo 4 terminado'),
(2, CURRENT_DATE - INTERVAL '1 day', FALSE, 'Cansancio por clases'),
(2, CURRENT_DATE, TRUE, 'Retomado con 20 minutos'),

--Lucia:Registros de bienestar
(4, CURRENT_DATE - INTERVAL '1 day', TRUE, 'Sesion de 10 minutos en la manana'),
(4, CURRENT_DATE, FALSE, 'Sin tiempo por entregas');

--Metas con porcentajes calculados
INSERT INTO metas (id_usuario, id_habito, titulo, progreso_porcentaje, fecha_limite, estado) VALUES
(1, 1, 'Racha perfecta de hidratacion mensual', 40.00, CURRENT_DATE + INTERVAL '18 days', 'En progreso'),
(1, 2, 'Finalizar libro de arquitectura de software', 65.00, CURRENT_DATE + INTERVAL '10 days', 'En progreso'),
(2, 5, 'Completar modulo B2 de vocabulario', 20.00, CURRENT_DATE + INTERVAL '25 days', 'En progreso');

--Recordatorios activos
INSERT INTO recordatorios (id_habito, hora, dias_semana, activo, mensaje) VALUES
(1, '08:30:00', 'Lunes, Martes, Miercoles, Jueves, Viernes', TRUE, 'Hora de tu primer vaso con agua del dia'),
(2, '21:00:00', 'Lunes a Domingo', TRUE, 'Toma tu libro y apaga las pantallas'),
(4, '07:00:00', 'Lunes a Domingo', TRUE, 'Inicia el dia con 10 min de respiracion');