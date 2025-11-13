// ============================
// MOSTRAR / OCULTAR CONTRASEÑA
// ============================
function togglePassword(inputId, iconId) {
  const input = document.getElementById(inputId);
  const icon = document.getElementById(iconId);

  if (input.type === "password") {
    input.type = "text";
    icon.classList.remove("fa-eye");
    icon.classList.add("fa-eye-slash");
  } else {
    input.type = "password";
    icon.classList.remove("fa-eye-slash");
    icon.classList.add("fa-eye");
  }
}

// ============================
// VALIDACIÓN DE CONTRASEÑA EN TIEMPO REAL
// ============================
const newpassInput = document.getElementById("newpass");
const ruleLength = document.getElementById("ruleLength");
const ruleUpper = document.getElementById("ruleUpper");
const ruleNumber = document.getElementById("ruleNumber");

if (newpassInput) {
  newpassInput.addEventListener("input", () => {
    const val = newpassInput.value;
    const lengthOk = val.length >= 8;
    const upperOk = /[A-Z]/.test(val);
    const numberOk = /\d/.test(val);

    ruleLength.classList.toggle("valid", lengthOk);
    ruleUpper.classList.toggle("valid", upperOk);
    ruleNumber.classList.toggle("valid", numberOk);
  });
}

// ============================
// GUARDAR NUEVA CONTRASEÑA
// ============================
function guardarNueva() {
  const newpass = document.getElementById("newpass").value;
  const confirmpass = document.getElementById("confirmpass").value;
  const msg = document.getElementById("msg3");

  const email = localStorage.getItem("emailRecuperacion");
  if (!email) {
    msg.textContent = "Error: no se encontró el correo. Regrese al paso anterior.";
    msg.style.color = "red";
    return;
  }

  if (newpass === "" || confirmpass === "") {
    msg.textContent = "Complete ambos campos.";
    msg.style.color = "red";
    return;
  }

  const lengthOk = newpass.length >= 8;
  const upperOk = /[A-Z]/.test(newpass);
  const numberOk = /\d/.test(newpass);

  if (!lengthOk || !upperOk || !numberOk) {
    msg.textContent = "La contraseña no cumple con los requisitos.";
    msg.style.color = "red";
    return;
  }

  if (newpass !== confirmpass) {
    msg.textContent = "Las contraseñas no coinciden.";
    msg.style.color = "red";
    return;
  }

  msg.textContent = "Guardando nueva contraseña...";
  msg.style.color = "#007bff";

  fetch("http://localhost:5000/api/reset-password", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password: newpass })
  })
    .then(res => res.json())
    .then(data => {
      if (data.error) {
        msg.textContent = data.error;
        msg.style.color = "red";
      } else {
        msg.textContent = data.message;
        msg.style.color = "green";

        // limpiar localStorage y redirigir
        localStorage.removeItem("emailRecuperacion");
        setTimeout(() => (window.location.href = "index.html"), 2500);
      }
    })
    .catch(err => {
      console.error("❌ Error:", err);
      msg.textContent = "Error de conexión con el servidor.";
      msg.style.color = "red";
    });
}
