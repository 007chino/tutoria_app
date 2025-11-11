import sqlite3

def init_users():
    conn = sqlite3.connect('tutorias.db')
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        password TEXT,
        rol TEXT
    )
    """)

    # Insertar usuarios de prueba (solo si no existen)
    usuarios = [
        ('admin@unsaac.edu.pe', '1234', 'Administrador'),
        ('tutor@unsaac.edu.pe', '1234', 'Tutor'),
        ('verificador@unsaac.edu.pe', '1234', 'Verificador')
    ]
    for u in usuarios:
        try:
            cursor.execute("INSERT INTO Usuarios (email, password, rol) VALUES (?, ?, ?)", u)
        except:
            pass  # ya existe
    conn.commit()
    conn.close()
    print("✅ Tabla de usuarios lista con datos de prueba")
