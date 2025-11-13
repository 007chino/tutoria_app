
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date as DateType, timedelta
import sqlite3
import os

# Ruta al archivo SQLite (ajusta si lo pones en otra carpeta)
DB_PATH = os.path.join(os.path.dirname(__file__), "tutorias_con_datos.db")


def get_db():
    """Devuelve una conexión a la base de datos con row_factory=Row."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


app = FastAPI(title="API Tutorías UNSAAC", version="1.0.0")

# CORS para permitir llamadas desde tu front (ajusta origins en producción)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # p.ej. ["http://localhost:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ======== MODELOS Pydantic ========

class Career(BaseModel):
    id: int
    name: str


class Tutor(BaseModel):
    id: int
    full_name: str
    career_id: int
    career_name: str


class Room(BaseModel):
    id: int
    name: str


class Session(BaseModel):
    id: int
    tutor_id: int
    tutor_name: str
    room_id: int
    room_name: str
    date: DateType
    start_time: str
    end_time: str
    notes: Optional[str] = None


class SessionCreate(BaseModel):
    tutor_id: int = Field(..., description="ID del tutor")
    room_id: int = Field(..., description="ID del ambiente")
    date: DateType = Field(..., description="Fecha de la tutoría (YYYY-MM-DD)")
    start_time: str = Field(..., pattern=r"^[0-2][0-9]:[0-5][0-9]$", description="Hora inicio HH:MM")
    end_time: str = Field(..., pattern=r"^[0-2][0-9]:[0-5][0-9]$", description="Hora fin HH:MM")
    notes: Optional[str] = None


# ======== ENDPOINTS CATÁLOGOS ========

@app.get("/careers", response_model=List[Career])
def list_careers():
    with get_db() as conn:
        cur = conn.execute("SELECT id, name FROM careers ORDER BY name")
        rows = cur.fetchall()
    return [Career(id=r["id"], name=r["name"]) for r in rows]


@app.get("/tutors", response_model=List[Tutor])
def list_tutors(
    q: Optional[str] = Query(default=None, description="Buscar por nombre"),
    career_id: Optional[int] = Query(default=None, description="Filtrar por carrera"),
):
    sql = (
        "SELECT t.id, t.full_name, t.career_id, c.name AS career_name "
        "FROM tutors t JOIN careers c ON c.id = t.career_id WHERE 1=1"
    )
    params: list = []
    if q:
        sql += " AND t.full_name LIKE ?"
        params.append(f"%{q}%")
    if career_id is not None:
        sql += " AND t.career_id = ?"
        params.append(career_id)
    sql += " ORDER BY t.full_name"

    with get_db() as conn:
        cur = conn.execute(sql, params)
        rows = cur.fetchall()

    return [
        Tutor(
            id=r["id"],
            full_name=r["full_name"],
            career_id=r["career_id"],
            career_name=r["career_name"],
        )
        for r in rows
    ]


@app.get("/rooms", response_model=List[Room])
def list_rooms():
    with get_db() as conn:
        cur = conn.execute("SELECT id, name FROM rooms ORDER BY name")
        rows = cur.fetchall()
    return [Room(id=r["id"], name=r["name"]) for r in rows]


# ======== ENDPOINTS SESIONES ========

@app.get("/sessions/week", response_model=List[Session])
def list_sessions_week(start: DateType = Query(..., description="Lunes (o cualquier día) de la semana")):
    """Devuelve todas las sesiones de la semana [start, start+7)."""
    week_start = start
    week_end = week_start + timedelta(days=7)

    with get_db() as conn:
        cur = conn.execute(
            """SELECT s.id,
                       s.tutor_id,
                       t.full_name AS tutor_name,
                       s.room_id,
                       r.name      AS room_name,
                       s.date,
                       s.start_time,
                       s.end_time,
                       s.notes
                  FROM sessions s
                  JOIN tutors t ON t.id = s.tutor_id
                  JOIN rooms  r ON r.id = s.room_id
                 WHERE s.date >= ? AND s.date < ?
                 ORDER BY s.date, s.start_time""",
            (week_start.isoformat(), week_end.isoformat()),
        )
        rows = cur.fetchall()

    return [
        Session(
            id=r["id"],
            tutor_id=r["tutor_id"],
            tutor_name=r["tutor_name"],
            room_id=r["room_id"],
            room_name=r["room_name"],
            date=DateType.fromisoformat(r["date"]),
            start_time=r["start_time"],
            end_time=r["end_time"],
            notes=r["notes"],
        )
        for r in rows
    ]


@app.post("/sessions", response_model=Session, status_code=201)
def create_session(payload: SessionCreate):
    """Crea una nueva sesión, respetando los triggers de conflicto de la BD."""
    # Validación básica de rango horario en Python (la BD también valida)
    if not ("07:00" <= payload.start_time < payload.end_time <= "21:00"):
        raise HTTPException(status_code=400, detail="Horario fuera de rango 07:00–21:00 o fin <= inicio")

    with get_db() as conn:
        # Verificar tutor
        cur = conn.execute("SELECT id, full_name FROM tutors WHERE id = ?", (payload.tutor_id,))
        tutor_row = cur.fetchone()
        if not tutor_row:
            raise HTTPException(status_code=404, detail="Tutor no encontrado")

        # Verificar ambiente
        cur = conn.execute("SELECT id, name FROM rooms WHERE id = ?", (payload.room_id,))
        room_row = cur.fetchone()
        if not room_row:
            raise HTTPException(status_code=404, detail="Ambiente no encontrado")

        try:
            cur = conn.execute(
                "INSERT INTO sessions (tutor_id, room_id, date, start_time, end_time, notes) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (
                    payload.tutor_id,
                    payload.room_id,
                    payload.date.isoformat(),
                    payload.start_time,
                    payload.end_time,
                    payload.notes,
                ),
            )
            new_id = cur.lastrowid
            conn.commit()
        except sqlite3.IntegrityError as e:
            # Los triggers devuelven mensajes claros de conflicto
            raise HTTPException(status_code=400, detail=str(e))

        # Recuperar el registro completo con JOIN
        cur = conn.execute(
            """SELECT s.id,
                       s.tutor_id,
                       t.full_name AS tutor_name,
                       s.room_id,
                       r.name      AS room_name,
                       s.date,
                       s.start_time,
                       s.end_time,
                       s.notes
                  FROM sessions s
                  JOIN tutors t ON t.id = s.tutor_id
                  JOIN rooms  r ON r.id = s.room_id
                 WHERE s.id = ?""",
            (new_id,),
        )
        row = cur.fetchone()

    return Session(
        id=row["id"],
        tutor_id=row["tutor_id"],
        tutor_name=row["tutor_name"],
        room_id=row["room_id"],
        room_name=row["room_name"],
        date=DateType.fromisoformat(row["date"]),
        start_time=row["start_time"],
        end_time=row["end_time"],
        notes=row["notes"],
    )


@app.get("/")
def root():
    return {"message": "API Tutorías UNSAAC OK"}
