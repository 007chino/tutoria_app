const usuariosTableBody = document.querySelector("#usuariosTable tbody");

async function listarUsuarios() {
  try {
    const res = await fetch("http://127.0.0.1:5000/usuarios"); // Debes crear endpoint /usuarios en Flask
    const data = await res.json();

    usuariosTableBody.innerHTML = "";
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
    console.error("Error al cargar usuarios:", err);
  }
}

// Cargar usuarios al abrir la página
listarUsuarios();
