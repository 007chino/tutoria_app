# ======================================================
#  SISTEMA DE TUTORÍAS UNIFICADO
#  Módulos:
#   1. Inicio de sesión / Usuarios / Tutorías
#   2. Recuperación de contraseña
#   3. Creación de cuenta
# ======================================================

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mail import Mail, Message
import sqlite3, os, datetime
from dotenv import load_dotenv

# ------------------------------------------------------
# CONFIGURACIÓN INICIAL
# ------------------------------------------------------
app = Flask(__name__)
CORS(app)
load_dotenv()

# Configuración del correo (para recuperación)
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# ------------------------------------------------------
# CONEXIÓN A LA BASE DE DATOS
# ------------------------------------------------------
def get_connection():
    return sqlite3.connect("tutoria.db")

def init_db():
    """Crea las tablas necesarias si no existen"""
    conn = get_connection()
    c = conn.cursor()

    # Tabla de usuarios
    c.execute('''
        CREATE TABLE IF NOT EXISTS Usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT,
            rol TEXT
        )
    ''')

    # Tabla de tutorías
    c.execute('''
        CREATE TABLE IF NOT EXISTS Tutorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_tutor TEXT,
            curso TEXT,
            fecha TEXT,
            estado TEXT DEFAULT 'Pendiente'
        )
    ''')

    # Tabla para recuperación de contraseñas
    c.execute('''
        CREATE TABLE IF NOT EXISTS Recuperacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            token TEXT,
            expiracion DATETIME
        )
    ''')

    # Insertar usuarios de prueba (solo si no existen)
    usuarios_prueba = [
        ("admin@unsaac.edu.pe", "admin123", "Administrador"),
        ("tutor@unsaac.edu.pe", "tutor123", "Tutor"),
        ("verificador@unsaac.edu.pe", "verif123", "Verificador")
    ]
    for email, password, rol in usuarios_prueba:
        c.execute("INSERT OR IGNORE INTO Usuarios (email, password, rol) VALUES (?, ?, ?)",
                  (email, password, rol))

    conn.commit()
    conn.close()

# ======================================================
# 1️⃣ MÓDULO: INICIO DE SESIÓN / USUARIOS / TUTORÍAS
# ======================================================

@app.route('/')
def home():
    return '✅ Backend unificado de Tutorías funcionando correctamente'

# -------------------------------
# LOGIN
# -------------------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT rol FROM Usuarios WHERE email=? AND password=?", (email, password))
    row = c.fetchone()
    conn.close()

    if row:
        return jsonify({"success": True, "rol": row[0]})
    else:
        return jsonify({"success": False, "message": "Correo o contraseña incorrectos"})

# -------------------------------
# LISTAR USUARIOS
# -------------------------------
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, email, rol FROM Usuarios")
    rows = c.fetchall()
    conn.close()
    return jsonify([{'id': r[0], 'email': r[1], 'rol': r[2]} for r in rows])

# -------------------------------
# LISTAR TUTORÍAS
# -------------------------------
@app.route('/tutorias', methods=['GET'])
def listar_tutorias():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM Tutorias")
    rows = c.fetchall()
    conn.close()
    return jsonify([{
        'id': r[0],
        'nombre_tutor': r[1],
        'curso': r[2],
        'fecha': r[3],
        'estado': r[4]
    } for r in rows])

# -------------------------------
# AGREGAR TUTORÍA
# -------------------------------
@app.route('/tutorias', methods=['POST'])
def agregar_tutoria():
    data = request.get_json()
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO Tutorias (nombre_tutor, curso, fecha) VALUES (?, ?, ?)",
              (data['nombre_tutor'], data['curso'], data['fecha']))
    conn.commit()
    conn.close()
    return jsonify({'mensaje': 'Tutoría registrada correctamente'})

# ======================================================
# 2️⃣ MÓDULO: RECUPERACIÓN DE CONTRASEÑA
# ======================================================

@app.route('/recuperar', methods=['POST'])
def recuperar():
    """Genera un token y lo envía al correo del usuario"""
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'success': False, 'message': 'Correo requerido'})

    token = os.urandom(8).hex()
    expiracion = datetime.datetime.now() + datetime.timedelta(minutes=30)

    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO Recuperacion (email, token, expiracion) VALUES (?, ?, ?)",
              (email, token, expiracion))
    conn.commit()
    conn.close()

    try:
        msg = Message("Recuperación de contraseña - Sistema de Tutorías", recipients=[email])
        msg.body = f"Tu código de recuperación es: {token}\nVálido por 30 minutos."
        mail.send(msg)
        return jsonify({'success': True, 'message': 'Correo enviado correctamente'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error al enviar correo: {e}'})

@app.route('/restablecer', methods=['POST'])
def restablecer():
    """Verifica el token y actualiza la contraseña"""
    data = request.get_json()
    email = data.get('email')
    token = data.get('token')
    nueva = data.get('nueva')

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT expiracion FROM Recuperacion WHERE email=? AND token=?", (email, token))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({'success': False, 'message': 'Token inválido'})

    expiracion = datetime.datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
    if datetime.datetime.now() > expiracion:
        conn.close()
        return jsonify({'success': False, 'message': 'Token expirado'})

    c.execute("UPDATE Usuarios SET password=? WHERE email=?", (nueva, email))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Contraseña actualizada correctamente'})

# ======================================================
# 3️⃣ MÓDULO: CREACIÓN DE CUENTA
# ======================================================

@app.route('/crear_cuenta', methods=['POST'])
def crear_cuenta():
    """Registra un nuevo usuario"""
    data = request.get_json()
    rol = data.get('rol')
    email = data.get('email')
    password = data.get('password')

    if not rol or not email or not password:
        return jsonify({'success': False, 'message': 'Faltan datos'})

    try:
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO Usuarios (rol, email, password) VALUES (?, ?, ?)",
                  (rol, email, password))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Usuario creado exitosamente'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'El correo ya está registrado'})

# ======================================================
# EJECUCIÓN DEL SERVIDOR
# ======================================================
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
