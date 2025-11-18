// proyec_horario.js

// ----- Tabs + navegación tipo “pantalla” con hash -----
const tabEls = document.querySelectorAll('.tab');
const screens = {
  general: document.getElementById('screen-general'),
  tutores: document.getElementById('screen-tutores'),
  estudiantes: document.getElementById('screen-estudiantes'),
  reportes: document.getElementById('screen-reportes'),
};

function activateRoute(route){
  if(!route) route = 'general';

  // tabs
  tabEls.forEach(t => {
    const active = t.dataset.route === route;
    t.classList.toggle('is-active', active);
    t.setAttribute('aria-selected', active ? 'true' : 'false');
  });

  // pantallas
  Object.entries(screens).forEach(([key,el])=>{
    el.classList.toggle('active', key === route);
  });

  // actualizar hash sin saltar
  if(location.hash.replace('#','') !== route){
    history.replaceState(null,'', `#${route}`);
  }

  // limpiar búsqueda y scroll top
  document.getElementById('q').value = '';
  const active = screens[route];
  active.scrollTop = 0;
}

// clic en tabs
tabEls.forEach(t => t.addEventListener('click', () => activateRoute(t.dataset.route)));

// al cargar/refrescar, usar el hash si existe
window.addEventListener('DOMContentLoaded', () => {
  const initial = (location.hash || '#general').replace('#','');
  activateRoute(initial);
});

// si el usuario cambia el hash manualmente
window.addEventListener('hashchange', () => activateRoute(location.hash.replace('#','')));

// ---- Búsqueda simple por pantalla
const q = document.getElementById('q');
q.addEventListener('input', () => {
  const text = q.value.toLowerCase();
  const currentKey = (location.hash || '#general').replace('#','');
  const active = screens[currentKey] || screens.general;
  active.querySelectorAll('.card, tbody .tr').forEach(el => {
    const content = el.innerText.toLowerCase();
    el.style.display = content.includes(text) ? '' : 'none';
  });
});

// ---- General: demo agregar semana
document.getElementById('addWeek')?.addEventListener('click', () => {
  const list = document.querySelector('#screen-general .list');
  const count = list.querySelectorAll('.card').length + 1;
  const el = document.createElement('article');
  el.className = 'card';
  el.innerHTML = `
    <span class="bullet" aria-hidden="true"></span>
    <div>
      <div class="title">Semana ${count}: Nueva actividad</div>
      <div class="subtitle">Describe brevemente las acciones de esta semana.</div>
    </div>
    <div class="actions">
      <button class="chip chip--ghost">Ver</button>
      <button class="chip" data-action="edit">Editar</button>
      <button class="chip chip--danger" data-action="delete">Eliminar</button>
    </div>`;
  list.appendChild(el);
});

// ---- Tutores: demo “Asignar 1”
document.querySelectorAll('#tabla-tutores .asignar').forEach(btn => {
  btn.addEventListener('click', () => {
    const row = btn.closest('tr');
    const asignados = row.querySelector('.asignados');
    const disponibles = row.querySelector('.disponibles');
    let a = parseInt(asignados.textContent,10);
    let d = parseInt(disponibles.textContent,10);
    if (d <= 0) return;
    asignados.textContent = ++a;
    disponibles.textContent = --d;
    if (d === 0){
      btn.textContent = 'Lleno';
      btn.classList.add('chip--danger');
      btn.disabled = true;
    }
  });
});

// ---- Reportes: demo generar historial
document.getElementById('btn-descargar')?.addEventListener('click', () => {
  const tipo = document.getElementById('tipo-reporte').value;
  const tbody = document.getElementById('historial-reportes');
  const tr = document.createElement('tr');
  tr.className = 'tr';
  const hoy = new Date().toISOString().slice(0,10);
  tr.innerHTML = `
    <td class="td">${hoy}</td>
    <td class="td">${tipo.charAt(0).toUpperCase()+tipo.slice(1)}</td>
    <td class="td">you@unsaac.edu</td>
    <td class="td"><button class="chip chip--ghost">Abrir</button></td>`;
  tbody.prepend(tr);
  alert('Reporte generado (demo).');
});

// ---- Sidebar: marcar semestre activo (visual)
document.querySelectorAll('.semester').forEach(s => {
  s.addEventListener('click', e => {
    e.preventDefault();
    document.querySelectorAll('.semester').forEach(x => x.classList.remove('is-active'));
    s.classList.add('is-active');
  });
});

// ======= Editar y Eliminar semana =======
const screensRoot = document.getElementById('screens');
screensRoot.addEventListener('click', (e) => {
  // ---- Eliminar semana ----
  const delBtn = e.target.closest('[data-action="delete"]');
  if (delBtn) {
    const card = delBtn.closest('.card');
    if (!card) return;
    const titleEl = card.querySelector('.title');
    const title = titleEl ? titleEl.textContent.trim() : 'esta semana';
    const ok = confirm(`¿Deseas eliminar ${title}?`);
    if (ok) {
      card.style.transition = 'opacity .25s ease, transform .25s ease';
      card.style.opacity = '0';
      card.style.transform = 'translateX(-10px)';
      setTimeout(() => card.remove(), 250);
    }
    return; // no seguir con editar
  }

  // ---- Editar nombre de semana ----
  const editBtn = e.target.closest('[data-action="edit"]');
  if (editBtn) {
    const card = editBtn.closest('.card');
    const titleEl = card.querySelector('.title');
    if (!titleEl) return;

    const full = titleEl.textContent.trim();
    const match = full.match(/^(Semana\s+\d+:\s*)(.*)$/i);
    const prefix = match ? match[1] : '';
    const currentName = match ? match[2] : full;

    // input + botones inline
    const input = document.createElement('input');
    input.type = 'text';
    input.value = currentName;
    input.style.width = '100%';
    input.style.font = 'inherit';
    input.style.padding = '6px 8px';
    input.style.border = '1px solid #ececf7';
    input.style.borderRadius = '8px';
    input.style.background = 'var(--surface)';

    const bar = document.createElement('div');
    bar.style.marginTop = '8px';
    const save = document.createElement('button');
    save.textContent = 'Guardar';
    save.className = 'chip';
    const cancel = document.createElement('button');
    cancel.textContent = 'Cancelar';
    cancel.className = 'chip chip--ghost';
    bar.append(save, ' ', cancel);

    const oldHTML = titleEl.innerHTML;
    titleEl.innerHTML = '';
    titleEl.append(input, bar);
    input.focus();
    input.select();

    const commit = () => {
      const newName = input.value.trim() || currentName;
      titleEl.innerHTML = `${prefix}${escapeHtml(newName)}`;
    };
    const rollback = () => {
      titleEl.innerHTML = oldHTML;
    };

    save.addEventListener('click', commit);
    cancel.addEventListener('click', rollback);
    input.addEventListener('keydown', (ev) => {
      if (ev.key === 'Enter') { ev.preventDefault(); commit(); }
      if (ev.key === 'Escape') { ev.preventDefault(); rollback(); }
    });
  }
});

// Utilidad para evitar inyección HTML
function escapeHtml(str){
  return str.replace(/[&<>"']/g, s => ({
    '&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'
  }[s]));
}
