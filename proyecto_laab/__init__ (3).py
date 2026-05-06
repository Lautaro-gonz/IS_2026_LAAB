{% extends 'base.html' %}
{% block title %}Nuevo turno — laab{% endblock %}
{% block page_title %}Nuevo turno{% endblock %}

{% block topbar_actions %}
  <a href="{% url 'turnos:panel_secretaria' %}" class="btn btn-ghost btn-sm">
    <i class="fa-solid fa-arrow-left"></i> Volver
  </a>
{% endblock %}

{% block content %}
<div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;max-width:1100px;">

  <!-- Columna izquierda: datos + médico -->
  <div style="display:flex;flex-direction:column;gap:18px;">

    {% if error %}
      <div class="message error"><i class="fa-solid fa-circle-exclamation"></i> {{ error }}</div>
    {% endif %}

    <form method="post" id="form-turno">
      {% csrf_token %}
      <input type="hidden" name="hora" id="input-hora">

      <!-- Datos del paciente -->
      <div class="card" style="margin-bottom:18px;">
        <div class="section-header" style="margin-bottom:14px;">
          <div class="section-num"><i class="fa-solid fa-user" style="font-size:12px;"></i></div>
          <div>
            <div class="card-title">Datos del paciente</div>
            <div class="card-subtitle">Campos obligatorios marcados con *</div>
          </div>
        </div>
        <div class="divider" style="margin-bottom:16px;"></div>
        <div class="form-grid">
          <div class="form-group">
            <label>Nombre completo *</label>
            <input type="text" name="nombre" placeholder="Ej: Juan Pérez" required>
          </div>
          <div class="form-group">
            <label>DNI *</label>
            <input type="text" name="dni" placeholder="Ej: 30123456" required
                   pattern="\d{7,8}" title="7 u 8 dígitos numéricos">
          </div>
          <div class="form-group">
            <label>Teléfono</label>
            <input type="text" name="telefono" placeholder="Ej: 3764123456"
                   pattern="\d{7,15}" title="Solo números">
          </div>
          <div class="form-group">
            <label>Email</label>
            <input type="email" name="email" placeholder="Ej: juan@mail.com">
          </div>
          <div class="form-group full">
            <label>Obra social</label>
            <select name="obra_social">
              <option value="">Sin obra social — paga 100% ($10.000)</option>
              {% for obra in obras_sociales %}
                <option value="{{ obra }}">{{ obra }}</option>
              {% endfor %}
            </select>
          </div>
        </div>
      </div>

      <!-- Selección de médico -->
      <div class="card">
        <div class="section-header" style="margin-bottom:14px;">
          <div class="section-num" style="background:linear-gradient(135deg,#059669,#10b981);">
            <i class="fa-solid fa-stethoscope" style="font-size:12px;"></i>
          </div>
          <div>
            <div class="card-title">Seleccioná el médico</div>
            <div class="card-subtitle">El calendario mostrará su disponibilidad</div>
          </div>
        </div>
        <div class="divider" style="margin-bottom:16px;"></div>

        <!-- Lista de médicos como cards clickeables -->
        <div id="lista-medicos" style="display:flex;flex-direction:column;gap:8px;">
          {% for idx, nombre in medicos %}
          <div class="medico-card" data-idx="{{ idx }}" onclick="seleccionarMedico({{ idx }}, '{{ nombre }}')">
            <div class="medico-avatar">{{ nombre|slice:":2"|upper }}</div>
            <div class="medico-info">
              <div class="medico-nombre">{{ nombre }}</div>
            </div>
            <i class="fa-solid fa-chevron-right medico-arrow"></i>
          </div>
          {% endfor %}
        </div>
        <input type="hidden" name="medico" id="input-medico">
        <input type="hidden" name="fecha"  id="input-fecha">
      </div>

      <!-- Botón submit (oculto hasta que se complete la selección) -->
      <div id="btn-confirmar" style="display:none;margin-top:16px;">
        <div class="card" style="background:var(--primary-soft);border-color:#bfdbfe;">
          <div style="display:flex;align-items:center;justify-content:space-between;">
            <div>
              <div style="font-weight:700;color:var(--primary);font-size:14px;">Turno listo para confirmar</div>
              <div id="resumen-turno" style="font-size:12px;color:var(--text-muted);margin-top:3px;"></div>
            </div>
            <button type="submit" class="btn btn-primary">
              <i class="fa-solid fa-calendar-plus"></i> Confirmar turno
            </button>
          </div>
        </div>
      </div>

    </form>
  </div>

  <!-- Columna derecha: calendario + slots -->
  <div style="display:flex;flex-direction:column;gap:18px;">

    <!-- Placeholder inicial -->
    <div class="card" id="card-placeholder" style="text-align:center;padding:48px 24px;">
      <div style="width:64px;height:64px;border-radius:50%;background:var(--primary-soft);display:flex;align-items:center;justify-content:center;margin:0 auto 16px;font-size:28px;color:var(--primary);">
        <i class="fa-solid fa-calendar-days"></i>
      </div>
      <div style="font-size:15px;font-weight:600;color:var(--text-soft);">Seleccioná un médico</div>
      <div style="font-size:13px;color:var(--text-muted);margin-top:6px;">El calendario mostrará los días disponibles</div>
    </div>

    <!-- Calendario (oculto hasta elegir médico) -->
    <div class="card" id="card-calendario" style="display:none;">
      <div class="card-header" style="margin-bottom:16px;">
        <div>
          <div class="card-title" id="cal-medico-nombre"></div>
          <div class="card-subtitle" id="cal-horario"></div>
        </div>
        <div style="display:flex;gap:6px;align-items:center;">
          <button class="btn btn-ghost btn-sm" onclick="cambiarMes(-1)"><i class="fa-solid fa-chevron-left"></i></button>
          <span id="cal-titulo" style="font-size:13px;font-weight:600;min-width:110px;text-align:center;"></span>
          <button class="btn btn-ghost btn-sm" onclick="cambiarMes(1)"><i class="fa-solid fa-chevron-right"></i></button>
        </div>
      </div>

      <!-- Leyenda -->
      <div style="display:flex;gap:12px;margin-bottom:14px;flex-wrap:wrap;">
        <div style="display:flex;align-items:center;gap:5px;font-size:11.5px;color:var(--text-muted);">
          <div style="width:12px;height:12px;border-radius:3px;background:#dcfce7;border:1px solid #86efac;"></div> Disponible
        </div>
        <div style="display:flex;align-items:center;gap:5px;font-size:11.5px;color:var(--text-muted);">
          <div style="width:12px;height:12px;border-radius:3px;background:#fef3c7;border:1px solid #fbbf24;"></div> Con turnos
        </div>
        <div style="display:flex;align-items:center;gap:5px;font-size:11.5px;color:var(--text-muted);">
          <div style="width:12px;height:12px;border-radius:3px;background:#fee2e2;border:1px solid #fca5a5;"></div> Sin lugar
        </div>
        <div style="display:flex;align-items:center;gap:5px;font-size:11.5px;color:var(--text-muted);">
          <div style="width:12px;height:12px;border-radius:3px;background:#f1f5f9;border:1px solid #e2e8f0;"></div> No atiende
        </div>
      </div>

      <!-- Grid calendario -->
      <div id="cal-grid" style="display:grid;grid-template-columns:repeat(7,1fr);gap:4px;text-align:center;">
        <!-- Se genera con JS -->
      </div>
    </div>

    <!-- Slots de horario (oculto hasta elegir día) -->
    <div class="card" id="card-slots" style="display:none;">
      <div class="card-header" style="margin-bottom:14px;">
        <div>
          <div class="card-title"><i class="fa-solid fa-clock" style="margin-right:6px;color:var(--primary);"></i>Horarios disponibles</div>
          <div class="card-subtitle" id="slots-fecha-label"></div>
        </div>
        <button class="btn btn-ghost btn-sm" onclick="limpiarFecha()">
          <i class="fa-solid fa-rotate-left"></i> Cambiar día
        </button>
      </div>
      <div id="slots-grid" style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;">
        <!-- Se genera con JS -->
      </div>
    </div>

  </div>
