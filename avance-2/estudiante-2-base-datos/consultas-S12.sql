--Solo los registros que sí se lograron
SELECT * FROM public.registros_habitos
WHERE completado = true
ORDER BY fecha DESC;

--Para contar el total de días completados y no completados por cada hábito
SELECT id_habito, completado, COUNT(*) as total_dias
FROM public.registros_habitos
GROUP BY id_habito, completado
ORDER BY id_habito ASC, completado DESC;

--Para calcular el porcentaje de éxito de un hábito en específico
SELECT 
    id_habito,
    COUNT(CASE WHEN completado = true THEN 1 END) * 100.0 / COUNT(*) AS porcentaje_exito
FROM public.registros_habitos
WHERE id_habito = 4
GROUP BY id_habito;