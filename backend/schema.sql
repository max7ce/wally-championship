-- WALLY CHAMPIONSHIP DATABASE SCHEMA
-- PostgreSQL Schema para Campeonato de Wally
-- 8 equipos, 3 canchas, 2 días

-- ============================================
-- EQUIPOS
-- ============================================
CREATE TABLE equipos (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  posicion INT, -- Posición en sorteo (1-8)
  created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- SLOTS DE TIEMPO (pre-generados)
-- ============================================
CREATE TABLE slots_tiempo (
  id SERIAL PRIMARY KEY,
  dia INT NOT NULL CHECK (dia IN (1, 2)),
  numero_slot INT NOT NULL, -- 1-14 slots por día
  hora_inicio TIME NOT NULL,
  cancha INT NOT NULL CHECK (cancha IN (1, 2, 3)),
  UNIQUE(dia, numero_slot, cancha)
);

-- ============================================
-- PARTIDOS (fixture)
-- ============================================
CREATE TABLE partidos (
  id SERIAL PRIMARY KEY,
  slot_id INT REFERENCES slots_tiempo(id),
  equipo_local_id INT REFERENCES equipos(id),
  equipo_visitante_id INT REFERENCES equipos(id),
  ronda INT CHECK (ronda IN (1, 2, 3)),
  created_at TIMESTAMP DEFAULT NOW(),
  CONSTRAINT no_same_team CHECK (equipo_local_id != equipo_visitante_id)
);

-- ============================================
-- RESULTADOS
-- ============================================
CREATE TABLE resultados (
  id SERIAL PRIMARY KEY,
  partido_id INT REFERENCES partidos(id) UNIQUE,
  puntos_local INT DEFAULT 0 CHECK (puntos_local >= 0),
  puntos_visitante INT DEFAULT 0 CHECK (puntos_visitante >= 0),
  punto_de_oro BOOLEAN DEFAULT FALSE,
  estado VARCHAR(20) DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'en_juego', 'finalizado')),
  terminado_por VARCHAR(20) CHECK (terminado_por IN ('puntos', 'tiempo', 'punto_oro')),
  tiempo_jugado INT, -- segundos jugados
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- USUARIOS/CANCHAS (autenticación simple)
-- ============================================
CREATE TABLE usuarios (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  tipo VARCHAR(20) NOT NULL CHECK (tipo IN ('cancha1', 'cancha2', 'cancha3', 'publico', 'admin')),
  created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- ÍNDICES para performance
-- ============================================
CREATE INDEX idx_partidos_slot ON partidos(slot_id);
CREATE INDEX idx_partidos_equipos ON partidos(equipo_local_id, equipo_visitante_id);
CREATE INDEX idx_resultados_partido ON resultados(partido_id);
CREATE INDEX idx_slots_dia_cancha ON slots_tiempo(dia, cancha);

-- ============================================
-- VISTA: Fixture completo con nombres
-- ============================================
CREATE VIEW v_fixture AS
SELECT 
  p.id as partido_id,
  st.dia,
  st.numero_slot,
  st.hora_inicio,
  st.cancha,
  e1.nombre as equipo_local,
  e2.nombre as equipo_visitante,
  p.ronda,
  COALESCE(r.estado, 'pendiente') as estado,
  r.puntos_local,
  r.puntos_visitante,
  r.punto_de_oro,
  r.terminado_por
FROM partidos p
JOIN slots_tiempo st ON p.slot_id = st.id
JOIN equipos e1 ON p.equipo_local_id = e1.id
JOIN equipos e2 ON p.equipo_visitante_id = e2.id
LEFT JOIN resultados r ON p.id = r.partido_id
ORDER BY st.dia, st.numero_slot, st.cancha;

-- ============================================
-- VISTA: Tabla de posiciones
-- ============================================
CREATE VIEW v_standings AS
WITH partidos_finalizados AS (
  SELECT 
    p.equipo_local_id as equipo_id,
    CASE 
      WHEN r.puntos_local > r.puntos_visitante THEN 3 -- Victoria
      WHEN r.puntos_local = r.puntos_visitante THEN 1 -- Empate (punto de oro no debería pasar)
      ELSE 0 -- Derrota
    END as puntos,
    CASE WHEN r.puntos_local > r.puntos_visitante THEN 1 ELSE 0 END as ganados,
    CASE WHEN r.puntos_local = r.puntos_visitante THEN 1 ELSE 0 END as empatados,
    CASE WHEN r.puntos_local < r.puntos_visitante THEN 1 ELSE 0 END as perdidos,
    r.puntos_local as puntos_favor,
    r.puntos_visitante as puntos_contra
  FROM partidos p
  JOIN resultados r ON p.id = r.partido_id
  WHERE r.estado = 'finalizado'
  
  UNION ALL
  
  SELECT 
    p.equipo_visitante_id as equipo_id,
    CASE 
      WHEN r.puntos_visitante > r.puntos_local THEN 3
      WHEN r.puntos_visitante = r.puntos_local THEN 1
      ELSE 0
    END as puntos,
    CASE WHEN r.puntos_visitante > r.puntos_local THEN 1 ELSE 0 END as ganados,
    CASE WHEN r.puntos_visitante = r.puntos_local THEN 1 ELSE 0 END as empatados,
    CASE WHEN r.puntos_visitante < r.puntos_local THEN 1 ELSE 0 END as perdidos,
    r.puntos_visitante as puntos_favor,
    r.puntos_local as puntos_contra
  FROM partidos p
  JOIN resultados r ON p.id = r.partido_id
  WHERE r.estado = 'finalizado'
)
SELECT 
  e.id,
  e.nombre,
  COALESCE(SUM(pf.puntos), 0) as puntos,
  COALESCE(SUM(pf.ganados), 0) as ganados,
  COALESCE(SUM(pf.empatados), 0) as empatados,
  COALESCE(SUM(pf.perdidos), 0) as perdidos,
  COALESCE(SUM(pf.ganados + pf.empatados + pf.perdidos), 0) as jugados,
  COALESCE(SUM(pf.puntos_favor), 0) as puntos_favor,
  COALESCE(SUM(pf.puntos_contra), 0) as puntos_contra,
  COALESCE(SUM(pf.puntos_favor), 0) - COALESCE(SUM(pf.puntos_contra), 0) as diferencia
FROM equipos e
LEFT JOIN partidos_finalizados pf ON e.id = pf.equipo_id
GROUP BY e.id, e.nombre
ORDER BY puntos DESC, diferencia DESC, puntos_favor DESC;
