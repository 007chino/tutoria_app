import random
import string
from flask_mail import Message
from flask import current_app

def generar_codigo():
    """Genera un código de 6 dígitos numéricos"""
    return ''.join(random.choices(string.digits, k=6))

def enviar_codigo(email, codigo):
    """Envía un correo real con el código de verificación"""
    try:
        mail = current_app.extensions.get('mail')
        if not mail:
            raise RuntimeError("❌ Flask-Mail no está inicializado correctamente.")

        msg = Message(
            subject="🔐 Código de verificación - Recuperación de contraseña",
            recipients=[email],
            body=f"""
Hola 👋,

Su código de verificación para restablecer la contraseña es: {codigo}

Este código es válido por 10 minutos.

Por favor, no comparta este código con nadie.

Atentamente,
Equipo UNSAAC
"""
        )
        mail.send(msg)
        print(f"✅ Correo enviado correctamente a {email}")

    except Exception as e:
        print(f"❌ Error al enviar correo a {email}: {e}")
