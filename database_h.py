# database_h.py
from database_connection_h import get_connection

# =============== SEMESTRES ===============
def list_semesters():
    conn = get_connection()
    rows = conn.execute("SELECT id, name FROM semester ORDER BY name DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def create_semester(name: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO semester(name) VALUES (?)", (name,))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id

def get_semester_id_by_name(name: str):
    conn = get_connection()
    row = conn.execute("SELECT id FROM semester WHERE name = ?", (name,)).fetchone()
    conn.close()
    return row["id"] if row else None

# =============== SEMANAS ===============
def list_weeks(semester_id: int, q: str = ""):
    like = f"%{(q or '').lower()}%"
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, week_number, title, subtitle
        FROM week
        WHERE semester_id = ?
          AND (LOWER(title) LIKE ? OR LOWER(COALESCE(subtitle,'')) LIKE ?)
        ORDER BY week_number
        """,
        (semester_id, like, like),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def next_week_number(semester_id: int) -> int:
    conn = get_connection()
    n = conn.execute(
        "SELECT COALESCE(MAX(week_number), 0) + 1 AS n FROM week WHERE semester_id = ?",
        (semester_id,),
    ).fetchone()["n"]
    conn.close()
    return n

def create_week(semester_id: int, title: str, subtitle: str = ""):
    wn = next_week_number(semester_id)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO week(semester_id, week_number, title, subtitle) VALUES (?,?,?,?)",
        (semester_id, wn, title, subtitle),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return {"id": new_id, "week_number": wn, "title": title, "subtitle": subtitle}

def update_week(week_id: int, title=None, subtitle=None):
    conn = get_connection()
    conn.execute(
        "UPDATE week SET title = COALESCE(?, title), subtitle = COALESCE(?, subtitle) WHERE id = ?",
        (title, subtitle, week_id),
    )
    conn.commit()
    conn.close()

def delete_week(week_id: int) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM week WHERE id = ?", (week_id,))
    conn.commit()
    ch = cur.rowcount
    conn.close()
    return ch

# =============== TUTORES ===============
def list_tutors():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, name, email, capacity, assigned, (capacity - assigned) AS available
        FROM tutor
        ORDER BY name
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def assign_tutor_slots(tutor_id: int, count: int = 1):
    conn = get_connection()
    cur = conn.cursor()
    t = cur.execute("SELECT capacity, assigned FROM tutor WHERE id=?", (tutor_id,)).fetchone()
    if not t:
        conn.close()
        return {"error": "Tutor no encontrado"}, 404
    cap, asg = t["capacity"], t["assigned"]
    if asg + count > cap:
        conn.close()
        return {"error": "Capacidad llena"}, 400
    cur.execute("UPDATE tutor SET assigned = assigned + ? WHERE id = ?", (count, tutor_id))
    conn.commit()
    conn.close()
    return {"id": tutor_id, "assigned": asg + count, "available": cap - (asg + count)}, 200

# =============== ESTUDIANTES ===============
def list_students(filterv: str = "todos"):
    where = ""
    if filterv == "alerta":
        where = "WHERE s.status='Alerta'"
    elif filterv == "sin-tutor":
        where = "WHERE s.tutor_id IS NULL"

    conn = get_connection()
    rows = conn.execute(
        f"""
        SELECT s.id, s.code, s.name, s.status, COALESCE(t.name,'') AS tutor
        FROM student s
        LEFT JOIN tutor t ON t.id = s.tutor_id
        {where}
        ORDER BY s.name
        """
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# =============== REPORTES ===============
def insert_report(date: str, typ: str, user: str, file_path: str | None):
    conn = get_connection()
    conn.execute(
        "INSERT INTO report_log(date,type,user,file) VALUES (?,?,?,?)",
        (date, typ, user, file_path),
    )
    conn.commit()
    conn.close()

def list_reports():
    conn = get_connection()
    rows = conn.execute(
        "SELECT id, date, type, user, file FROM report_log ORDER BY id DESC LIMIT 200"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]
