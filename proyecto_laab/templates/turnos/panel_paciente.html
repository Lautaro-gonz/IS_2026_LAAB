{% extends 'base.html' %}
{% block title %}Mis turnos — laab{% endblock %}
{% block page_title %}Mis turnos{% endblock %}

{% block content %}

<div class="card" style="margin-bottom:18px;">
  <div class="card-header">
    <div class="card-title">
      <i class="fa-solid fa-magnifying-glass" style="margin-right:6px;color:var(--primary)"></i>
      Buscar turnos por DNI
    </div>
  </div>
  <form method="post" style="display:flex;gap:12px;align-items:flex-end;">
    {% csrf_token %}
    <div class="form-group" style="flex:1;">
      <label>Número de DNI</label>
      <input type="text" name="dni" value="{{ dni }}" placeholder="Ej: 30123456"
             pattern="\d{7,8}" title="El DNI debe tener 7 u 8 dígitos" required>
    </div>
    <button type="submit" class="btn btn-primary">
      <i class="fa-solid fa-magnifying-glass"></i> Buscar
    </button>
  </form>
</div>

{% if dni %}
<div class="card">
  <div class="card-header">
    <div>
      <div class="card-title">
        <i class="fa-solid fa-file-medical" style="margin-right:6px;color:var(--primary)"></i>
        Turnos para DNI {{ dni }}
      </div>
      <div class="card-subtitle">{{ turnos|length }} resultado{{ turnos|length|pluralize:"s" }}</div>
    </div>
  </div>

  {% if turnos %}
    {% for t in turnos %}
    <div class="turno-item">
      <div class="turno-time">
        <div class="turno-time-hora">{{ t.hora }}</div>
        <div class="turno-time-fecha">{{ t.fecha }}</div>
      </div>
      <div class="turno-info">
        <div class="turno-paciente">Dr/a. {{ t.medico }}</div>
        <div class="turno-meta">
          <i class="fa-solid fa-heart-pulse" style="margin-right:3px"></i>{{ t.especialidad }}
          &nbsp;·&nbsp;
          <i class="fa-solid fa-clock" style="margin-right:3px"></i>{{ t.duracion }} min
        </div>
      </div>
      <div style="text-align:right;display:flex;flex-direction:column;align-items:flex-end;gap:6px;">
        <span class="badge badge-{{ t.estado }}">{{ t.estado }}</span>
        <div style="font-size:12px;color:var(--success);font-weight:600;">
          Paga: ${{ t.costo.paga_paciente|floatformat:0 }}
        </div>
      </div>
    </div>
    {% endfor %}
  {% else %}
    <div class="empty-state">
      <div class="empty-icon"><i class="fa-solid fa-magnifying-glass"></i></div>
      <p>No se encontraron turnos para el DNI {{ dni }}.</p>
    </div>
  {% endif %}
</div>
{% endif %}

{% endblock %}
