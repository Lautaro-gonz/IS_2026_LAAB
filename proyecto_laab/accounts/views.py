import re
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date, datetime, timedelta
from .models import UsuarioDB, inicializar_usuarios, AuditoriaDB, registrar_auditoria
from turnos.logica import Especialidad, HORARIOS, DURACIONES
from turnos.models import TurnoDB, ObraSocialDB

COLORES_ESP = {
    'Clínica Médica': '#3b82f6',
    'Pediatría':      '#8b5cf6',
    'Cardiología':    '#ef4444',
    'Ginecología':    '#f59e0b',
    'Traumatología':  '#10b981',
    'Dermatología':   '#0d9488',
}

ESPECIALIDADES = [e.value for e in Especialidad]

# Código interno de autorización para administrador
CODIGO_ADMIN = 'LAAB-ADMIN-2024'


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
                registrar_auditoria(usuario.username, usuario.rol, 'LOGIN', 'Inicio de sesión exitoso.')
                return redirect('accounts:dashboard')
            else:
                messages.error(request, 'Usuario o contraseña incorrectos.')
        except UsuarioDB.DoesNotExist:
            messages.error(request, 'Usuario o contraseña incorrectos.')

    timeout = request.GET.get('timeout')
    return render(request, 'accounts/login.html', {
        'especialidades': ESPECIALIDADES,
        'timeout': timeout,
    })


