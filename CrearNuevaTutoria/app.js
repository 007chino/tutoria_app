(async function(){
  // ====== CONFIGURACIÓN ======
  const API_URL = "http://127.0.0.1:8000"; // cambia si tu backend corre en otra URL/puerto

  const HOUR_START = 7;    // 07:00
  const HOUR_END   = 21;   // 21:00

  // Altura de una hora según CSS (se recalcula cuando se necesita)
  function getHourHeight(){
    const v = parseInt(
      getComputedStyle(document.documentElement)
        .getPropertyValue('--hour-height')
    );
    return Number.isFinite(v) && v > 0 ? v : 64;
  }

  // ====== ESTADO (ahora desde backend) ======
  let tutors = [];   // {id, nombre, carrera}
  let rooms  = [];   // {id, name}
  let events = [];   // sesiones de la semana: {id, tutorId, date, start, end, ambiente, roomId, notes}

  let selectedTutorId = null;
  let weekStart = mondayOf(new Date());

  // ====== DOM refs ======
  const tutorListEl   = document.getElementById('tutorList');
  const searchEl      = document.getElementById('search');
  const filterCarrera = document.getElementById('filterCarrera');
  const selectedPill  = document.getElementById('selectedTutor');

  const monthLabelEl  = document.getElementById('monthLabel');
  const daysHeaderEl  = document.getElementById('daysHeader');
  const hoursEl       = document.getElementById('hours');
  const columnsEl     = document.getElementById('columns');
  const nowLineEl     = document.getElementById('nowLine');

  const dateInput = document.getElementById('dateInput');
  const timeInput = document.getElementById('timeInput');
  const roomInput = document.getElementById('roomInput');
  const saveBtn   = document.getElementById('saveBtn');
  const msgEl     = document.getElementById('msg');

  // ====== LISTENERS ======
  document.getElementById('prevWeek').addEventListener('click', ()=>{
    weekStart = addDays(weekStart, -7);
    renderWeek();
  });
  document.getElementById('nextWeek').addEventListener('click', ()=>{
    weekStart = addDays(weekStart, 7);
    renderWeek();
  });
  document.getElementById('todayBtn').addEventListener('click', ()=>{
    weekStart = mondayOf(new Date());
    renderWeek();
  });
  searchEl.addEventListener('input', renderTutorList);
  filterCarrera.addEventListener('change', renderTutorList);
  saveBtn.addEventListener('click', onSave);

  window.addEventListener('resize', ()=>{
    renderWeek();
  });

  // ====== INICIALIZACIÓN (frontend + backend) ======
  await init();

  async function init(){
    try{
      await loadTutors();
      await loadRooms();
      buildFilterOptions();
      renderTutorList();
      buildHours();
      renderWeek();  // esto internamente pedirá las sesiones al backend
    }catch(err){
      console.error(err);
      flashMessage("Error al inicializar la aplicación (no se pudo conectar a la API).", "err");
    }
  }

  // ============================
  //   CARGA DESDE BACKEND
  // ============================

  async function loadTutors(){
    const res = await fetch(`${API_URL}/tutors`);
    if(!res.ok) throw new Error("No se pudieron cargar los tutores");
    const data = await res.json();
    // mapeamos al formato que usa el front
    tutors = data.map(t => ({
      id: t.id,
      nombre: t.full_name,
      carrera: t.career_name
    }));
    tutors.sort((a,b)=> a.nombre.localeCompare(b.nombre, 'es', {sensitivity:'base'}));
  }

  async function loadRooms(){
    const res = await fetch(`${API_URL}/rooms`);
    if(!res.ok) throw new Error("No se pudieron cargar los ambientes");
    rooms = await res.json(); // {id, name}
  }

  async function fetchWeekSessions(){
    try{
      const startIso = isoDate(weekStart);
      const res = await fetch(`${API_URL}/sessions/week?start=${startIso}`);
      if(!res.ok) throw new Error("No se pudieron cargar las sesiones de la semana");
      const data = await res.json();

      events = data.map(s => ({
        id: s.id,
        tutorId: s.tutor_id,
        date: s.date,             // "YYYY-MM-DD"
        start: s.start_time,      // "HH:MM"
        end: s.end_time,          // "HH:MM"
        ambiente: s.room_name,    // nombre del ambiente
        roomId: s.room_id,
        notes: s.notes
      }));

      renderEventsOnWeek();
    }catch(err){
      console.error(err);
      flashMessage("Error al cargar las tutorías de la semana.", "err");
    }
  }

  // ============================
  //   UI: CARRERAS / TUTORES
  // ============================

  function buildFilterOptions(){
    // Limpiar por si se recarga
    while(filterCarrera.options.length > 1){
      filterCarrera.remove(1);
    }
    const carreras = Array.from(new Set(tutors.map(t=>t.carrera)));
    carreras.sort((a,b)=> a.localeCompare(b, 'es', {sensitivity:'base'}));
    for(const c of carreras){
      const opt = document.createElement('option');
      opt.value = c; opt.textContent = c;
      filterCarrera.appendChild(opt);
    }
  }

  function renderTutorList(){
    const q = strip(searchEl.value).toLowerCase();
    const filter = filterCarrera.value;
    tutorListEl.innerHTML = '';
    tutors
      .filter(t => (filter==='*' || t.carrera===filter))
      .filter(t => strip(t.nombre).toLowerCase().includes(q))
      .forEach(t=>{
        const li = document.createElement('li');
        li.className = 'tutor' + (t.id===selectedTutorId?' selected':'');
        li.innerHTML = `
          <div class="avatar">${inic(t.nombre)}</div>
          <div>
            <div class="name">${t.nombre}</div>
            <div class="meta">${t.carrera}</div>
          </div>
        `;
        li.addEventListener('click', ()=>{
          selectedTutorId = t.id;
          selectedPill.textContent = `Tutor: ${t.nombre}`;
          renderTutorList();
          // No hace falta recargar semana, solo repintar eventos para marcar el seleccionado
          renderEventsOnWeek();
        });
        tutorListEl.appendChild(li);
      });
  }

  // ============================
  //   UI: CALENDARIO
  // ============================

  function buildHours(){
    hoursEl.innerHTML = '';
    for(let h=HOUR_START; h<HOUR_END; h++){
      const div = document.createElement('div');
      div.className = 'hour';
      div.textContent = `${pad(h)}:00`;
      hoursEl.appendChild(div);
    }
  }

  function renderWeek(){
    const hourHeight = getHourHeight();

    // Encabezado de días
    daysHeaderEl.innerHTML = '<div class="hours-label-cell"></div>'; // columna de horas vacía
    for(let i=0;i<7;i++){
      const d = addDays(weekStart, i);
      const cell = document.createElement('div');
      cell.className = 'day';
      const abbr = ["LU","MA","MI","JU","VI","SA","DO"][i];
      cell.innerHTML = `${abbr}<span class="n">${d.getDate()}</span>`;
      daysHeaderEl.appendChild(cell);
    }
    monthLabelEl.textContent = monthLabelOf(weekStart);

    // Columnas
    columnsEl.innerHTML = '';
    for(let i=0;i<7;i++){
      const d = addDays(weekStart,i);
      const col = document.createElement('div');
      col.className = 'day-col';
      col.dataset.date = isoDate(d);
      col.style.height = `${(HOUR_END - HOUR_START) * hourHeight}px`;

      // Click para autocompletar fecha y hora
      col.addEventListener('click', (ev)=>{
        const rect = col.getBoundingClientRect();
        const y = ev.clientY - rect.top + col.scrollTop;
        const totalMins = (HOUR_END - HOUR_START) * 60;
        const mins = Math.max(
          0,
          Math.min(
            totalMins - 30,
            Math.round(y / hourHeight * 60 / 30) * 30
          )
        );
        const t = timeFromMinutes(mins);
        dateInput.value = col.dataset.date;
        timeInput.value = t;
        flashMessage(`Fecha y hora sugeridas: ${col.dataset.date} ${t}`, 'ok');
      });

      columnsEl.appendChild(col);
    }

    // Línea de "ahora"
    const now = new Date();
    const isInWeek = now >= weekStart && now < addDays(weekStart,7);
    if(isInWeek){
      const dayIdx = (now.getDay()+6)%7;
      const mins = (now.getHours()-HOUR_START)*60 + now.getMinutes();
      const y = mins * (hourHeight/60);
      nowLineEl.style.display='block';
      nowLineEl.style.top = `${y+6}px`;
      nowLineEl.style.left = `calc((100% / 7) * ${dayIdx})`;
      nowLineEl.style.width = `calc((100% / 7) - var(--col-gap))`;
    }else{
      nowLineEl.style.display='none';
    }

    // Pedimos al backend las sesiones de esta semana y luego pintamos
    fetchWeekSessions();
  }

  function renderEventsOnWeek(){
    const hourHeight = getHourHeight();

    // Limpiar eventos
    document.querySelectorAll('.day-col').forEach(col => col.innerHTML = '');

    const startIso = isoDate(weekStart);
    const endIso   = isoDate(addDays(weekStart,7));

    const toShow = events.filter(ev => ev.date >= startIso && ev.date < endIso);

    // Agrupar por fecha
    const byDate = {};
    for(const ev of toShow){
      (byDate[ev.date] ??= []).push(ev);
    }

    // Pintar
    document.querySelectorAll('.day-col').forEach(col=>{
      const date = col.dataset.date;
      const list = byDate[date] || [];
      for(const ev of list){
        const y = minutesSinceStart(ev.start) * (hourHeight/60);
        const endM = minutesSinceStart(ev.end);
        const startM = minutesSinceStart(ev.start);
        const h = Math.max(22, (endM - startM) * (hourHeight/60));
        const div = document.createElement('div');
        div.className = 'event';
        if(selectedTutorId && ev.tutorId === selectedTutorId) div.classList.add('selected-tutor');

        const tutor = tutors.find(t=>t.id===ev.tutorId);
        const who = tutor ? tutor.nombre : `Tutor ${ev.tutorId}`;
        div.style.top = `${y+6}px`;
        div.style.height = `${h-8}px`;

        div.innerHTML = `
          <div class="title">${ev.ambiente}</div>
          <div class="small">${ev.start}–${ev.end} · ${who}</div>
        `;

        col.appendChild(div);
      }
    });
  }

  // ============================
  //   GUARDAR NUEVA TUTORÍA
  // ============================

  async function onSave(){
    clearMessage();
    const tutorId = selectedTutorId;
    const date = dateInput.value;
    const start = timeInput.value;
    const ambiente = roomInput.value.trim();

    if(!tutorId){ return flashMessage("Selecciona un tutor.", 'err'); }
    if(!date){ return flashMessage("Indica la fecha.", 'err'); }
    if(!start){ return flashMessage("Indica la hora de inicio.", 'err'); }
    if(!ambiente){ return flashMessage("Indica el ambiente.", 'err'); }

    // Buscar el ambiente en la lista de rooms del backend
    const room = rooms.find(r => r.name.toLowerCase() === ambiente.toLowerCase());
    if(!room){
      return flashMessage("Ambiente no encontrado. Escribe el nombre tal como está registrado.", "err");
    }

    const end = calcEnd(start, 60); // duración por defecto = 60 min

    // En vez de guardar en localStorage, enviamos al backend
    const payload = {
      tutor_id: tutorId,
      room_id: room.id,
      date: date,
      start_time: start,
      end_time: end,
      notes: null
    };

    saveBtn.disabled = true;
    try{
      const res = await fetch(`${API_URL}/sessions`, {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify(payload)
      });

      let body = null;
      try { body = await res.json(); } catch(_){}

      if(!res.ok){
        const detail = body && body.detail ? body.detail : "Error al guardar la tutoría.";
        return flashMessage(detail, "err");
      }

      flashMessage("¡Tutoría guardada!", "ok");
      // Recargamos las sesiones de la semana desde el backend
      fetchWeekSessions();
      // Opcional: limpiar campo de ambiente
      // roomInput.value = "";
    }catch(err){
      console.error(err);
      flashMessage("Error de conexión con el servidor.", "err");
    }finally{
      saveBtn.disabled = false;
    }
  }

  // ============================
  //   UTILIDADES TIEMPO/FECHA
  // ============================

  function mondayOf(d){
    const x = new Date(d.getFullYear(), d.getMonth(), d.getDate());
    const day = (x.getDay() + 6) % 7; // 0 = lunes
    x.setDate(x.getDate() - day);
    x.setHours(0,0,0,0);
    return x;
  }
  function isoDate(d){ return d.toISOString().slice(0,10); }
  function addDays(d, n){ const x = new Date(d); x.setDate(x.getDate()+n); return x; }
  function pad(n){ return n.toString().padStart(2,'0'); }
  function minutesSinceStart(timeStr){
    const [hh,mm] = timeStr.split(":").map(Number);
    return (hh - HOUR_START) * 60 + mm;
  }
  function timeFromMinutes(mins){
    const h = Math.floor(mins/60) + HOUR_START;
    const m = mins%60;
    return `${pad(h)}:${pad(m)}`;
  }
  function monthLabelOf(d){
    return new Intl.DateTimeFormat('es-PE',{month:'long', year:'numeric'}).format(d);
  }
  function calcEnd(start, minutes=60){
    const [hh,mm] = start.split(":").map(Number);
    const dt = new Date(2000,0,1,hh,mm);
    dt.setMinutes(dt.getMinutes()+minutes);
    return `${pad(dt.getHours())}:${pad(dt.getMinutes())}`;
  }

  // ============================
  //   HELPERS
  // ============================

  function strip(s){
    return (s||"").normalize("NFD").replace(/\p{Diacritic}/gu,'');
  }
  function inic(nombre){
    const parts = nombre.trim().split(/\s+/);
    const a = parts[0]?.[0]||'?';
    const b = parts[1]?.[0]||'';
    return (a+b).toUpperCase();
  }
  function clearMessage(){
    msgEl.textContent='';
    msgEl.className='msg';
  }
  function flashMessage(text, kind='ok'){
    msgEl.textContent = text;
    msgEl.className = 'msg ' + (kind==='ok'?'ok':'err');
    setTimeout(()=>{
      if(msgEl.textContent===text) clearMessage();
    }, 4000);
  }

})();
