const tableBody = document.querySelector("#tutoriasTable tbody");
const form = document.getElementById("addTutoriaForm");

// Función para listar tutorías
async function listarTutorias() {
  try {
    const res = await fetch("http://127.0.0.1:5000/tutorias");
    const data = await res.json();

    tableBody.innerHTML = "";
    data.forEach(tutoria => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${tutoria.id}</td>
        <td>${tutoria.nombre_tutor}</td>
        <td>${tutoria.curso}</td>
        <td>${tutoria.fecha}</td>
      `;
      tableBody.appendChild(row);
    });
  } catch (err) {
    console.error("Error al cargar tutorías:", err);
  }
}

// Función para agregar tutoría
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const nombre_tutor = document.getElementById("nombre_tutor").value.trim();
  const curso = document.getElementById("curso").value.trim();
  const fecha = document.getElementById("fecha").value;

  try {
    const res = await fetch("http://127.0.0.1:5000/tutorias", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nombre_tutor, curso, fecha })
    });
    const data = await res.json();
    alert(data.mensaje);
    form.reset();
    listarTutorias();
  } catch (err) {
    alert("Error al agregar tutoría");
    console.error(err);
  }
});

// Cargar tutorías al abrir la página
listarTutorias();
