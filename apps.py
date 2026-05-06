<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>laab · Iniciar sesión</title>
  {% load static %}
  <link rel="stylesheet" href="{% static 'css/style.css' %}">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <script>
  (function(){
    window.__applyTheme=function(t){
      var el=document.documentElement;
      el.setAttribute('data-theme',t);
    };
    window.__applyTheme(localStorage.getItem('laab-theme')||'light');
  })();
  </script>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Inter', sans-serif;
      background: #060d1f;
      min-height: 100vh;
    }

    .login-wrap {
      min-height: 100vh;
      display: grid;
      grid-template-columns: 420px 1fr;
    }

    /* ══ PANEL IZQUIERDO ══ */
    .login-brand-panel {
      background: linear-gradient(160deg, #060d1f 0%, #0a1628 60%, #0d1e38 100%);
      border-right: 1px solid rgba(96,165,250,.12);
      display: flex;
      flex-direction: column;
      padding: 52px 44px;
      position: relative;
      overflow: hidden;
    }

    /* Destellos de fondo */
    .login-brand-panel::before {
      content: '';
      position: absolute;
      top: -80px; left: -80px;
      width: 320px; height: 320px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(37,99,235,.18), transparent 70%);
      pointer-events: none;
    }
    .login-brand-panel::after {
      content: '';
      position: absolute;
      bottom: -100px; right: -60px;
      width: 280px; height: 280px;
      border-radius: 50%;
      background: radial-gradient(circle, rgba(96,165,250,.1), transparent 70%);
      pointer-events: none;
    }

    /* ── Logo ── */
    .brand-logo {
      display: flex;
      align-items: center;
      gap: 20px;
      margin-bottom: 28px;
      position: relative;
      z-index: 1;
    }

    .brand-emblem {
      width: 72px; height: 72px;
      background: linear-gradient(135deg, #1a3a6e, #0f2348);
      border: 1.5px solid rgba(96,165,250,.3);
      border-radius: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 8px 32px rgba(37,99,235,.25), inset 0 1px 0 rgba(255,255,255,.06);
      flex-shrink: 0;
    }

    .brand-name-block { display: flex; flex-direction: column; gap: 4px; }

    .brand-name {
      font-family: 'Playfair Display', Georgia, serif;
      font-size: 52px;
      font-weight: 800;
      color: #ffffff;
      letter-spacing: 8px;
      line-height: 1;
      text-shadow: 0 2px 24px rgba(96,165,250,.2);
    }

    .brand-subtitle-row {
      display: flex;
      align-items: center;
      gap: 14px;
      margin-top: 2px;
    }
    .brand-subtitle {
      font-size: 9px;
      letter-spacing: 3.5px;
      color: rgba(148,187,233,.65);
      font-weight: 500;
      text-transform: uppercase;
    }
    .brand-est {
      font-size: 9px;
      color: rgba(255,255,255,.22);
      white-space: nowrap;
    }

    .brand-divider {
      height: 1.5px;
      margin-top: 8px;
      background: linear-gradient(90deg, #2563eb, #60a5fa, rgba(96,165,250,.05));
      border-radius: 1px;
    }

    .brand-tagline {
      font-size: 9px;
      letter-spacing: 5px;
      color: rgba(148,187,233,.3);
      position: relative;
      z-index: 1;
    }

    /* ── Info cards debajo ── */
    .brand-info {
      margin-top: auto;
      position: relative;
      z-index: 1;
      display: flex;
      flex-direction: column;
      gap: 12px;
    }

    .brand-info-item {
      display: flex;
      align-items: center;
      gap: 14px;
      padding: 14px 16px;
      background: rgba(255,255,255,.03);
      border: 1px solid rgba(255,255,255,.06);
      border-radius: 12px;
    }
    .brand-info-icon {
      width: 36px; height: 36px;
      border-radius: 10px;
      display: flex; align-items: center; justify-content: center;
      font-size: 15px;
      flex-shrink: 0;
    }
    .brand-info-icon.blue   { background: rgba(37,99,235,.18);  color: #60a5fa; }
    .brand-info-icon.teal   { background: rgba(8,145,178,.18);  color: #22d3ee; }
    .brand-info-icon.green  { background: rgba(5,150,105,.18);  color: #34d399; }
    .brand-info-text strong {
      display: block;
      font-size: 12px; font-weight: 600;
      color: rgba(255,255,255,.75);
      margin-bottom: 1px;
    }
    .brand-info-text span {
      font-size: 11px;
      color: rgba(255,255,255,.3);
    }

    /* ══ PANEL DERECHO ══ */
    .login-form-panel {
      background: linear-gradient(160deg, #0d1e35 0%, #0f2244 100%);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 48px 40px;
    }

    [data-theme="light"] .login-form-panel {
      background: #f4f7ff;
    }
    [data-theme="light"] .login-brand-panel {
      background: linear-gradient(160deg, #0a1628 0%, #0d1e38 100%);
    }

    .login-form-inner { width: 100%; max-width: 400px; }

    .login-eyebrow {
      font-size: 11px;
      letter-spacing: 3px;
      color: #60a5fa;
      font-weight: 700;
      margin-bottom: 10px;
    }
    [data-theme="light"] .login-eyebrow { color: #1a56db; }

    .login-heading {
      font-family: 'Playfair Display', Georgia, serif;
      font-size: 38px;
      font-weight: 800;
      color: #ffffff;
      letter-spacing: -.5px;
      line-height: 1.1;
      margin-bottom: 6px;
    }
    [data-theme="light"] .login-heading { color: #0d1b3e; }

    .login-heading span { color: #60a5fa; }
    [data-theme="light"] .login-heading span { color: #1a56db; }

    .login-subheading {
      font-size: 13px;
      color: rgba(255,255,255,.35);
      margin-bottom: 36px;
      font-weight: 400;
    }
    [data-theme="light"] .login-subheading { color: #4a5578; }

    /* ── Campos ── */
    .field-wrap { margin-bottom: 18px; }

    .field-label {
      font-size: 10px;
      letter-spacing: 2px;
      font-weight: 700;
      color: rgba(255,255,255,.4);
      margin-bottom: 8px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    [data-theme="light"] .field-label { color: #4a5578; }

    .field-label i { font-size: 11px; opacity: .7; }

    .dark-input {
      width: 100%;
      padding: 14px 16px;
      background: rgba(255,255,255,.97);
      border: 1.5px solid transparent;
      border-radius: 10px;
      font-size: 15px;
      color: #0d1b3e;
      font-family: 'Inter', sans-serif;
      outline: none;
      transition: border-color .2s, box-shadow .2s;
    }
    [data-theme="light"] .dark-input {
      background: #ffffff;
      border-color: #c7d2fe;
    }
    .dark-input:focus {
      border-color: #60a5fa;
      box-shadow: 0 0 0 3px rgba(96,165,250,.2);
    }
    [data-theme="light"] .dark-input:focus {
      border-color: #1a56db;
      box-shadow: 0 0 0 3px rgba(26,86,219,.12);
    }

    .btn-login {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      width: 100%;
      padding: 14px;
      background: none;
      border: none;
      cursor: pointer;
      color: #60a5fa;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 3px;
      font-family: 'Inter', sans-serif;
      transition: color .2s, letter-spacing .2s;
      margin-top: 4px;
    }
    [data-theme="light"] .btn-login { color: #1a56db; }
    .btn-login:hover { color: #93c5fd; letter-spacing: 4px; }
    [data-theme="light"] .btn-login:hover { color: #1442b5; }
    .btn-login i { font-size: 16px; }

    /* ── Demo card ── */
    .demo-card {
      margin-top: 24px;
      background: rgba(255,255,255,.04);
      border: 1px solid rgba(255,255,255,.08);
      border-radius: 12px;
      padding: 16px 18px;
    }
    [data-theme="light"] .demo-card {
      background: #f0f4ff;
      border-color: #dde5ff;
    }
    .demo-card-title {
      font-size: 10px;
      letter-spacing: 2px;
      font-weight: 700;
      color: #60a5fa;
      margin-bottom: 12px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    [data-theme="light"] .demo-card-title { color: #1a56db; }
    .demo-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 6px 20px;
      font-size: 12px;
      color: rgba(255,255,255,.38);
    }
    [data-theme="light"] .demo-grid { color: #4a5578; }

    .error-msg {
      background: rgba(220,38,38,.15);
      border: 1px solid rgba(220,38,38,.3);
      color: #fca5a5;
      border-radius: 10px;
      padding: 11px 14px;
      font-size: 13px;
      margin-bottom: 18px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    /* ── Toggle tema ── */
    .login-theme-toggle {
      position: fixed;
      top: 16px; right: 16px;
      z-index: 999;
      width: 38px; height: 38px;
      border-radius: 10px;
      background: rgba(255,255,255,.1);
      border: 1px solid rgba(255,255,255,.15);
      color: rgba(255,255,255,.65);
      cursor: pointer;
      font-size: 15px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all .18s;
      backdrop-filter: blur(6px);
    }
    .login-theme-toggle:hover { background: rgba(255,255,255,.2); color: #fff; }
    [data-theme="light"] .login-theme-toggle {
      background: rgba(26,86,219,.1);
      border-color: rgba(26,86,219,.2);
      color: #1a56db;
    }

    @media (max-width: 768px) {
      .login-wrap { grid-template-columns: 1fr; }
      .login-brand-panel { padding: 32px 28px; }
      .brand-info { display: none; }
    }
  </style>
</head>
<body>

<button class="login-theme-toggle" onclick="toggleTheme()" title="Cambiar tema">
  <i class="fa-solid fa-moon" id="login-theme-icon"></i>
</button>

<div class="login-wrap">

  <!-- ══ IZQUIERDA: Branding ══ -->
  <div class="login-brand-panel">

    <div class="brand-logo">
      <!-- Emblema cuadrado con cruz médica -->
      <div class="brand-emblem">
        <svg width="40" height="40" viewBox="0 0 40 40" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- Cruz médica -->
          <rect x="15" y="6" width="10" height="28" rx="3" fill="rgba(96,165,250,.9)"/>
          <rect x="6" y="15" width="28" height="10" rx="3" fill="rgba(96,165,250,.9)"/>
          <!-- Brillo -->
          <rect x="15" y="6" width="4" height="28" rx="3" fill="rgba(255,255,255,.15)"/>
          <rect x="6" y="15" width="28" height="4" rx="3" fill="rgba(255,255,255,.15)"/>
        </svg>
      </div>

      <div class="brand-name-block">
        <div class="brand-name">LAAB</div>
        <div class="brand-subtitle-row">
          <span class="brand-subtitle">CLÍNICA MÉDICA PRIVADA</span>
          <span class="brand-est">Est. 2024</span>
        </div>
        <div class="brand-divider"></div>
      </div>
    </div>

    <div class="brand-tagline">SALUD &nbsp;·&nbsp; CONFIANZA &nbsp;·&nbsp; EXCELENCIA</div>



  </div>

  <!-- ══ DERECHA: Formulario ══ -->
  <div class="login-form-panel">
    <div class="login-form-inner">

      <div class="login-eyebrow">BIENVENIDO</div>
      <div class="login-heading">Iniciar <span>sesión</span></div>
      <div class="login-subheading">Sistema de Turnos · Clínica LAAB</div>

      {% if messages %}
        {% for message in messages %}
          <div class="error-msg"><i class="fa-solid fa-circle-exclamation"></i> {{ message }}</div>
        {% endfor %}
      {% endif %}

      <form method="post" style="display:flex;flex-direction:column;">
        {% csrf_token %}

        <div class="field-wrap">
          <div class="field-label"><i class="fa-regular fa-user"></i> USUARIO</div>
          <input class="dark-input" type="text" name="username" placeholder="Ingresá tu usuario" autofocus required>
        </div>

        <div class="field-wrap">
          <div class="field-label"><i class="fa-solid fa-lock"></i> CONTRASEÑA</div>
          <input class="dark-input" type="password" name="password" placeholder="••••••••" required>
        </div>

        <button type="submit" class="btn-login">
          <i class="fa-solid fa-right-to-bracket"></i> INICIAR SESIÓN
        </button>
      </form>

      <div class="demo-card">
        <div class="demo-card-title">
          <i class="fa-solid fa-circle-info"></i> USUARIOS DE PRUEBA
        </div>
        <div class="demo-grid">
          <div>admin / admin123</div>
          <div>secretaria / secre123</div>
          <div>doctor1 / doc123</div>
          <div>paciente1 / pac123</div>
        </div>
      </div>

    </div>
  </div>

</div>

<script>
(function(){
  function syncIcon(t){
    var i = document.getElementById('login-theme-icon');
    if(i) i.className = t==='dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
  }
  var cur = document.documentElement.getAttribute('data-theme') || 'light';
  syncIcon(cur);
  window.toggleTheme = function(){
    var c = document.documentElement.getAttribute('data-theme') || 'light';
    var n = c==='dark' ? 'light' : 'dark';
    window.__applyTheme(n);
    localStorage.setItem('laab-theme', n);
    syncIcon(n);
  };
})();
</script>
</body>
</html>
