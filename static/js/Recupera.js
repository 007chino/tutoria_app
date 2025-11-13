function enviarCodigo() {
  const email = document.getElementById("email").value.trim();
  const msg = document.getElementById("msg1");

  if (email === "") {
    msg.textContent = "Por favor, ingrese su correo electrónico.";
    msg.style.color = "red";
    return;
  }

  // Validar correo institucional UNSAAC
  const regexEmail = /^[a-zA-Z0-9._%+-]+@unsaac\.edu\.pe$/;
  if (!regexEmail.test(email)) {
    msg.textContent = "Ingrese un correo institucional válido (@unsaac.edu.pe).";
    msg.style.color = "red";
    return;
  }

  msg.textContent = "Enviando código de verificación...";
  msg.style.color = "blue";

  fetch("http://localhost:5000/api/send-code", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email })
  })
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      msg.textContent = data.error;
      msg.style.color = "red";
    } else {
      msg.textContent = data.message;
      msg.style.color = "green";

      // ✅ Guardar el correo en localStorage antes de redirigir
      localStorage.setItem("emailRecuperacion", email);

      // Redirigir a la página de verificación después de 2.5 s
      setTimeout(() => {
        window.location.href = "Verifica.html";
      }, 2500);
    }
  })
  .catch(err => {
    msg.textContent = "Error de conexión con el servidor.";
    msg.style.color = "red";
    console.error("❌ Error en la solicitud:", err);
  });
}
