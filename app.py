from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)

# -----------------------------
# CREACIÓN DE TABLA
# -----------------------------
def crear_tabla():
    conn = sqlite3.connect('tutoria.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rol TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# -----------------------------
# RUTAS
# -----------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/crear_cuenta', methods=['POST'])
def crear_cuenta():
    data = request.get_json()
    rol = data.get('rol')
    email = data.get('email')
    password = data.get('password')

    if not rol or not email or not password:
        return jsonify({'success': False, 'message': 'Faltan datos'})

    try:
        conn = sqlite3.connect('tutoria.db')
        c = conn.cursor()
        c.execute("INSERT INTO usuarios (rol, email, password) VALUES (?, ?, ?)", (rol, email, password))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Usuario creado exitosamente'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'El correo ya está registrado'})

# -----------------------------
# EJECUCIÓN PRINCIPAL
# -----------------------------
if __name__ == '__main__':
    crear_tabla()
    app.run(debug=True)
