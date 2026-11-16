--SEMANA 12: MOTOR DE GAMIFICACIÓN Y RACHAS

--Tabla para el perfil de juego del usuario (Niveles y XP)
CREATE TABLE IF NOT EXISTS perfil_gamificacion (
    id_usuario INT PRIMARY KEY REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
    nivel INT DEFAULT 1,
    xp_total INT DEFAULT 0,
    racha_actual INT DEFAULT 0,
    mejor_racha INT DEFAULT 0,
    ultima_actividad DATE
);

INSERT INTO perfil_gamificacion (id_usuario)
SELECT id_usuario FROM usuarios
ON CONFLICT DO NOTHING;

--Función automática para calcular experiencia y niveles
CREATE OR REPLACE FUNCTION fn_otorgar_experiencia()
RETURNS TRIGGER AS $$
DECLARE
    v_xp_ganada INT := 50; --Puntos que gana el usuario por cumplir su hábito
    v_id_usuario INT;
BEGIN
    --Obtenemos a qué usuario le pertenece este hábito
    SELECT id_usuario INTO v_id_usuario 
    FROM habitos WHERE id_habito = NEW.id_habito;

    --Si el registro entra como 'Completado' o equivalente
    IF NEW.estado = 'Completado' THEN
        
        --Actualizamos sus puntos y racha
        UPDATE perfil_gamificacion
        SET 
            xp_total = xp_total + v_xp_ganada,
            --Fórmula automática de nivel: Sube 1 nivel por cada 500 XP
            nivel = 1 + ((xp_total + v_xp_ganada) / 500),
            racha_actual = racha_actual + 1,
            ultima_actividad = CURRENT_DATE
        WHERE id_usuario = v_id_usuario;
        
        --Verificamos si rompió su propio récord (Mejor Racha)
        UPDATE perfil_gamificacion
        SET mejor_racha = racha_actual
        WHERE id_usuario = v_id_usuario AND racha_actual > mejor_racha;
        
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

--El Trigger que vigila la tabla de registros diarios
DROP TRIGGER IF EXISTS trg_gamificacion_activa ON registros_habitos;
CREATE TRIGGER trg_gamificacion_activa
AFTER INSERT OR UPDATE ON registros_habitos
FOR EACH ROW
EXECUTE FUNCTION fn_otorgar_experiencia();