<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{% block title %}laab · Turnos{% endblock %}</title>
  {% load static %}
  <link rel="stylesheet" href="{% static 'css/style.css' %}">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
  <!-- anti-flash: aplica variables CSS directamente antes de pintar -->
  <script>
  (function(){
    var D={
      '--bg':'#0d1117','--surface':'#161b22','--surface2':'#1c2128',
      '--border':'rgba(255,255,255,.08)','--text':'#cdd9e5',
      '--text-soft':'#768390','--text-muted':'#545d68',
      '--primary-soft':'rgba(26,86,219,.18)','--teal-soft':'rgba(8,145,178,.18)',
      '--success-soft':'rgba(5,150,105,.18)','--warning-soft':'rgba(217,119,6,.18)',
      '--danger-soft':'rgba(220,38,38,.18)','--purple-soft':'rgba(124,58,237,.18)',
      '--orange-soft':'rgba(234,88,12,.18)',
      '--shadow':'0 1px 4px rgba(0,0,0,.35)',
      '--shadow-md':'0 4px 20px rgba(0,0,0,.45)',
      '--shadow-lg':'0 12px 40px rgba(0,0,0,.55)'
    };
    window.__LAAB_DARK=D;
    window.__applyTheme=function(t){
      var el=document.documentElement;
      el.setAttribute('data-theme',t);
      if(t==='dark'){Object.keys(D).forEach(function(k){el.style.setProperty(k,D[k]);});}
      else{Object.keys(D).forEach(function(k){el.style.removeProperty(k);});}
    };
    window.__applyTheme(localStorage.getItem('laab-theme')||'light');
  })();
  </script>
</head>
<body>
{% block body %}
<div class="layout">

  <aside class="sidebar">
    <div class="sidebar-brand">
      <div class="brand-row">
        <div class="brand-icon"><i class="fa-solid fa-plus"></i></div>
        <div class="brand-name">la<span>ab</span></div>
      </div>
      <div class="brand-tagline">Sistema de Turnos · Clínica laab</div>
    </div>

    <nav class="sidebar-nav">
      {% with rol=request.session.usuario.rol %}

        {% if rol == 'admin' %}
          <span class="nav-label">Administración</span>
          <a href="{% url 'accounts:panel_admin' %}" class="nav-link {% if request.resolver_match.url_name == 'panel_admin' %}active{% endif %}">
            <i class="fa-solid fa-gauge-high"></i> Panel general
          </a>
          <a href="{% url 'turnos:panel_secretaria' %}" class="nav-link {% if request.resolver_match.url_name == 'panel_secretaria' %}active{% endif %}">
            <i class="fa-solid fa-calendar-days"></i> Agenda de turnos
          </a>
          <a href="{% url 'turnos:crear_turno' %}" class="nav-link {% if request.resolver_match.url_name == 'crear_turno' %}active{% endif %}">
            <i class="fa-solid fa-calendar-plus"></i> Nuevo turno
          </a>

        {% elif rol == 'secretaria' %}
          <span class="nav-label">Secretaría</span>
          <a href="{% url 'turnos:panel_secretaria' %}" class="nav-link {% if request.resolver_match.url_name == 'panel_secretaria' %}active{% endif %}">
            <i class="fa-solid fa-calendar-days"></i> Agenda de turnos
          </a>
          <a href="{% url 'turnos:crear_turno' %}" class="nav-link {% if request.resolver_match.url_name == 'crear_turno' %}active{% endif %}">
            <i class="fa-solid fa-calendar-plus"></i> Nuevo turno
          </a>

        {% elif rol == 'doctor' %}
          <span class="nav-label">Doctor</span>
          <a href="{% url 'turnos:panel_doctor' %}" class="nav-link {% if request.resolver_match.url_name == 'panel_doctor' %}active{% endif %}">
            <i class="fa-solid fa-stethoscope"></i> Mi agenda
          </a>

        {% elif rol == 'paciente' %}
          <span class="nav-label">Paciente</span>
          <a href="{% url 'turnos:panel_paciente' %}" class="nav-link {% if request.resolver_match.url_name == 'panel_paciente' %}active{% endif %}">
            <i class="fa-solid fa-file-medical"></i> Mis turnos
          </a>
        {% endif %}

      {% endwith %}
    </nav>

    <div class="sidebar-footer">
      {% with u=request.session.usuario %}
      {% if u %}
      <div class="user-chip">
        <div class="user-avatar">{{ u.nombre_completo|first|upper }}</div>
        <div>
          <div class="user-name">{{ u.nombre_completo }}</div>
          <div class="user-role">{{ u.rol }}</div>
        </div>
      </div>
      <a href="{% url 'accounts:logout' %}" class="btn-logout">
        <i class="fa-solid fa-right-from-bracket"></i> Cerrar sesión
      </a>
      {% endif %}
      {% endwith %}
    </div>
  </aside>

  <main class="main">
    <div class="topbar">
      <div class="topbar-title">{% block page_title %}{% endblock %}</div>
      <div class="topbar-actions" style="display:flex;align-items:center;gap:8px;">
        {% block topbar_actions %}{% endblock %}
        <button class="btn-theme-toggle" id="theme-toggle" onclick="toggleTheme()" title="Cambiar tema">
          <i class="fa-solid fa-moon" id="theme-icon"></i>
        </button>
      </div>
    </div>
    <div class="page-content">
      {% if messages %}
        <ul class="messages">
          {% for message in messages %}
            <li class="message {{ message.tags }}">{{ message }}</li>
          {% endfor %}
        </ul>
      {% endif %}
      {% block content %}{% endblock %}
    </div>
  </main>

</div>
{% endblock %}
<script>
(function(){
  function syncIcon(t){
    var i=document.getElementById('theme-icon');
    if(i) i.className=t==='dark'?'fa-solid fa-sun':'fa-solid fa-moon';
  }
  var cur=document.documentElement.getAttribute('data-theme')||'light';
  syncIcon(cur);
  window.toggleTheme=function(){
    var c=document.documentElement.getAttribute('data-theme')||'light';
    var n=c==='dark'?'light':'dark';
    window.__applyTheme(n);
    localStorage.setItem('laab-theme',n);
    syncIcon(n);
  };
})();
</script>
</body>
</html>
