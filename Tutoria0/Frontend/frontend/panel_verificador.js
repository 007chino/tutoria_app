const tableBody = document.querySelector("#tutoriasVerificarTable tbody");

async function listarTutoriasPendientes() {
  try {
    const res = await fetch("http://127.0.0.1:5000/tutorias"); // Usamos mismas tutorías
    const data = await res.json();

    tableBody.innerHTML = "";
    data.forEach(tutoria => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${tutoria.id}</td>
        <td>${tutoria.nombre_tutor}</td>
        <td>${tutoria.curso}</td>
        <td>${tutoria.fecha}</td>
        <td>
          <button onclick="alert('Tutoría aprobada!')">Aprobar</button>
          <button onclick="alert('Tutoría rechazada!')">Rechazar</button>
        </td>
      `;
      tableBody.appendChild(row);
    });
  } catch (err) {
    console.error("Error al cargar tutorías:", err);
  }
}

// Cargar tutorías al abrir la página
listarTutoriasPendientes();
