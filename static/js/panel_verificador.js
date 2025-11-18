// ===============================
// PANEL VERIFICADOR
// ===============================

document.addEventListener("DOMContentLoaded", () => {
  listarTutoriasPorValidar();
});

/**
* Obtiene las tutorías que aún no están validadas
*/
async function listarTutoriasPorValidar() {
  try {
      const res = await fetch("/api/tutorias/pendientes");
      const data = await res.json();

      const tbody = document.querySelector("#tutoriasVerificarTable tbody");
      tbody.innerHTML = "";

      if (data.length === 0) {
          tbody.innerHTML = `
              <tr>
                  <td colspan="5" style="padding:12px; text-align:center; color:#777">
                      No hay tutorías pendientes de validación.
                  </td>
              </tr>
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
              <td>
                  <button class="btn-validar" onclick="validarTutoria(${t.id})">
                      Validar
                  </button>
              </td>
          `;
          tbody.appendChild(row);
      });

  } catch (err) {
      console.error("Error al cargar tutorías:", err);
  }
}

/**
* Envía una validación al backend
*/
async function validarTutoria(id) {
  if (!confirm("¿Confirmar validación?")) return;

  try {
      const res = await fetch(`/api/tutorias/validar/${id}`, {
          method: "PUT"
      });

      const data = await res.json();
      alert(data.mensaje);

      listarTutoriasPorValidar();

  } catch (err) {
      console.error("Error al validar tutoría:", err);
  }
}
