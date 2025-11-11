from flask import Flask, request, jsonify
from flask_cors import CORS
from db_connection import get_connection

app = Flask(__name__)
CORS(app)

# -------------------------------
# Función para crear tabla de tutorías
# -------------------------------
def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Tutorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_tutor TEXT,
        curso TEXT,
        fecha TEXT,
        estado TEXT DEFAULT 'Pendiente'
    )
    """)
    conn.commit()
    conn.close()

# -------------------------------
# Función para crear tabla de usuarios y agregar prueba
# -------------------------------
def init_users():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        rol TEXT
    )
    """)

    usuarios_prueba = [
        ("admin@unsaac.edu.pe", "admin123", "Administrador"),
        ("tutor@unsaac.edu.pe", "tutor123", "Tutor"),
        ("verificador@unsaac.edu.pe", "verif123", "Verificador")
    ]

    for email, password, rol in usuarios_prueba:
        cursor.execute("INSERT OR IGNORE INTO Usuarios (email, password, rol) VALUES (?, ?, ?)",
                       (email, password, rol))

    conn.commit()
    conn.close()

# -------------------------------
# Endpoint de prueba
# -------------------------------
@app.route('/')
def home():
    return '✅ Backend de Tutorías con SQLite funcionando correctamente'

# -------------------------------
# Endpoints de tutorías
# -------------------------------
@app.route('/tutorias', methods=['GET'])
def listar_tutorias():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Tutorias")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([
        {'id': r[0], 'nombre_tutor': r[1], 'curso': r[2], 'fecha': r[3], 'estado': r[4]}
        for r in rows
    ])

@app.route('/tutorias', methods=['POST'])
def agregar_tutoria():
    data = request.get_json()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO Tutorias (nombre_tutor, curso, fecha) VALUES (?, ?, ?)",
        (data['nombre_tutor'], data['curso'], data['fecha'])
    )
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Tutoría registrada correctamente '})

# -------------------------------
# Endpoint de login
# -------------------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT rol FROM Usuarios WHERE email=? AND password=?", (email, password))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({"success": True, "rol": row[0]})
    else:
        return jsonify({"success": False, "message": "Correo o contraseña incorrectos"})

# -------------------------------
# Endpoint para listar usuarios (solo admin)
# -------------------------------
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, rol FROM Usuarios")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([
        {'id': r[0], 'email': r[1], 'rol': r[2]}
        for r in rows
    ])

# -------------------------------
# Ejecutar servidor
# -------------------------------
if __name__ == '__main__':
    init_db()
    init_users()
    app.run(debug=True, port=5000)
