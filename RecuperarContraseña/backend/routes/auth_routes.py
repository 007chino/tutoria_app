from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime, timedelta
import bcrypt
from utils.email_utils import generar_codigo, enviar_codigo

auth_routes = Blueprint('auth_routes', __name__)

DB_PATH = "database.db"

# Enviar código al email institucional
@auth_routes.route("/api/send-code", methods=["POST"])
def send_code():
    data = request.get_json()
    email = data.get("email")

    if not email or not email.endswith("@unsaac.edu.pe"):
        return jsonify({"error": "Correo institucional inválido."}), 400

    expira = datetime.now() + timedelta(minutes=10)
    codigo = str(generar_codigo())  # asegurarse de que sea string

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO codigos (email, codigo, expira_en) VALUES (?, ?, ?)", (email, codigo, expira.isoformat()))
    conn.commit()
    conn.close()

    enviar_codigo(email, codigo)

    return jsonify({"message": "Código enviado correctamente."})

# Verificar código enviado
@auth_routes.route("/api/verify-code", methods=["POST"])
def verify_code():
    data = request.get_json()
    email = data.get("email")
    codigo = data.get("codigo").strip()  # asegurarse de quitar espacios

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT codigo, expira_en FROM codigos WHERE email=? ORDER BY id DESC LIMIT 1", (email,))
    row = c.fetchone()
    conn.close()

    if not row:
        return jsonify({"error": "Código no encontrado."}), 404

    codigo_db, expira = row
    codigo_db = str(codigo_db)  # convertir a string por si acaso

    if datetime.now() > datetime.fromisoformat(expira):
        return jsonify({"error": "El código ha expirado."}), 400

    if codigo != codigo_db:
        return jsonify({"error": "Código incorrecto."}), 400

    return jsonify({"message": "Código verificado correctamente."})


# Restablecer contraseña
@auth_routes.route("/api/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    email = data.get("email")
    newpass = data.get("password")

    hashed = bcrypt.hashpw(newpass.encode('utf-8'), bcrypt.gensalt())

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE usuarios SET password=? WHERE email=?", (hashed, email))
    conn.commit()
    conn.close()

    return jsonify({"message": "Contraseña actualizada correctamente."})
