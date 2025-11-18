// ===============================
// PANEL ADMIN - CARGA DE USUARIOS
// ===============================

document.addEventListener("DOMContentLoaded", () => {
  listarUsuarios();
});

const usuariosTableBody = document.querySelector("#usuariosTable tbody");

async function listarUsuarios() {
try {
  // RUTA CORRECTA PARA FLASK
  const res = await fetch("/api/usuarios");

  if (!res.ok) {
    throw new Error("No se pudo obtener la lista de usuarios");
  }

  const data = await res.json();

  usuariosTableBody.innerHTML = "";

  if (data.length === 0) {
    usuariosTableBody.innerHTML = `
      <tr>
        <td colspan="3" style="padding:15px; color:#777;">No hay usuarios registrados.</td>
      </tr>
    `;
    return;
  }

  data.forEach(usuario => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${usuario.id}</td>
      <td>${usuario.email}</td>
      <td>${usuario.rol}</td>
    `;
    usuariosTableBody.appendChild(row);
  });

} catch (err) {
  console.error("Error:", err);
  usuariosTableBody.innerHTML = `
    <tr>
      <td colspan="3" style="padding:15px; color:red; font-weight:bold;">
        Error al cargar usuarios
      </td>
    </tr>
  `;
}
}
