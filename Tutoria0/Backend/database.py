import sqlite3

# Conexión (si no existe la base, la crea automáticamente)
conn = sqlite3.connect('tutorias.db')

# Crear cursor
cursor = conn.cursor()

# Crear tabla de ejemplo (puedes modificarla según tu sistema)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS tutorias (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        correo TEXT NOT NULL,
        tema TEXT NOT NULL
    )
''')

# Guardar y cerrar
conn.commit()
conn.close()

print("✅ Base de datos y tabla creadas correctamente.")
