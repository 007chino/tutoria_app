# app_h.py
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os, csv, datetime

from init_db_h import init_db
import database_h as db

# --- App & CORS ---
app = Flask(__name__)
CORS(app)

# --- Paths ---
BASE_DIR = os.path.dirname(__file__)
REPORTS_DIR = os.path.join(BASE_DIR, "reports_h")
os.makedirs(REPORTS_DIR, exist_ok=True)

# --- Inicializa DB si es necesario ---
init_db()

# ============ SEMESTRES ============
@app.get("/api/semesters")
def semesters():
    return jsonify(db.list_semesters())

@app.post("/api/semesters")
def semester_create():
    name = (request.json or {}).get("name")
    if not name:
        return jsonify({"error": "name requerido"}), 400
    try:
        new_id = db.create_semester(name)
        return jsonify({"id": new_id, "name": name}), 201
    except Exception:
        return jsonify({"error": "duplicado"}), 409

# ============ SEMANAS ============
@app.get("/api/semesters/<int:sem_id>/weeks")
def weeks(sem_id):
    q = request.args.get("q", "")
    return jsonify(db.list_weeks(sem_id, q))

@app.post("/api/semesters/<int:sem_id>/weeks")
def week_create(sem_id):
    j = request.json or {}
    title = j.get("title")
    subtitle = j.get("subtitle", "")
    if not title:
        return jsonify({"error": "title requerido"}), 400
    payload = db.create_week(sem_id, title, subtitle)
    return jsonify(payload), 201

@app.patch("/api/weeks/<int:week_id>")
def week_update(week_id):
    j = request.json or {}
    title = j.get("title")
    subtitle = j.get("subtitle")
    db.update_week(week_id, title, subtitle)
    return jsonify({"id": week_id, "title": title, "subtitle": subtitle})

@app.delete("/api/weeks/<int:week_id>")
def week_delete(week_id):
    ch = db.delete_week(week_id)
    if not ch:
        return jsonify({"error": "Semana no encontrada"}), 404
    return jsonify({"ok": True})

# ============ TUTORES ============
@app.get("/api/tutors")
def tutors():
    return jsonify(db.list_tutors())

@app.post("/api/tutors/<int:tutor_id>/assign")
def tutor_assign(tutor_id):
    count = int((request.json or {}).get("count", 1))
    payload, code = db.assign_tutor_slots(tutor_id, count)
    return jsonify(payload), code

# ============ ESTUDIANTES ============
@app.get("/api/students")
def students():
    filterv = request.args.get("filter", "todos")
    return jsonify(db.list_students(filterv))

# ============ REPORTES ============
@app.post("/api/reports")
def reports_create():
    j = request.json or {}
    typ = j.get("type")  # semanal | mensual | csv
    user = j.get("user", "you@unsaac.edu")
    today = datetime.date.today().isoformat()
    file_url = None

    if typ == "csv":
        filename = f"reporte_{today}.csv"
        fpath = os.path.join(REPORTS_DIR, filename)

        # CSV de estudiantes
        rows = db.list_students("todos")
        with open(fpath, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["Código", "Estudiante", "Estado", "Tutor"])
            for r in rows:
                w.writerow([r["code"], r["name"], r["status"], r.get("tutor") or "(sin tutor)"])

        file_url = f"/files_h/{filename}"

    db.insert_report(today, typ, user, file_url)
    return jsonify({"date": today, "type": typ, "user": user, "file": file_url}), 201

@app.get("/api/reports/history")
def reports_history():
    return jsonify(db.list_reports())

@app.route("/files_h/<path:fname>")
def files_serve(fname):
    return send_from_directory(REPORTS_DIR, fname)

# ============ Salud ============
@app.get("/health")
def health():
    return jsonify({"ok": True})

if __name__ == "__main__":
    # pip install flask flask-cors
    app.run(host="127.0.0.1", port=5000, debug=True)