</div>

<style>
.medico-card{
  display:flex;align-items:center;gap:12px;
  padding:12px 14px;border-radius:10px;
  border:1.5px solid var(--border);cursor:pointer;
  transition:all .18s;background:var(--surface);
}
.medico-card:hover{border-color:var(--primary);background:var(--primary-soft);}
.medico-card.selected{border-color:var(--primary);background:var(--primary-soft);box-shadow:0 0 0 3px rgba(26,86,219,.1);}
.medico-avatar{
  width:38px;height:38px;border-radius:50%;
  background:var(--primary-grad);color:#fff;
  display:flex;align-items:center;justify-content:center;
  font-size:13px;font-weight:700;flex-shrink:0;
}
.medico-nombre{font-size:13.5px;font-weight:600;color:var(--text)}
.medico-arrow{color:var(--text-muted);font-size:12px;margin-left:auto;}
.medico-card.selected .medico-arrow{color:var(--primary);}

.cal-header-dia{font-size:11px;font-weight:700;color:var(--text-muted);padding:4px 0;text-transform:uppercase;letter-spacing:.05em;}
.cal-dia{
  aspect-ratio:1;display:flex;align-items:center;justify-content:center;
  border-radius:8px;font-size:13px;font-weight:500;
  border:1.5px solid transparent;transition:all .15s;
}
.cal-dia.pasado{color:var(--text-muted);cursor:default;background:#f8fafc;}
.cal-dia.no_atiende{color:#cbd5e1;cursor:default;background:#f1f5f9;}
.cal-dia.disponible{
  background:#dcfce7;color:#166534;border-color:#86efac;
  cursor:pointer;font-weight:700;
}
.cal-dia.disponible:hover{background:#16a34a;color:#fff;border-color:#16a34a;transform:scale(1.08);}
.cal-dia.parcial{
  background:#fef3c7;color:#92400e;border-color:#fbbf24;
  cursor:pointer;font-weight:700;
}
.cal-dia.parcial:hover{background:#f59e0b;color:#fff;border-color:#f59e0b;transform:scale(1.08);}
.cal-dia.lleno{background:#fee2e2;color:#991b1b;cursor:not-allowed;border-color:#fca5a5;}
.cal-dia.hoy{outline:2px solid var(--primary);outline-offset:1px;}
.cal-dia.seleccionado{background:var(--primary)!important;color:#fff!important;border-color:var(--primary)!important;}

.slot-btn{
  padding:10px 6px;border-radius:8px;border:1.5px solid var(--border);
  background:var(--surface);color:var(--text);font-size:13px;font-weight:600;
  cursor:pointer;transition:all .15s;font-family:'JetBrains Mono',monospace;
  text-align:center;
}
.slot-btn:hover{border-color:var(--primary);background:var(--primary-soft);color:var(--primary);}
.slot-btn.selected{background:var(--primary);color:#fff;border-color:var(--primary);}
</style>

<script>
const MESES = ['Enero','Febrero','Marzo','Abril','Mayo','Junio','Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre'];
const DIAS  = ['Lu','Ma','Mi','Ju','Vi','Sá','Do'];

let medicoIdx    = null;
let medicoNombre = '';
let calAnio      = new Date().getFullYear();
let calMes       = new Date().getMonth() + 1;
let fechaSel     = null;
let horaSel      = null;
let disponMes    = {};

function seleccionarMedico(idx, nombre) {
  medicoIdx    = idx;
  medicoNombre = nombre;

  document.querySelectorAll('.medico-card').forEach(c => c.classList.remove('selected'));
  document.querySelector(`.medico-card[data-idx="${idx}"]`).classList.add('selected');
  document.getElementById('input-medico').value = idx;

  document.getElementById('card-placeholder').style.display = 'none';
  document.getElementById('card-calendario').style.display  = 'block';
  document.getElementById('cal-medico-nombre').textContent  = nombre;

  limpiarFecha();
  cargarMes();
}

function cargarMes() {
  document.getElementById('cal-titulo').textContent = `${MESES[calMes-1]} ${calAnio}`;

  fetch(`/turnos/api/disponibilidad-mes/?medico=${medicoIdx}&anio=${calAnio}&mes=${calMes}`)
    .then(r => r.json())
    .then(data => {
      disponMes = data;
      renderCalendario();
    });
}

function cambiarMes(delta) {
  calMes += delta;
  if (calMes > 12) { calMes = 1;  calAnio++; }
  if (calMes < 1)  { calMes = 12; calAnio--; }
  limpiarFecha();
  cargarMes();
}

function renderCalendario() {
  const grid = document.getElementById('cal-grid');
  grid.innerHTML = '';

  DIAS.forEach(d => {
    const h = document.createElement('div');
    h.className = 'cal-header-dia';
    h.textContent = d;
    grid.appendChild(h);
  });

  const primerDia = new Date(calAnio, calMes - 1, 1).getDay();
  const offset    = (primerDia === 0) ? 6 : primerDia - 1;

  for (let i = 0; i < offset; i++) {
    grid.appendChild(document.createElement('div'));
  }

  const hoyStr = new Date().toISOString().slice(0,10);

  for (const [dia, estado] of Object.entries(disponMes)) {
    const d   = document.createElement('div');
    const mes = String(calMes).padStart(2,'0');
    const dStr= `${calAnio}-${mes}-${String(dia).padStart(2,'0')}`;

    d.className = `cal-dia ${estado}`;
    d.textContent = dia;
    if (dStr === hoyStr) d.classList.add('hoy');
    if (dStr === fechaSel) d.classList.add('seleccionado');

    if (estado === 'disponible' || estado === 'parcial') {
      d.onclick = () => seleccionarFecha(dStr, parseInt(dia));
    }
    grid.appendChild(d);
  }
}

function seleccionarFecha(fechaStr, dia) {
  fechaSel = fechaStr;
  document.getElementById('input-fecha').value = fechaStr;

  renderCalendario();

  const label = new Date(fechaStr + 'T12:00:00').toLocaleDateString('es-AR',
    {weekday:'long', year:'numeric', month:'long', day:'numeric'});
  document.getElementById('slots-fecha-label').textContent = label;
  document.getElementById('card-slots').style.display = 'block';

  cargarSlots(fechaStr);
  limpiarHora();
}

function cargarSlots(fechaStr) {
  const grid = document.getElementById('slots-grid');
  grid.innerHTML = '<div style="grid-column:1/-1;text-align:center;padding:20px;color:var(--text-muted)"><i class="fa-solid fa-spinner fa-spin"></i> Cargando horarios...</div>';

  fetch(`/turnos/api/disponibilidad-dia/?medico=${medicoIdx}&fecha=${fechaStr}`)
    .then(r => r.json())
    .then(data => {
      grid.innerHTML = '';

      if (data.horario) {
        document.getElementById('cal-horario').textContent = `Atiende ${data.horario}`;
      }

      if (!data.disponible || !data.slots || data.slots.length === 0) {
        grid.innerHTML = `<div style="grid-column:1/-1;text-align:center;padding:20px;color:var(--text-muted);">
          <i class="fa-solid fa-calendar-xmark" style="font-size:24px;margin-bottom:8px;display:block;"></i>
          Sin horarios disponibles</div>`;
        return;
      }

      data.slots.forEach(slot => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'slot-btn';
        btn.textContent = slot;
        btn.onclick = () => seleccionarHora(slot, btn);
        grid.appendChild(btn);
      });
    });
}

function seleccionarHora(hora, btn) {
  horaSel = hora;
  document.getElementById('input-hora').value = hora;

  document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');

  const fechaLabel = new Date(fechaSel + 'T12:00:00').toLocaleDateString('es-AR',
    {weekday:'long', day:'numeric', month:'long'});
  document.getElementById('resumen-turno').textContent =
    `${medicoNombre} · ${fechaLabel} a las ${hora}`;
  document.getElementById('btn-confirmar').style.display = 'block';
}

function limpiarFecha() {
  fechaSel = null;
  horaSel  = null;
  document.getElementById('input-fecha').value = '';
  document.getElementById('input-hora').value  = '';
  document.getElementById('card-slots').style.display  = 'none';
  document.getElementById('btn-confirmar').style.display = 'none';
}

function limpiarHora() {
  horaSel = null;
  document.getElementById('input-hora').value = '';
  document.getElementById('btn-confirmar').style.display = 'none';
}
</script>
{% endblock %}
