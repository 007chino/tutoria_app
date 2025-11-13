from flask import Flask
from flask_cors import CORS
from flask_mail import Mail
import os
from dotenv import load_dotenv
from routes.auth_routes import auth_routes

# Crear la app
app = Flask(__name__)
CORS(app)
load_dotenv()  # Cargar variables de entorno

# Configuración del correo
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')

mail = Mail(app)

# Registrar blueprint con rutas
app.register_blueprint(auth_routes)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
