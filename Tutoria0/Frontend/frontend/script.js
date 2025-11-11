document.getElementById("loginForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const emailInput = document.getElementById("email");
  const passwordInput = document.getElementById("password");
  const errorMsg = document.getElementById("errorMsg");

  const email = emailInput.value.trim();
  const password = passwordInput.value.trim();

  let hasError = false;

  // Limpiar estilos anteriores
  emailInput.style.border = "";
  passwordInput.style.border = "";
  errorMsg.textContent = "";
  errorMsg.classList.remove("success");

  // Validar correo institucional
  const emailPattern = /^[a-zA-Z0-9._%+-]+@unsaac\.edu\.pe$/;
  if (!emailPattern.test(email)) {
    errorMsg.textContent = "El correo debe ser institucional (terminar en @unsaac.edu.pe)";
    emailInput.style.border = "2px solid red";
    hasError = true;
  }

  // Validar contraseña mínima
  if (password.length < 4) {
    if (errorMsg.textContent) errorMsg.textContent += " | ";
    errorMsg.textContent += "La contraseña debe tener al menos 4 caracteres";
    passwordInput.style.border = "2px solid red";
    hasError = true;
  }

  if (hasError) return;

  try {
    const res = await fetch("http://127.0.0.1:5000/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    if (data.success) {
      // Campos correctos → borde verde
      emailInput.style.border = "2px solid green";
      passwordInput.style.border = "2px solid green";
      errorMsg.style.color = "green";
      errorMsg.classList.add("success");
      errorMsg.textContent = `Bienvenido, ${data.rol}`;

      // Redirigir después de 1 segundo
      setTimeout(() => {
        if (data.rol === "Administrador") window.location.href = "panel_admin.html";
        else if (data.rol === "Tutor") window.location.href = "panel_tutor.html";
        else if (data.rol === "Verificador") window.location.href = "panel_verificador.html";
      }, 1000);
    } else {
      errorMsg.style.color = "red";
      errorMsg.textContent = data.message;
      emailInput.style.border = "2px solid red";
      passwordInput.style.border = "2px solid red";
    }
  } catch (err) {
    console.error(err);
    errorMsg.style.color = "red";
    errorMsg.textContent = "Error al conectar con el servidor";
  }
});
