--Vista para que el motor de IA evalue el riesgo de abandono
CREATE OR REPLACE VIEW v_analisis_riesgo_ia AS
SELECT
    h.id_usuario,
    h.id_habito,
    h.nombre AS habito,
    h.frecuencia,
    COUNT(r.id_registro) AS total_registros,
    COUNT(r.id_registro) FILTER (WHERE r.completado = FALSE) AS dias_fallados,
    MAX(r.fecha) AS ultimo_registro,
    CASE
        WHEN CURRENT_DATE - MAX(r.fecha) > 3 THEN 'Riesgo Alto'
        WHEN COUNT(r.id_registro) FILTER (WHERE r.completado = FALSE) >= 2 THEN 'Riesgo Medio'
        ELSE 'Estable'
    END AS nivel_riesgo
FROM habitos h
LEFT JOIN registros_habitos r ON h.id_habito = r.id_habito
GROUP BY h.id_usuario, h.id_habito, h.nombre, h.frecuencia;