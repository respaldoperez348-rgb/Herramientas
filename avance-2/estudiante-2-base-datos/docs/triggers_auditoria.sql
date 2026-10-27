-- MODULO: INTEGRACIÓN Y PRUEBAS
--Sistema de Auditoría y Triggers

-- 1. Crear tabla para guardar el registro de movimientos sospechosos o modificaciones
CREATE TABLE IF NOT EXISTS auditoria_sistema (
    id_auditoria SERIAL PRIMARY KEY,
    tabla_afectada VARCHAR(50),
    accion VARCHAR(20), -- 'UPDATE' o 'DELETE'
    fecha_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    detalle TEXT
);

-- 2. Crear la función que ejecutará el Trigger
CREATE OR REPLACE FUNCTION fn_auditar_cambios_habitos()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO auditoria_sistema(tabla_afectada, accion, detalle)
        VALUES ('habitos', 'DELETE', 'Se eliminó el hábito ID: ' || OLD.id_habito || ' - ' || OLD.nombre);
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO auditoria_sistema(tabla_afectada, accion, detalle)
        VALUES ('habitos', 'UPDATE', 'Se modificó el hábito ID: ' || NEW.id_habito || ' (Antes: ' || OLD.nombre || ')');
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- 3. Enlazar el Trigger a la tabla de hábitos
-- (Borramos primero por si ya existía de una prueba anterior)
DROP TRIGGER IF EXISTS trg_auditar_habitos ON habitos;

CREATE TRIGGER trg_auditar_habitos
AFTER UPDATE OR DELETE ON habitos
FOR EACH ROW EXECUTE FUNCTION fn_auditar_cambios_habitos();