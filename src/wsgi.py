from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date, datetime
from .usuarios import usuario_repo, Usuario
from turnos.logica import medico_repo, Especialidad, repositorio as turno_repo, HORARIOS, DURACIONES

COLORES_ESP = {
    'Clínica Médica': '#3b82f6',
    'Pediatría':      '#8b5cf6',
    'Cardiología':    '#ef4444',
    'Ginecología':    '#f59e0b',
    'Traumatología':  '#10b981',
    'Dermatología':   '#0d9488',
}


ESPECIALIDADES = [e.value for e in Especialidad]


def login_view(request):
    if request.session.get('usuario'):
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        usuario  = usuario_repo.buscar(username)

        if usuario and usuario.verificar_password(password):
            request.session['usuario'] = usuario.to_dict()
            return redirect('accounts:dashboard')
        else:
            messages.error(request, 'Usuario o contrasena incorrectos.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    request.session.flush()
    return redirect('accounts:login')


def dashboard(request):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('accounts:login')

    rol = usuario.get('rol')
    if rol == 'admin':
        return redirect('accounts:panel_admin')
    elif rol == 'secretaria':
        return redirect('turnos:panel_secretaria')
    elif rol == 'doctor':
        return redirect('turnos:panel_doctor')
    elif rol == 'paciente':
        return redirect('turnos:panel_paciente')

    messages.error(request, 'Rol no reconocido.')
    return redirect('accounts:login')


def panel_admin(request):
    usuario = request.session.get('usuario')
    if not usuario or usuario.get('rol') != 'admin':
        messages.error(request, 'Acceso denegado.')
        return redirect('accounts:login')

    if request.method == 'POST':
        accion = request.POST.get('accion')

        if accion == 'crear':
            username     = request.POST.get('username', '').strip()
            password     = request.POST.get('password', '').strip()
            rol          = request.POST.get('rol', 'paciente')
            nombre       = request.POST.get('nombre_completo', '').strip()
            especialidad = request.POST.get('especialidad', '').strip()
            matricula    = request.POST.get('matricula', '').strip()

            if not username or not password or not nombre:
                messages.error(request, 'Completa todos los campos obligatorios.')
            elif usuario_repo.existe(username):
                messages.error(request, f"El usuario '{username}' ya existe.")
            else:
                nuevo = Usuario(username, password, rol, nombre,
                                especialidad=especialidad, matricula=matricula)
                usuario_repo.agregar(nuevo)

                # Si es doctor, agregarlo también al registro de médicos
                if rol == 'doctor':
                    if not matricula:
                        matricula = f"MP-{username.upper()}"
                    medico_repo.agregar(nombre, especialidad or 'Clinica Medica', matricula)

                messages.success(request, f"Usuario '{username}' creado correctamente.")

        elif accion == 'eliminar':
            username = request.POST.get('username')
            if username == 'admin':
                messages.error(request, 'No podes eliminar al admin.')
            else:
                u = usuario_repo.buscar(username)
                # Si era doctor, eliminarlo del registro de médicos también
                if u and u.rol == 'doctor' and u.matricula:
                    medico_repo.eliminar(u.matricula)
                usuario_repo.eliminar(username)
                messages.success(request, f"Usuario '{username}' eliminado.")

        return redirect('accounts:panel_admin')

    todos            = usuario_repo.todos()
    hoy              = date.today().isoformat()
    dia_semana_hoy   = date.today().weekday()
    todos_turnos     = turno_repo.todos()
    turnos_hoy       = [t for t in todos_turnos if t.fecha == hoy]
    medicos          = medico_repo.todos()

    doctor_stats = []
    for m in medicos:
        t_hoy   = [t for t in turnos_hoy if t.medico.nombre == m.nombre]
        pend    = sum(1 for t in t_hoy if t.estado == 'PENDIENTE')
        horario = HORARIOS.get(m.matricula, {})

        if dia_semana_hoy not in horario.get('dias', []):
            badge_txt = 'No atiende hoy'
            badge_cls = 'gray'
        else:
            dur    = DURACIONES.get(m.especialidad.value, 20)
            inicio = datetime.strptime(horario['inicio'], '%H:%M')
            fin    = datetime.strptime(horario['fin'],    '%H:%M')
            total  = int((fin - inicio).total_seconds() // 60) // dur
            ocup   = len([t for t in t_hoy if t.estado != 'CANCELADO'])
            if pend > 0:
                badge_txt = f'{pend} pendiente{"s" if pend > 1 else ""}'
                badge_cls = 'amber'
            elif ocup >= total:
                badge_txt = 'Sin lugar'
                badge_cls = 'red'
            else:
                badge_txt = 'Disponible'
                badge_cls = 'green'

        doctor_stats.append({
            'medico':     m,
            'turnos_hoy': len(t_hoy),
            'color':      COLORES_ESP.get(m.especialidad.value, '#3b82f6'),
            'badge_txt':  badge_txt,
            'badge_cls':  badge_cls,
        })

    doctor_stats.sort(key=lambda x: x['turnos_hoy'], reverse=True)
    max_hoy = max((d['turnos_hoy'] for d in doctor_stats), default=1) or 1
    for d in doctor_stats:
        d['pct'] = round(d['turnos_hoy'] / max_hoy * 100)

    roles_stats = [
        (sum(1 for u in todos if u.rol == 'secretaria'), 'Secretarias', 'blue'),
        (sum(1 for u in todos if u.rol == 'doctor'),     'Doctores',    'green'),
        (sum(1 for u in todos if u.rol == 'paciente'),   'Pacientes',   'purple'),
        (sum(1 for u in todos if u.rol == 'admin'),      'Admins',      'amber'),
    ]

    # Turnos por día de la semana (últimos 7 días)
    from datetime import timedelta
    semana = []
    for i in range(6, -1, -1):
        d = date.today() - timedelta(days=i)
        count = sum(1 for t in todos_turnos if t.fecha == d.isoformat())
        semana.append({'dia': d.strftime('%a'), 'count': count})
    max_semana = max((s['count'] for s in semana), default=1) or 1

    return render(request, 'accounts/panel_admin.html', {
        'usuarios':      todos,
        'roles_stats':   roles_stats,
        'especialidades': ESPECIALIDADES,
        'turnos_hoy':    [t.to_dict() for t in turnos_hoy],
        'total_turnos':  len(todos_turnos),
        'confirmados':   sum(1 for t in todos_turnos if t.estado == 'CONFIRMADO'),
        'cancelados':    sum(1 for t in todos_turnos if t.estado == 'CANCELADO'),
        'doctor_stats':  doctor_stats,
        'semana':        semana,
        'max_semana':    max_semana,
        'hoy_str':       date.today().strftime('%A %d de %B, %Y'),
    })
