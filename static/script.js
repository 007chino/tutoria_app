async function crearCuenta() {
  const rol = document.getElementById('rol').value;
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const confirm = document.getElementById('confirm').value;
  const mensajeEl = document.getElementById('mensaje');

  // reset
  mensajeEl.textContent = '';
  mensajeEl.classList.remove('error','ok');

  // validaciones
  if (!rol || !email || !password || !confirm) {
    mensajeEl.textContent = 'Por favor, completa todos los campos.';
    mensajeEl.classList.add('error');
    return;
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    mensajeEl.textContent = 'Por favor, ingresa un correo válido.';
    mensajeEl.classList.add('error');
    return;
  }

  if (password !== confirm) {
    mensajeEl.textContent = 'Las contraseñas no coinciden.';
    mensajeEl.classList.add('error');
    return;
  }

  if (password.length < 6) {
    mensajeEl.textContent = 'La contraseña debe tener al menos 6 caracteres.';
    mensajeEl.classList.add('error');
    return;
  }

  // petición al servidor
  try {
    const res = await fetch('/crear_cuenta', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ rol, email, password })
    });

    const data = await res.json();

    if (res.ok && data.success) {
      mensajeEl.textContent = data.message || '✅ Cuenta creada correctamente.';
      mensajeEl.classList.add('ok');
      // limpiar campos
      document.getElementById('rol').selectedIndex = 0;
      document.getElementById('email').value = '';
      document.getElementById('password').value = '';
      document.getElementById('confirm').value = '';
    } else {
      // mostrar error servidor (por ejemplo: correo duplicado)
      mensajeEl.textContent = data.message || 'Error al crear la cuenta.';
      mensajeEl.classList.add('error');
    }
  } catch (err) {
    console.error(err);
    mensajeEl.textContent = 'Error de conexión con el servidor.';
    mensajeEl.classList.add('error');
  }
}

/* Conectar también el botón por si se agrega listener */
document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('btn-crear');
  if (btn) btn.addEventListener('click', (e) => { e.preventDefault(); crearCuenta(); });
});
