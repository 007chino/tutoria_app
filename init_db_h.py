# init_db_h.py
from database_connection_h import get_connection

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.executescript(
        """
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS semester (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS week (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          semester_id INTEGER NOT NULL REFERENCES semester(id) ON DELETE CASCADE,
          week_number INTEGER NOT NULL,
          title TEXT NOT NULL,
          subtitle TEXT,
          UNIQUE(semester_id, week_number)
        );

        CREATE TABLE IF NOT EXISTS tutor (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          name TEXT NOT NULL,
          email TEXT NOT NULL UNIQUE,
          capacity INTEGER NOT NULL,
          assigned INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS student (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          code TEXT NOT NULL UNIQUE,
          name TEXT NOT NULL,
          status TEXT NOT NULL DEFAULT 'OK',
          tutor_id INTEGER REFERENCES tutor(id)
        );

        CREATE TABLE IF NOT EXISTS report_log (
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          date TEXT NOT NULL,
          type TEXT NOT NULL,
          user TEXT NOT NULL,
          file TEXT
        );
        """
    )

    # -------- Seed básico (si está vacío) --------
    if cur.execute("SELECT COUNT(*) c FROM semester").fetchone()[0] == 0:
        cur.executemany("INSERT INTO semester(name) VALUES (?)",
                        [('2025-II',), ('2025-I',), ('2024-II',), ('2024-I',)])
        sem_id = cur.execute("SELECT id FROM semester WHERE name='2025-II'").fetchone()[0]

        cur.executemany(
            "INSERT INTO week(semester_id,week_number,title,subtitle) VALUES (?,?,?,?)",
            [
                (sem_id, 1, "Semana 1: Registro y bienvenida",
                 "Charlas iniciales, alta de estudiantes y verificación de horarios."),
                (sem_id, 2, "Semana 2: Tutorías iniciales",
                 "Asignación de tutor y metas del primer mes."),
                (sem_id, 3, "Semana 3: Seguimiento académico",
                 "Checkpoints, incidencias y plan remedial.")
            ],
        )

        cur.executemany(
            "INSERT INTO tutor(name,email,capacity,assigned) VALUES (?,?,?,?)",
            [
                ("María Quispe", "m.quispe@unsaac.edu", 10, 8),
                ("Jorge Ramos", "j.ramos@unsaac.edu", 12, 6),
                ("Lucía Huamán", "l.huaman@unsaac.edu", 8, 8),
            ],
        )

        cur.executemany(
            "INSERT INTO student(code,name,status,tutor_id) VALUES (?,?,?,?)",
            [
                ("20251234", "Ana Paredes", "OK", 1),
                ("20254567", "Diego Lazo", "Pendiente", None),
                ("20257890", "Nadia Choque", "Alerta", 2),
            ],
        )

        cur.execute(
            "INSERT INTO report_log(date,type,user) VALUES (?,?,?)",
            ("2025-10-01", "semanal", "admin@unsaac.edu"),
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("✅ Base de datos iniciada y con datos de ejemplo.")
