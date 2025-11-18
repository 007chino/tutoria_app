# app.py
# Sistema de tutorías - archivo unificado
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from flask_mail import Mail, Message
import sqlite3
import os, datetime
from dotenv import load_dotenv

# ------------------------------------------------------
# Configuración y app
# ------------------------------------------------------
load_dotenv()
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Mail
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587) if os.getenv('MAIL_PORT') else 587)
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "tutoria.db")

# ------------------------------------------------------
# Utilidades BD
# ------------------------------------------------------
def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Crea las tablas necesarias si no existen"""
    conn = get_connection()
    c = conn.cursor()

    # Tabla Usuarios: email, password, rol
    c.execute('''
        CREATE TABLE IF NOT EXISTS Usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT,
            rol TEXT
        )
    ''')

    # Tabla Tutorias
    c.execute('''
        CREATE TABLE IF NOT EXISTS Tutorias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_tutor TEXT,
            curso TEXT,
            fecha TEXT,
            estado TEXT DEFAULT 'Pendiente'
        )
    ''')

    # Tabla Recuperacion
    c.execute('''
        CREATE TABLE IF NOT EXISTS Recuperacion (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            token TEXT,
            expiracion DATETIME
        )
    ''')

    # Usuarios de prueba (si aún no existen)
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

# Inicializar DB al iniciar
init_db()

# ------------------------------------------------------
# Rutas que sirven las páginas (templates)
# ------------------------------------------------------
@app.route('/')
def root():
    # Página principal: inicio de sesión según indicaste
    return render_template('index_inicio_sesion.html')

@app.route('/inicio')
def inicio_sesion_view():
    return render_template('index_inicio_sesion.html')

@app.route('/recuperar_view')
def recuperar_view():
    return render_template('Recupera.html')

@app.route('/verifica_view')
def verifica_view():
    return render_template('Verifica.html')

@app.route('/restablece_view')
def restablece_view():
    return render_template('Restablece.html')

@app.route('/crear_cuenta_view')
def crear_cuenta_view():
    return render_template('index_crear_cuenta.html')

@app.route('/proyec_horario_view')
def proyec_horario_view():
    return render_template('proyec_horario.html')

# Paneles por rol
@app.route('/panel/admin')
def panel_admin_view():
    return render_template('panel_admin.html')

@app.route('/panel/tutor')
def panel_tutor_view():
    return render_template('panel_tutor.html')

@app.route('/panel/verificador')
def panel_verificador_view():
    return render_template('panel_verificador.html')

# ------------------------------------------------------
# API - Autenticación, usuarios y tutorías
# Se crean endpoints con y sin prefijo /api para compatibilidad
# ------------------------------------------------------

# --- LOGIN ---
def _login_logic(email, password):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT rol FROM Usuarios WHERE email=? AND password=?", (email, password))
    row = c.fetchone()
    conn.close()
    if row:
        return True, row["rol"]
    else:
        return False, None

@app.route('/login', methods=['POST'])
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json() or request.form
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email y contraseña requeridos'}), 400
    ok, rol = _login_logic(email, password)
    if ok:
        return jsonify({'success': True, 'rol': rol})
    else:
        return jsonify({'success': False, 'message': 'Correo o contraseña incorrectos'}), 401

# --- CREAR CUENTA ---
@app.route('/crear_cuenta', methods=['POST'])
@app.route('/api/crear_cuenta', methods=['POST'])
def crear_cuenta():
    data = request.get_json() or request.form
    rol = data.get('rol')
    email = data.get('email')
    password = data.get('password')

    if not rol or not email or not password:
        return jsonify({'success': False, 'message': 'Faltan datos'}), 400

    try:
        conn = get_connection()
        c = conn.cursor()
        # tabla Usuarios tiene columnas (email, password, rol)
        c.execute("INSERT INTO Usuarios (email, password, rol) VALUES (?, ?, ?)",
                  (email, password, rol))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Usuario creado exitosamente'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'El correo ya está registrado'}), 409

# --- LISTAR USUARIOS ---
@app.route('/usuarios', methods=['GET'])
@app.route('/api/usuarios', methods=['GET'])
def listar_usuarios():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, email, rol FROM Usuarios")
    rows = c.fetchall()
    conn.close()
    return jsonify([{'id': r['id'], 'email': r['email'], 'rol': r['rol']} for r in rows])

# --- TUTORIAS (GET/POST) ---
@app.route('/tutorias', methods=['GET'])
@app.route('/api/tutorias', methods=['GET'])
def listar_tutorias():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM Tutorias")
    rows = c.fetchall()
    conn.close()
    tutorias = []
    for r in rows:
        tutorias.append({
            'id': r['id'],
            'nombre_tutor': r['nombre_tutor'],
            'curso': r['curso'],
            'fecha': r['fecha'],
            'estado': r['estado']
        })
    return jsonify(tutorias)

@app.route('/tutorias', methods=['POST'])
@app.route('/api/tutorias', methods=['POST'])
def agregar_tutoria():
    data = request.get_json() or request.form
    nombre_tutor = data.get('nombre_tutor')
    curso = data.get('curso')
    fecha = data.get('fecha')
    if not nombre_tutor or not curso or not fecha:
        return jsonify({'success': False, 'message': 'Faltan datos de la tutoría'}), 400
    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO Tutorias (nombre_tutor, curso, fecha) VALUES (?, ?, ?)",
              (nombre_tutor, curso, fecha))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Tutoría registrada correctamente'})

# ------------------------------------------------------
# RECUPERACIÓN DE CONTRASEÑA
# ------------------------------------------------------
@app.route('/recuperar', methods=['POST'])
@app.route('/api/recuperar', methods=['POST'])
def recuperar():
    data = request.get_json() or request.form
    email = data.get('email')
    if not email:
        return jsonify({'success': False, 'message': 'Correo requerido'}), 400

    token = os.urandom(8).hex()
    expiracion = datetime.datetime.datetime.now() + datetime.timedelta(minutes=30) if False else datetime.datetime.now() + datetime.timedelta(minutes=30)
    # store as ISO string
    expiracion_str = expiracion.isoformat()

    conn = get_connection()
    c = conn.cursor()
    c.execute("INSERT INTO Recuperacion (email, token, expiracion) VALUES (?, ?, ?)",
              (email, token, expiracion_str))
    conn.commit()
    conn.close()

    # Enviar correo
    try:
        msg = Message("Recuperación de contraseña - Sistema de Tutorías", recipients=[email])
        msg.body = f"Tu código de recuperación es: {token}\nVálido por 30 minutos."
        mail.send(msg)
        return jsonify({'success': True, 'message': 'Correo enviado correctamente'})
    except Exception as e:
        # Si falla enviar correo, devolvemos token en respuesta (útil para desarrollo local)
        return jsonify({'success': False, 'message': f'Error al enviar correo: {e}', 'token': token}), 500

@app.route('/restablecer', methods=['POST'])
@app.route('/api/restablecer', methods=['POST'])
def restablecer():
    data = request.get_json() or request.form
    email = data.get('email')
    token = data.get('token')
    nueva = data.get('nueva')

    if not email or not token or not nueva:
        return jsonify({'success': False, 'message': 'Faltan datos'}), 400

    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT expiracion FROM Recuperacion WHERE email=? AND token=? ORDER BY id DESC LIMIT 1", (email, token))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({'success': False, 'message': 'Token inválido'}), 400

    try:
        expiracion = datetime.datetime.datetime.fromisoformat(row['expiracion'])
    except Exception:
        # fallback parse
        expiracion = datetime.datetime.datetime.strptime(row['expiracion'], "%Y-%m-%dT%H:%M:%S.%f")

    if datetime.datetime.datetime.now() > expiracion:
        conn.close()
        return jsonify({'success': False, 'message': 'Token expirado'}), 400

    c.execute("UPDATE Usuarios SET password=? WHERE email=?", (nueva, email))
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'message': 'Contraseña actualizada correctamente'})

# ------------------------------------------------------
# RUTA ÚTIL: redirigir a panel según rol (útil desde frontend)
# ------------------------------------------------------
@app.route('/panel_por_rol', methods=['GET'])
def panel_por_rol():
    # recibe ?rol=Administrador  o Tutor o Verificador
    rol = request.args.get('rol', '')
    if rol.lower().startswith('admin') or 'administrador' in rol.lower():
        return redirect(url_for('panel_admin_view'))
    if 'tutor' in rol.lower():
        return redirect(url_for('panel_tutor_view'))
    if 'verificador' in rol.lower():
        return redirect(url_for('panel_verificador_view'))
    # por defecto vuelve a inicio
    return redirect(url_for('inicio_sesion_view'))

# ------------------------------------------------------
# Ejecutar servidor
# ------------------------------------------------------
if __name__ == '__main__':
    # Asegura que exista la DB y carpetas
    if not os.path.exists(DB_PATH):
        init_db()
    app.run(debug=True, port=5000)
