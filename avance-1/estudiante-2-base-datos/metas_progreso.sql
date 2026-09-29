--Vista para calcular dias completados y estado dinamico
CREATE OR REPLACE VIEW v_porgreso_metas AS
SELECT
    m.id_meta,
    m.id_usuario,
    u.nombre AS nombre_usuario,
    m.id_habito,
    h.nombre AS nombre_habito,
    m.titulo AS meta_titulo,
    m.fecha_limite,
    COUNT(r.id_registro) FILTER (WHERE r.completado = TRUE) AS dias_completados, m.progreso_porcentaje,
    CASE
        WHEN m.progreso_porcentaje >= 100.00 THEN 'Completada'
        WHEN m.fecha_limite < CURRENT_DATE AND m.progreso_porcentaje < 100.00 THEN 'Expirada'
        ELSE 'En progreso'
    END AS estado_calculado
FROM meta m
JOIN usuarios u ON m.id_usuario = u.id_usuario
LEFT JOIN habitos h ON m.id_habito = h.id_habito
LEFT JOIN registros_habitos r ON h.id_habito = r.id_habito
GROUP BY m.id_meta, m.id_usuario, u.nombre, m.id_habito, h.nombre, m.titulo, m.fecha_limite, m.progreso_porcentaje;


--Funcion para actualizar el porcentaje de una meta especifica
--Recibe: id_meta y objetivo_dias (dias planeados para cumplir la meta)
CREATE OR REPLACE FUNCTION sp_actualizar_proceso_meta(
    p_id_meta INT,
    p_objetivo_dias INT
)
RETURN NUMERIC AS $$
DECLARE
    v_dias_hechos INT;
    v_nuevo_porcentaje NUMERIC(5,2);
    v_nuevo_estado VARCHAR(20);
BEGIN

    --Contar registros completados asociados al habito de la meta
    SELECT COUNT(r.id_registro)
    INTO v_dias_hechos
    FROM metas m
    JOIN habitos h ON m.id_habito = h.id_habito
    LEFT JOIN registros_habitos r ON h.id_habito = r.id_habito AND r.completado = TRUE
    WHERE m.id_meta = p_id_meta;

    --Calcular porcentaje evitando division entre cero
    IF p_objetivo_dias > 0 THEN
        v_nuevo_porcentaje := LEAST(ROUNT((v_dias_hechos::NUMERIC / p.objetivo_dias::NUMERIC)* 100, 2), 100.00);
    ELSE
        v_nuevo_porcentaje := 0.00;
    END IF;

    --Determinar estado
    IF v_nuevo_porcentaje >= 100.00 THEN
        v_nuevo_estado := 'Completado';
    ELSE
        v_nuevo_estado := 'En progreso';
    END IF;

    --Actualizar la tabla metas
    UPDATE metas
    SET progreso_porcentaje = v_nuevo_porcentaje,
        estado = v_nuevo_estado
    WHERE id_meta = p_id_meta;

    RETURN v_nuevo_porcentaje;
END;
$$ LENGUAGE plpgsql;

