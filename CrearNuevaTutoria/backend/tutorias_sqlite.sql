
-- ===============================================
-- Tutorías UNSAAC - Esquema SQLite (portable)
-- Compatible con: SQLite 3.35+
-- Crea tablas, índices, triggers anti-choque y datos de ejemplo
-- ===============================================

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 3000;

-- -------------------------
-- Limpieza opcional (reanudar sin error)
-- -------------------------
DROP TRIGGER IF EXISTS trg_sessions_no_overlap_tutor_ins;
DROP TRIGGER IF EXISTS trg_sessions_no_overlap_tutor_upd;
DROP TRIGGER IF EXISTS trg_sessions_no_overlap_room_ins;
DROP TRIGGER IF EXISTS trg_sessions_no_overlap_room_upd;

DROP VIEW IF EXISTS v_sessions;

DROP TABLE IF EXISTS sessions;
DROP TABLE IF EXISTS rooms;
DROP TABLE IF EXISTS tutors;
DROP TABLE IF EXISTS careers;

-- -------------------------
-- Catálogos
-- -------------------------
CREATE TABLE careers (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  name      TEXT NOT NULL UNIQUE
);

CREATE TABLE tutors (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  full_name   TEXT NOT NULL,
  career_id   INTEGER NOT NULL,
  is_active   INTEGER NOT NULL DEFAULT 1,
  created_at  TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(full_name),
  FOREIGN KEY (career_id) REFERENCES careers(id) ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE TABLE rooms (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  name        TEXT NOT NULL UNIQUE,
  location    TEXT,
  capacity    INTEGER,
  created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- -------------------------
-- Sesiones / Tutorías
-- -------------------------
CREATE TABLE sessions (
  id           INTEGER PRIMARY KEY AUTOINCREMENT,
  tutor_id     INTEGER NOT NULL,
  room_id      INTEGER NOT NULL,
  date         TEXT    NOT NULL,              -- formato 'YYYY-MM-DD'
  start_time   TEXT    NOT NULL,              -- formato 'HH:MM' 24h
  end_time     TEXT    NOT NULL,              -- formato 'HH:MM' 24h
  notes        TEXT,
  created_at   TEXT    NOT NULL DEFAULT (datetime('now')),
  updated_at   TEXT    NOT NULL DEFAULT (datetime('now')),

  -- Validaciones básicas
  CHECK (length(date) = 10 AND substr(date,5,1)='-' AND substr(date,8,1)='-'),
  CHECK (start_time GLOB '[0-2][0-9]:[0-5][0-9]' AND end_time GLOB '[0-2][0-9]:[0-5][0-9]'),
  CHECK (start_time >= '07:00' AND end_time <= '21:00'),    -- Ventana 07:00–21:00
  CHECK (end_time > start_time),                            -- Debe terminar después de iniciar
  CHECK (substr(start_time,4,2) IN ('00','30') AND substr(end_time,4,2) IN ('00','30')), -- pasos de 30 mins

  FOREIGN KEY (tutor_id) REFERENCES tutors(id) ON UPDATE CASCADE ON DELETE RESTRICT,
  FOREIGN KEY (room_id)  REFERENCES rooms(id)  ON UPDATE CASCADE ON DELETE RESTRICT
);

-- Índices para acelerar consultas frecuentes
CREATE INDEX idx_tutors_name ON tutors(full_name);
CREATE INDEX idx_sessions_by_day_tutor ON sessions(date, tutor_id);
CREATE INDEX idx_sessions_by_day_room  ON sessions(date, room_id);

-- Actualiza updated_at en cambios
CREATE TRIGGER IF NOT EXISTS trg_sessions_touch_updated_at
AFTER UPDATE ON sessions
FOR EACH ROW
BEGIN
  UPDATE sessions SET updated_at = datetime('now') WHERE id = NEW.id;
END;

-- -------------------------
-- Triggers anti-solapamiento (overlap)
-- Nota: con tiempos 'HH:MM' las comparaciones lexicográficas funcionan.
-- Overlap si: NOT (A.end <= B.start OR B.end <= A.start)
-- -------------------------

-- Por tutor en el mismo día (INSERT)
CREATE TRIGGER trg_sessions_no_overlap_tutor_ins
BEFORE INSERT ON sessions
FOR EACH ROW
BEGIN
  SELECT CASE WHEN EXISTS (
    SELECT 1
    FROM sessions s
    WHERE s.tutor_id = NEW.tutor_id
      AND s.date = NEW.date
      AND NOT (s.end_time <= NEW.start_time OR NEW.end_time <= s.start_time)
  ) THEN RAISE(ABORT, 'Conflicto: el tutor ya tiene una sesión en ese horario.') END;
END;

-- Por tutor en el mismo día (UPDATE)
CREATE TRIGGER trg_sessions_no_overlap_tutor_upd
BEFORE UPDATE ON sessions
FOR EACH ROW
BEGIN
  SELECT CASE WHEN EXISTS (
    SELECT 1
    FROM sessions s
    WHERE s.tutor_id = NEW.tutor_id
      AND s.date = NEW.date
      AND s.id <> NEW.id
      AND NOT (s.end_time <= NEW.start_time OR NEW.end_time <= s.start_time)
  ) THEN RAISE(ABORT, 'Conflicto: el tutor ya tiene una sesión en ese horario.') END;
END;

-- Por ambiente/sala en el mismo día (INSERT)
CREATE TRIGGER trg_sessions_no_overlap_room_ins
BEFORE INSERT ON sessions
FOR EACH ROW
BEGIN
  SELECT CASE WHEN EXISTS (
    SELECT 1
    FROM sessions s
    WHERE s.room_id = NEW.room_id
      AND s.date = NEW.date
      AND NOT (s.end_time <= NEW.start_time OR NEW.end_time <= s.start_time)
  ) THEN RAISE(ABORT, 'Conflicto: el ambiente ya está ocupado en ese horario.') END;
END;

-- Por ambiente/sala en el mismo día (UPDATE)
CREATE TRIGGER trg_sessions_no_overlap_room_upd
BEFORE UPDATE ON sessions
FOR EACH ROW
BEGIN
  SELECT CASE WHEN EXISTS (
    SELECT 1
    FROM sessions s
    WHERE s.room_id = NEW.room_id
      AND s.date = NEW.date
      AND s.id <> NEW.id
      AND NOT (s.end_time <= NEW.start_time OR NEW.end_time <= s.start_time)
  ) THEN RAISE(ABORT, 'Conflicto: el ambiente ya está ocupado en ese horario.') END;
END;

-- -------------------------
-- Vista conveniente
-- -------------------------
CREATE VIEW v_sessions AS
SELECT
  s.id,
  s.date,
  s.start_time,
  s.end_time,
  t.full_name       AS tutor,
  c.name            AS carrera,
  r.name            AS ambiente,
  s.notes,
  s.created_at,
  s.updated_at
FROM sessions s
JOIN tutors t   ON t.id = s.tutor_id
JOIN careers c  ON c.id = t.career_id
JOIN rooms r    ON r.id = s.room_id;

-- -------------------------
-- Datos de ejemplo
-- -------------------------
INSERT INTO careers(name) VALUES
  ('Ing. Informática'),
  ('Ing. Industrial'),
  ('Ing. Civil');

INSERT INTO tutors(full_name, career_id) VALUES
  ('Luis Angel Mogrovejo Ccorimanya', (SELECT id FROM careers WHERE name='Ing. Informática')),
  ('Chino',                            (SELECT id FROM careers WHERE name='Ing. Informática')),
  ('Fulanita',                         (SELECT id FROM careers WHERE name='Ing. Industrial')),
  ('Menganito',                        (SELECT id FROM careers WHERE name='Ing. Civil')),
  ('María Pérez',                      (SELECT id FROM careers WHERE name='Ing. Informática')),
  ('Jorge Quispe',                     (SELECT id FROM careers WHERE name='Ing. Industrial')),
  ('Ana Huamán',                       (SELECT id FROM careers WHERE name='Ing. Civil'));

INSERT INTO rooms(name, location, capacity) VALUES
  ('Aula 201',   'Pabellón A', 35),
  ('Lab Redes',  'Subsuelo B', 24),
  ('Aula 105',   'Pabellón A', 30);

-- Sesiones ejemplo (usa fechas relativas)
INSERT INTO sessions(tutor_id, room_id, date, start_time, end_time, notes) VALUES
  ((SELECT id FROM tutors WHERE full_name='Luis Angel Mogrovejo Ccorimanya'),
   (SELECT id FROM rooms  WHERE name='Aula 201'),
   DATE('now','-2 day'), '10:00','11:00',''),
  ((SELECT id FROM tutors WHERE full_name='Fulanita'),
   (SELECT id FROM rooms  WHERE name='Aula 201'),
   DATE('now'), '09:30','10:30',''),
  ((SELECT id FROM tutors WHERE full_name='Menganito'),
   (SELECT id FROM rooms  WHERE name='Lab Redes'),
   DATE('now'), '13:00','14:00',''),
  ((SELECT id FROM tutors WHERE full_name='Chino'),
   (SELECT id FROM rooms  WHERE name='Aula 105'),
   DATE('now','+1 day'), '16:00','17:00','');

-- -------------------------
-- Consultas de ejemplo
-- -------------------------
-- -- Todas las sesiones ordenadas
-- SELECT * FROM v_sessions ORDER BY date, start_time;
-- -- Por fecha específica
-- SELECT * FROM v_sessions WHERE date = DATE('now') ORDER BY start_time;
-- -- De un tutor
-- SELECT * FROM v_sessions WHERE tutor = 'Chino' ORDER BY date, start_time;
-- -- Intentar insertar choque (debe fallar):
-- -- INSERT INTO sessions(tutor_id, room_id, date, start_time, end_time)
-- -- VALUES (1, 1, DATE('now'), '09:45','10:15');
