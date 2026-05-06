{% extends 'base.html' %}
{% block title %}Mi agenda — laab{% endblock %}
{% block page_title %}Mi agenda{% endblock %}

{% block content %}

<div class="card" style="margin-bottom:18px;">
  <form method="get" class="filters">
    <div class="form-group">
      <label><i class="fa-solid fa-filter" style="margin-right:4px"></i>Filtrar por fecha</label>
      <input type="date" name="fecha" value="{{ fecha_filtro }}">
    </div>
    <button type="submit" class="btn btn-ghost">
      <i class="fa-solid fa-magnifying-glass"></i> Filtrar
    </button>
    <a href="{% url 'turnos:panel_doctor' %}" class="btn btn-ghost">
      <i class="fa-solid fa-rotate-left"></i> Ver todos
    </a>
  </form>
</div>

<div class="card">
  <div class="card-header">
    <div>
      <div class="card-title">
        <i class="fa-solid fa-stethoscope" style="margin-right:6px;color:var(--primary)"></i>
        Mis turnos{% if fecha_filtro %} — {{ fecha_filtro }}{% endif %}
      </div>
      <div class="card-subtitle">Dr/a. {{ doctor }}</div>
    </div>
    <span style="font-size:13px;color:var(--text-muted);">{{ turnos|length }} turno{{ turnos|length|pluralize:"s" }}</span>
  </div>

  {% if turnos %}
    {% for t in turnos %}
    <div class="turno-item">
      <div class="turno-time">
        <div class="turno-time-hora">{{ t.hora }}</div>
        <div class="turno-time-fecha">{{ t.fecha }}</div>
      </div>
      <div class="turno-info">
        <div class="turno-paciente">{{ t.paciente }}</div>
        <div class="turno-meta">
          <i class="fa-solid fa-id-card" style="margin-right:3px"></i>DNI {{ t.dni }}
          &nbsp;·&nbsp;
          <i class="fa-solid fa-clock" style="margin-right:3px"></i>{{ t.duracion }} min
          &nbsp;·&nbsp; {{ t.costo.detalle }}
        </div>
      </div>
      <div style="text-align:right;display:flex;flex-direction:column;align-items:flex-end;gap:6px;">
        <span class="badge badge-{{ t.estado }}">{{ t.estado }}</span>
        <a href="{% url 'turnos:detalle_turno' t.id %}" class="btn btn-ghost btn-sm">
          <i class="fa-solid fa-eye"></i> Ver detalle
        </a>
      </div>
    </div>
    {% endfor %}
  {% else %}
    <div class="empty-state">
      <div class="empty-icon"><i class="fa-solid fa-calendar-days"></i></div>
      <p>No tenés turnos{% if fecha_filtro %} para esa fecha{% endif %}.</p>
    </div>
  {% endif %}
</div>
{% endblock %}
