function verificarCodigo() {
  const codigo = document.getElementById("codigo").value.trim();
  const email = localStorage.getItem("emailRecuperacion"); // Recuperamos el email que guardaste antes
  const msg = document.getElementById("msg2");

  if (!email) {
    msg.textContent = "Error: no se encontró el correo. Regrese al paso anterior.";
    msg.style.color = "red";
    return;
  }

  if (codigo === "") {
    msg.textContent = "Por favor, ingrese el código.";
    msg.style.color = "red";
    return;
  }

  const regexCodigo = /^\d{6}$/;
  if (!regexCodigo.test(codigo)) {
    msg.textContent = "El código debe tener exactamente 6 dígitos numéricos.";
    msg.style.color = "red";
    return;
  }

  msg.textContent = "Verificando código...";
  msg.style.color = "blue";

  // 🔹 Enviar al backend Flask
  fetch("http://localhost:5000/api/verify-code", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, codigo }) // ambos se envían como string
  })
    .then(async res => {
      const data = await res.json();
      if (res.ok) {
        msg.textContent = data.message;
        msg.style.color = "green";

        // Guardar el email para la siguiente pantalla (restablecer contraseña)
        localStorage.setItem("emailVerificado", email);

        setTimeout(() => {
          window.location.href = "Restablece.html";
        }, 2500);
      } else {
        msg.textContent = data.error || "Error en la verificación.";
        msg.style.color = "red";
      }
    })
    .catch(err => {
      console.error("❌ Error de conexión:", err);
      msg.textContent = "Error de conexión con el servidor.";
      msg.style.color = "red";
    });
}

// 🔹 Cargar el email automáticamente si existe
window.addEventListener("DOMContentLoaded", () => {
  const email = localStorage.getItem("emailRecuperacion");
  if (email) {
    document.getElementById("emailHidden").value = email;
  }
});