def registro_view(request):
    if request.session.get('usuario'):
        return redirect('accounts:dashboard')

    error = None
    reg_rol = 'paciente'

    if request.method == 'POST':
        rol      = request.POST.get('rol', 'paciente')
        nombre   = request.POST.get('nombre_completo', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        confirm  = request.POST.get('confirm_password', '').strip()
        reg_rol  = rol

        # Validaciones comunes
        if not nombre or not username or not password:
            error = 'Completá todos los campos obligatorios.'
        elif len(username) < 4:
            error = 'El usuario debe tener al menos 4 caracteres.'
        elif len(password) < 6:
            error = 'La contraseña debe tener al menos 6 caracteres.'
        elif password != confirm:
            error = 'Las contraseñas no coinciden.'
        elif UsuarioDB.objects.filter(username=username).exists():
            error = f"El usuario '{username}' ya existe. Elegí otro."
        elif UsuarioDB.objects.filter(nombre_completo__iexact=nombre).exists():
            error = f"Ya existe un usuario con el nombre '{nombre}'. Verificá los datos."

        elif rol == 'paciente':
            dni = request.POST.get('dni', '').strip()
            if not dni:
                error = 'Ingresá tu número de DNI.'
            elif not re.match(r'^\d{7,8}$', dni):
                error = 'El DNI debe tener 7 u 8 dígitos numéricos, sin puntos ni espacios.'
            else:
                u = UsuarioDB(username=username, rol='paciente', nombre_completo=nombre, dni=dni)
                u.set_password(password)
                u.save()
                registrar_auditoria(username, 'paciente', 'REGISTRO',
                    f"Nuevo paciente registrado: '{nombre}' (DNI: {dni}).")
                messages.success(request, f'¡Cuenta creada! Ya podés iniciar sesión, {nombre.split()[0]}.')
                return redirect('accounts:login')

        elif rol == 'doctor':
            matricula    = request.POST.get('matricula', '').strip().upper()
            especialidad = request.POST.get('especialidad', '').strip()
            if not matricula:
                error = 'Ingresá tu número de matrícula profesional.'
            elif not especialidad:
                error = 'Seleccioná tu especialidad.'
            elif not re.match(r'^MP-\d{4,6}$', matricula):
                error = 'La matrícula debe tener el formato MP-XXXX (ej: MP-12345).'
            elif UsuarioDB.objects.filter(matricula=matricula).exists():
                error = 'Esa matrícula ya está registrada en el sistema.'
            else:
                u = UsuarioDB(username=username, rol='doctor', nombre_completo=nombre,
                              especialidad=especialidad, matricula=matricula)
                u.set_password(password)
                u.save()
                registrar_auditoria(username, 'doctor', 'REGISTRO',
                    f"Nuevo doctor registrado: '{nombre}' (Mat: {matricula}, Esp: {especialidad}).")
                messages.success(request, f'¡Cuenta creada! Bienvenido/a, Dr/a. {nombre.split()[0]}.')
                return redirect('accounts:login')

        elif rol == 'admin':
            codigo = request.POST.get('codigo_institucional', '').strip()
            if not codigo:
                error = 'Ingresá el código de autorización de administrador.'
            elif codigo != CODIGO_ADMIN:
                error = 'Código de administrador incorrecto.'
            else:
                u = UsuarioDB(username=username, rol='admin', nombre_completo=nombre)
                u.set_password(password)
                u.save()
                registrar_auditoria(username, 'admin', 'REGISTRO',
                    f"Nuevo administrador registrado: '{nombre}'.")
                messages.success(request, f'¡Cuenta de administrador creada! Bienvenido/a, {nombre.split()[0]}.')
                return redirect('accounts:login')

        else:
            error = 'Tipo de cuenta no válido.'

    return render(request, 'accounts/login.html', {
        'reg_error':      error,
        'show_registro':  True,
        'reg_rol':        reg_rol,
        'especialidades': ESPECIALIDADES,
    })


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
            elif UsuarioDB.objects.filter(nombre_completo__iexact=nombre).exists():
                messages.error(request, f"Ya existe un usuario con el nombre '{nombre}'.")
            else:
                if rol == 'doctor' and not matricula:
                    matricula = f"MP-{username.upper()}"
                
                u = UsuarioDB(username=username, rol=rol, nombre_completo=nombre,
                              especialidad=especialidad or 'Clinica Medica', matricula=matricula)
                u.set_password(password)
                u.save()
                registrar_auditoria(usuario.get('username', 'admin'), 'admin', 'CREAR_USUARIO', f"Usuario '{username}' creado (rol: {rol}).")
                messages.success(request, f"Usuario '{username}' creado correctamente.")

        elif accion == 'eliminar':
            username = request.POST.get('username')
            if username == 'admin':
                messages.error(request, 'No podés eliminar al admin.')
            else:
                try:
                    u = UsuarioDB.objects.get(username=username)
                    u.delete()
                    registrar_auditoria(usuario.get('username', 'admin'), 'admin', 'ELIMINAR_USUARIO', f"Usuario '{username}' eliminado.")
                    messages.success(request, f"Usuario '{username}' eliminado.")
                except UsuarioDB.DoesNotExist:
                    messages.error(request, 'Usuario no encontrado.')

        elif accion == 'crear_os':
            nombre = request.POST.get('nombre', '').strip()
            cobertura = request.POST.get('cobertura', 0)
            if nombre:
                ObraSocialDB.objects.create(nombre=nombre, cobertura=float(cobertura))
                registrar_auditoria(usuario.get('username', 'admin'), 'admin', 'CREAR_OS', f"Obra Social '{nombre}' creada (cobertura: {cobertura}%).")
                messages.success(request, f"Obra Social '{nombre}' creada.")

        elif accion == 'editar_os':
            os_id = request.POST.get('os_id')
            cobertura = request.POST.get('cobertura', 0)
            try:
                os_obj = ObraSocialDB.objects.get(pk=os_id)
                os_obj.cobertura = float(cobertura)
                os_obj.save()
                registrar_auditoria(usuario.get('username', 'admin'), 'admin', 'EDITAR_OS', f"Obra Social '{os_obj.nombre}' modificada (cobertura: {cobertura}%).")
                messages.success(request, f"Obra Social '{os_obj.nombre}' actualizada.")
            except ObraSocialDB.DoesNotExist:
                messages.error(request, 'Obra Social no encontrada.')

        elif accion == 'eliminar_os':
            os_id = request.POST.get('os_id')
            try:
                os_obj = ObraSocialDB.objects.get(pk=os_id)
                nombre_os = os_obj.nombre
                os_obj.delete()
                registrar_auditoria(usuario.get('username', 'admin'), 'admin', 'ELIMINAR_OS', f"Obra Social '{nombre_os}' eliminada.")
                messages.success(request, f"Obra Social '{nombre_os}' eliminada.")
            except ObraSocialDB.DoesNotExist:
                messages.error(request, 'Obra Social no encontrada.')

        return redirect('accounts:panel_admin')

    # Stats
    hoy            = date.today()
    dia_semana_hoy = hoy.weekday()
    todos_turnos   = TurnoDB.objects.all()
    turnos_hoy     = TurnoDB.objects.filter(fecha=hoy)
    medicos        = UsuarioDB.objects.filter(rol='doctor')
    todos_usuarios = UsuarioDB.objects.all()
    obras_sociales = ObraSocialDB.objects.all()

    # Auditoria filter
    rol_auditoria = request.GET.get('rol_auditoria', '')
    auditoria_qs = AuditoriaDB.objects.all()
    if rol_auditoria:
        auditoria_qs = auditoria_qs.filter(rol=rol_auditoria)
    auditoria_logs = auditoria_qs[:100] # Limitar a los ultimos 100

    doctor_stats = []
    for m in medicos:
        t_hoy   = turnos_hoy.filter(medico_matricula=m.matricula)
        activos = t_hoy.exclude(estado='CANCELADO').count()
        pend    = t_hoy.filter(estado='PENDIENTE').count()
        conf    = t_hoy.filter(estado='CONFIRMADO').count()
        aten    = t_hoy.filter(estado='EN ATENCION').count()
        horario = HORARIOS.get(m.matricula, {})

        ahora_time    = datetime.now().time()
        hora_ini_str  = horario.get('inicio', '')
        hora_fin_str  = horario.get('fin', '')
        no_empezo     = bool(hora_ini_str) and ahora_time < datetime.strptime(hora_ini_str, '%H:%M').time()
        ya_termino    = bool(hora_fin_str) and ahora_time >= datetime.strptime(hora_fin_str, '%H:%M').time()
        if dia_semana_hoy not in horario.get('dias', []):
            badge_txt, badge_cls = 'No atiende hoy', 'gray'
        elif ya_termino:
            badge_txt, badge_cls = 'Finalizado', 'gray'
        elif no_empezo:
            badge_txt, badge_cls = f'Por comenzar · a partir de {hora_ini_str}', 'gray'
        else:
            dur    = DURACIONES.get(m.especialidad, 20)
            inicio = datetime.strptime(horario['inicio'], '%H:%M')
            fin    = datetime.strptime(horario['fin'],    '%H:%M')
            total  = int((fin - inicio).total_seconds() // 60) // dur
            if aten > 0:
                badge_txt, badge_cls = 'En atención', 'blue'
            elif pend > 0:
                badge_txt, badge_cls = f'{pend} pendiente{"s" if pend > 1 else ""}', 'amber'
            elif conf > 0:
                badge_txt, badge_cls = f'{conf} confirmado{"s" if conf > 1 else ""}', 'teal'
            elif activos >= total:
                badge_txt, badge_cls = 'Sin lugar', 'red'
            else:
                badge_txt, badge_cls = 'Disponible', 'green'

        doctor_stats.append({
            'medico':     m,
            'turnos_hoy': activos,
            'color':      COLORES_ESP.get(m.especialidad, '#3b82f6'),
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

    ultimo_turno_obj = TurnoDB.objects.order_by('-creado_en').first()
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
        'obras_sociales': obras_sociales,
        'auditoria_logs': auditoria_logs,
        'rol_auditoria':  rol_auditoria,
        'ultimo_turno':   ultimo_turno_obj.to_dict() if ultimo_turno_obj else None,
    })
