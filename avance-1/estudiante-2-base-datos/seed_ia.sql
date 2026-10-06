--Insertar preferencias simuladas
INSERT INTO preferencias_ia (id_usuario, rango_horario_optimo)
VALUES 
(1, '06:00-08:00'),
(2, '19:00-22:00');

--Insertar recomendación generada (simulando que la IA ya actuó)
INSERT INTO recomendaciones_ia (id_usuario, id_habito, tipo_alerta, mensaje_sugerido)
VALUES 
(1, 2, 'Riesgo abandono', 'He notado que tus lecturas han disminuido. ¿Qué tal si hoy bajamos la meta a solo 10 minutos para no perder el hábito?');

--Insertar un recordatorio inteligente basado en la recomendación anterior
INSERT INTO recordatorios (id_habito, hora, dias_semana, activo, mensaje, es_inteligente, id_recomendacion)
VALUES 
(2, '20:00:00', 'Lunes a Domingo', TRUE, 'Lectura ligera de 10 min', TRUE, 1);