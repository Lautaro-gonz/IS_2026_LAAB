from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date, datetime, timedelta
from .models import UsuarioDB, inicializar_usuarios
from turnos.logica import medico_repo, Especialidad, HORARIOS, DURACIONES
from turnos.models import TurnoDB

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
    inicializar_usuarios()
    if request.session.get('usuario'):
        return redirect('accounts:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        try:
            usuario = UsuarioDB.objects.get(username=username)
            if usuario.verificar_password(password):
                request.session['usuario'] = usuario.to_dict()
                return redirect('accounts:dashboard')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        except UsuarioDB.DoesNotExist:
            messages.error(request, 'Usuario o contraseña incorrectos.')

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
            elif UsuarioDB.objects.filter(username=username).exists():
                messages.error(request, f"El usuario '{username}' ya existe.")
            else:
                u = UsuarioDB(username=username, rol=rol, nombre_completo=nombre,
                              especialidad=especialidad, matricula=matricula)
                u.set_password(password)
                u.save()
                if rol == 'doctor':
                    if not matricula:
                        matricula = f"MP-{username.upper()}"
                    medico_repo.agregar(nombre, especialidad or 'Clinica Medica', matricula)
                messages.success(request, f"Usuario '{username}' creado correctamente.")

        elif accion == 'eliminar':
            username = request.POST.get('username')
            if username == 'admin':
                messages.error(request, 'No podés eliminar al admin.')
            else:
                try:
                    u = UsuarioDB.objects.get(username=username)
                    if u.rol == 'doctor' and u.matricula:
                        medico_repo.eliminar(u.matricula)
                    u.delete()
                    messages.success(request, f"Usuario '{username}' eliminado.")
                except UsuarioDB.DoesNotExist:
                    messages.error(request, 'Usuario no encontrado.')

        return redirect('accounts:panel_admin')

    # Stats
    hoy            = date.today()
    dia_semana_hoy = hoy.weekday()
    todos_turnos   = TurnoDB.objects.all()
    turnos_hoy     = TurnoDB.objects.filter(fecha=hoy)
    medicos        = medico_repo.todos()
    todos_usuarios = UsuarioDB.objects.all()

    doctor_stats = []
    for m in medicos:
        t_hoy  = turnos_hoy.filter(medico_nombre=m.nombre)
        pend   = t_hoy.filter(estado='PENDIENTE').count()
        horario = HORARIOS.get(m.matricula, {})

        if dia_semana_hoy not in horario.get('dias', []):
            badge_txt, badge_cls = 'No atiende hoy', 'gray'
        else:
            dur    = DURACIONES.get(m.especialidad.value, 20)
            inicio = datetime.strptime(horario['inicio'], '%H:%M')
            fin    = datetime.strptime(horario['fin'],    '%H:%M')
            total  = int((fin - inicio).total_seconds() // 60) // dur
            ocup   = t_hoy.exclude(estado='CANCELADO').count()
            if pend > 0:
                badge_txt, badge_cls = f'{pend} pendiente{"s" if pend > 1 else ""}', 'amber'
            elif ocup >= total:
                badge_txt, badge_cls = 'Sin lugar', 'red'
            else:
                badge_txt, badge_cls = 'Disponible', 'green'

        doctor_stats.append({
            'medico':     m,
            'turnos_hoy': t_hoy.count(),
            'color':      COLORES_ESP.get(m.especialidad.value, '#3b82f6'),
            'badge_txt':  badge_txt,
            'badge_cls':  badge_cls,
        })

    doctor_stats.sort(key=lambda x: x['turnos_hoy'], reverse=True)
    max_hoy = max((d['turnos_hoy'] for d in doctor_stats), default=1) or 1
    for d in doctor_stats:
        d['pct'] = round(d['turnos_hoy'] / max_hoy * 100)

    roles_stats = [
        (todos_usuarios.filter(rol='secretaria').count(), 'Secretarias', 'blue'),
        (todos_usuarios.filter(rol='doctor').count(),     'Doctores',    'green'),
        (todos_usuarios.filter(rol='paciente').count(),   'Pacientes',   'purple'),
        (todos_usuarios.filter(rol='admin').count(),      'Admins',      'amber'),
    ]

    semana = []
    for i in range(6, -1, -1):
        d = hoy - timedelta(days=i)
        count = TurnoDB.objects.filter(fecha=d).count()
        semana.append({'dia': d.strftime('%a'), 'count': count})
    max_semana = max((s['count'] for s in semana), default=1) or 1

    return render(request, 'accounts/panel_admin.html', {
        'usuarios':       todos_usuarios,
        'roles_stats':    roles_stats,
        'especialidades': ESPECIALIDADES,
        'turnos_hoy':     [t.to_dict() for t in turnos_hoy],
        'total_turnos':   todos_turnos.count(),
        'confirmados':    todos_turnos.filter(estado='CONFIRMADO').count(),
        'cancelados':     todos_turnos.filter(estado='CANCELADO').count(),
        'doctor_stats':   doctor_stats,
        'semana':         semana,
        'max_semana':     max_semana,
        'hoy_str':        hoy.strftime('%A %d de %B, %Y'),
    })
