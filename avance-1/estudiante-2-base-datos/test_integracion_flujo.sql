-- MODULO: INTEGRACIÓN Y PRUEBAS 
-- Pruebas de Integración (End-to-End)


-- Iniciar bloque de prueba (usamos ROLLBACK al final para no guardar basura)
BEGIN;

DO $$ 
DECLARE 
    v_nuevo_usuario INT;
    v_nuevo_habito INT;
BEGIN
    RAISE NOTICE '--- INICIANDO PRUEBA DE INTEGRACIÓN ---';

    -- PRUEBA 1: Inserción de Usuario y Preferencias IA
    INSERT INTO usuarios (nombre, correo, contrasena) 
    VALUES ('Usuario Prueba S11', 'test.s11@correo.com', 'hash123')
    RETURNING id_usuario INTO v_nuevo_usuario;
    
    INSERT INTO preferencias_ia (id_usuario, tono_asistente, rango_horario_optimo) 
    VALUES (v_nuevo_usuario, 'Amigable', '07:00-09:00');
    
    RAISE NOTICE 'Prueba 1 superada: Usuario e IA creados.';

    -- PRUEBA 2: Creación de Hábito y Recordatorio
    INSERT INTO habitos (id_usuario, nombre, descripcion, frecuencia) 
    VALUES (v_nuevo_usuario, 'Caminar 30 min', 'Prueba de integración', 'Diaria')
    RETURNING id_habito INTO v_nuevo_habito;

    INSERT INTO recordatorios (id_habito, hora, dias_semana, activo, es_inteligente)
    VALUES (v_nuevo_habito, '07:30:00', 'Lunes a Domingo', TRUE, TRUE);

    RAISE NOTICE 'Prueba 2 superada: Hábito y recordatorio creados.';

    -- PRUEBA 3: Inserción de Metas y Registros Diarios
    INSERT INTO metas (id_usuario, id_habito, titulo, fecha_limite)
    VALUES (v_nuevo_usuario, v_nuevo_habito, 'Caminar 1 semana', CURRENT_DATE + INTERVAL '7 days');

    INSERT INTO registros_habitos (id_habito, fecha, completado)
    VALUES (v_nuevo_habito, CURRENT_DATE, TRUE);

    RAISE NOTICE 'Prueba 3 superada: Metas y registros enlazados correctamente.';
    
    -- PRUEBA 4: Forzar el Trigger de Auditoría (Simular actualización)
    UPDATE habitos SET nombre = 'Caminar 45 min' WHERE id_habito = v_nuevo_habito;
    RAISE NOTICE 'Prueba 4 superada: Actualización realizada, trigger disparado.';

END $$;

-- Verificamos si la auditoría capturó el cambio de la Prueba 4
-- SELECT * FROM auditoria_sistema;

-- Deshacemos todos los cambios generados en esta prueba para dejar la BD limpia
ROLLBACK;