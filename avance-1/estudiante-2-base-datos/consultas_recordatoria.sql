CREATE OR REPLACE FUNCTION sp_obtener_recordatorio_activos(
    p_id_usuario INT,
    p_dia_actual VARCHAR
)

RETURNS TABLE(
    id_recordatorio INT,
    nombre_habito VARCHAR,
    hora TIME WITHOUT TIME ZONE,
    mensaje_notificacion TEXT,
    es_inteligente BOOLEAN,
    tono_usado VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.id_recordatorio,
        h.nombre AS nombre_habito,
        r.hora,
        COALESCE(ria.mensaje_sugerido, r.mensaje) AS mensaje_notificacion,
        r.es_inteligente,
        pia.tono_asistente AS tono_usado
    FROM recordatorios r
    JOIN habitos h ON r.id_habito = h.id_habito
    JOIN usuarios u ON h.id_usuario = u.id_usuario
    LEFT JOIN recomendaciones_ia ria ON r.id_recomendacion = ria.id_recomendacion
    LEFT JOIN preferencias_ia pia ON u.id_usuario = pia.id_usuario
    WHERE
        u.id_usuario = p_id_usuario
        AND r.activo = TRUE
        AND r.dias_semana ILIKE '%' || p_dia_actual || '%'
    ORDER BY r.hora ASC;
END;
$$ LANGUAGE plpgsql;



--Probar los recordatorios del usuario 1 para un día Lunes
SELECT * FROM sp_obtener_recordatorios_activos(1, 'Lunes'::VARCHAR);

