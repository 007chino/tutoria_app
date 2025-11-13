import sqlite3
import bcrypt

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # === TABLA DE USUARIOS ===
    c.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            apellido TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # === TABLA DE CÓDIGOS DE VERIFICACIÓN ===
    c.execute("""
        CREATE TABLE IF NOT EXISTS codigos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            codigo TEXT NOT NULL,
            expira_en DATETIME NOT NULL
        )
    """)

    # === USUARIOS DE PRUEBA ===
    usuarios_demo = [
        ("Luz Diana", "Huamani", "215714@unsaac.edu.pe", "Luz1234"),
        ("Carlos", "Mendoza", "cmendoza@unsaac.edu.pe", "Carlos2024"),
        ("Valeria", "Quispe", "vquispe@unsaac.edu.pe", "Vale2025")
    ]

    for nombre, apellido, email, plain_password in usuarios_demo:
        # Encriptar la contraseña antes de guardarla
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())

        try:
            c.execute("INSERT INTO usuarios (nombre, apellido, email, password) VALUES (?, ?, ?, ?)",
                      (nombre, apellido, email, hashed))
        except sqlite3.IntegrityError:
            # Si ya existe el correo, lo ignoramos para evitar duplicados
            pass

    conn.commit()
    conn.close()
    print("✅ Base de datos creada con usuarios de prueba.")

# Ejecutar directamente el script para crear la BD
if __name__ == "__main__":
    init_db()
