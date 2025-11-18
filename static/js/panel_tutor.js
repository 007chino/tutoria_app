// ===============================
// PANEL TUTOR - CRUD DE TUTORÍAS
// ===============================

document.addEventListener("DOMContentLoaded", () => {
  listarTutorias();

  const form = document.getElementById("addTutoriaForm");
  form.addEventListener("submit", agregarTutoria);
});

/**
* Obtiene la lista de tutorías desde Flask
*/
async function listarTutorias() {
  try {
      const res = await fetch("/api/tutorias");
      const data = await res.json();

      const tbody = document.querySelector("#tutoriasTable tbody");
      tbody.innerHTML = "";

      if (data.length === 0) {
          tbody.innerHTML = `
              <tr><td colspan="4" style="padding:12px; text-align:center; color:#777">
              No hay tutorías registradas
              </td></tr>
          `;
          return;
      }

      data.forEach(t => {
          const row = document.createElement("tr");
          row.innerHTML = `
              <td>${t.id}</td>
              <td>${t.nombre_tutor}</td>
              <td>${t.curso}</td>
              <td>${t.fecha}</td>
          `;
          tbody.appendChild(row);
      });

  } catch (err) {
      console.error("Error al obtener tutorías:", err);
  }
}

/**
* Envía una nueva tutoría a Flask
*/
async function agregarTutoria(e) {
  e.preventDefault();

  const nombre_tutor = document.getElementById("nombre_tutor").value;
  const curso = document.getElementById("curso").value;
  const fecha = document.getElementById("fecha").value;

  const nuevaTutoria = { nombre_tutor, curso, fecha };

  try {
      const res = await fetch("/api/tutorias", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(nuevaTutoria)
      });

      const data = await res.json();

      alert(data.mensaje);

      document.getElementById("addTutoriaForm").reset();
      listarTutorias();

  } catch (err) {
      console.error("Error al agregar tutoría:", err);
  }
}
