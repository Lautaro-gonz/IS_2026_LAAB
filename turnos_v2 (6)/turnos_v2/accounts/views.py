from django.shortcuts import render, redirect
from django.contrib import messages
from .usuarios import usuario_repo, Usuario
from turnos.logica import medico_repo, Especialidad, auditoria, obra_social_repo


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
            auditoria.registrar(usuario.nombre_completo, usuario.rol,
                'Inicio de sesion', f'Usuario {username} ingreso al sistema')
            return redirect('accounts:dashboard')
        else:
            auditoria.registrar(username, 'desconocido',
                'Login fallido', f'Intento fallido para {username}')
            messages.error(request, 'Usuario o contrasena incorrectos.')

    return render(request, 'accounts/login.html')


def logout_view(request):
    usuario = request.session.get('usuario', {})
    auditoria.registrar(
        usuario.get('nombre_completo', '?'),
        usuario.get('rol', '?'),
        'Cierre de sesion', ''
    )
    request.session.flush()
    return redirect('accounts:login')


def dashboard(request):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('accounts:login')
    rol = usuario.get('rol')
    if rol == 'admin':        return redirect('accounts:panel_admin')
    elif rol == 'secretaria': return redirect('turnos:panel_secretaria')
    elif rol == 'doctor':     return redirect('turnos:panel_doctor')
    elif rol == 'paciente':   return redirect('turnos:panel_paciente')
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
                if rol == 'doctor':
                    mat = matricula or f"MP-{username.upper()}"
                    medico_repo.agregar(nombre, especialidad or 'Clinica Medica', mat)
                auditoria.registrar(usuario.get('nombre_completo'), usuario.get('rol'),
                    'Crear usuario', f"'{username}' con rol '{rol}'")
                messages.success(request, f"Usuario '{username}' creado.")

        elif accion == 'eliminar':
            username = request.POST.get('username')
            if username == 'admin':
                messages.error(request, 'No podes eliminar al admin.')
            else:
                u = usuario_repo.buscar(username)
                if u and u.rol == 'doctor' and u.matricula:
                    medico_repo.eliminar(u.matricula)
                usuario_repo.eliminar(username)
                auditoria.registrar(usuario.get('nombre_completo'), usuario.get('rol'),
                    'Eliminar usuario', f"'{username}' eliminado")
                messages.success(request, f"Usuario '{username}' eliminado.")

        return redirect('accounts:panel_admin')

    todos = usuario_repo.todos()
    roles_stats = [
        (sum(1 for u in todos if u.rol == 'secretaria'), 'Secretarias', 'blue'),
        (sum(1 for u in todos if u.rol == 'doctor'),     'Doctores',    'green'),
        (sum(1 for u in todos if u.rol == 'paciente'),   'Pacientes',   'purple'),
        (sum(1 for u in todos if u.rol == 'admin'),      'Admins',      'amber'),
    ]
    return render(request, 'accounts/panel_admin.html', {
        'usuarios':       todos,
        'roles_stats':    roles_stats,
        'especialidades': ESPECIALIDADES,
    })


def panel_auditoria(request):
    usuario = request.session.get('usuario')
    if not usuario or usuario.get('rol') != 'admin':
        messages.error(request, 'Acceso denegado.')
        return redirect('accounts:login')

    filtro_rol = request.GET.get('rol', '')
    logs = auditoria.filtrar_por_rol(filtro_rol) if filtro_rol else auditoria.todos()
    todos_logs = auditoria.todos()
    stats = {
        'total':      len(todos_logs),
        'secretaria': len([l for l in todos_logs if l.rol == 'secretaria']),
        'doctor':     len([l for l in todos_logs if l.rol == 'doctor']),
        'paciente':   len([l for l in todos_logs if l.rol == 'paciente']),
        'admin':      len([l for l in todos_logs if l.rol == 'admin']),
    }
    return render(request, 'accounts/panel_auditoria.html', {
        'logs':       [l.to_dict() for l in logs],
        'stats':      stats,
        'filtro_rol': filtro_rol,
    })


def panel_pacientes(request):
    usuario = request.session.get('usuario')
    if not usuario or usuario.get('rol') != 'admin':
        messages.error(request, 'Acceso denegado.')
        return redirect('accounts:login')

    from turnos.logica import repositorio
    pacientes_dict = {}
    for t in repositorio.todos():
        dni = t.paciente.dni
        if dni not in pacientes_dict:
            pacientes_dict[dni] = {
                'nombre':      t.paciente.nombre,
                'dni':         dni,
                'obra_social': str(t.paciente.obra_social) if t.paciente.obra_social else 'Sin obra social',
                'turnos':      0,
                'ultimo':      t.fecha,
            }
        pacientes_dict[dni]['turnos'] += 1
        if t.fecha > pacientes_dict[dni]['ultimo']:
            pacientes_dict[dni]['ultimo'] = t.fecha

    return render(request, 'accounts/panel_pacientes.html', {
        'pacientes': sorted(pacientes_dict.values(), key=lambda p: p['nombre']),
    })


def panel_obras_sociales(request):
    usuario = request.session.get('usuario')
    if not usuario or usuario.get('rol') != 'admin':
        messages.error(request, 'Acceso denegado.')
        return redirect('accounts:login')

    if request.method == 'POST':
        accion = request.POST.get('accion')
        nombre = request.POST.get('nombre', '').strip()
        nombre_u = usuario.get('nombre_completo')
        rol_u    = usuario.get('rol')

        try:
            if accion == 'agregar':
                cobertura = request.POST.get('cobertura', '').strip()
                obra_social_repo.agregar(nombre, cobertura)
                auditoria.registrar(nombre_u, rol_u, 'Agregar obra social',
                    f"'{nombre}' con {cobertura}% de cobertura")
                messages.success(request, f"Obra social '{nombre}' agregada.")

            elif accion == 'modificar_cobertura':
                nueva = request.POST.get('cobertura', '').strip()
                obra_social_repo.modificar_cobertura(nombre, nueva)
                auditoria.registrar(nombre_u, rol_u, 'Modificar cobertura',
                    f"'{nombre}' → {nueva}%")
                messages.success(request, f"Cobertura de '{nombre}' actualizada a {nueva}%.")

            elif accion == 'desactivar':
                motivo = request.POST.get('motivo', '').strip()
                obra_social_repo.desactivar(nombre, motivo)
                auditoria.registrar(nombre_u, rol_u, 'Desactivar obra social',
                    f"'{nombre}'. Motivo: {motivo}")
                messages.success(request, f"'{nombre}' desactivada.")

            elif accion == 'activar':
                obra_social_repo.activar(nombre)
                auditoria.registrar(nombre_u, rol_u, 'Activar obra social', f"'{nombre}' reactivada")
                messages.success(request, f"'{nombre}' reactivada.")

            elif accion == 'eliminar':
                obra_social_repo.eliminar(nombre)
                auditoria.registrar(nombre_u, rol_u, 'Eliminar obra social', f"'{nombre}' eliminada")
                messages.success(request, f"'{nombre}' eliminada.")

        except ValueError as e:
            messages.error(request, str(e))

        return redirect('accounts:panel_obras_sociales')

    obras = obra_social_repo.todas()
    stats = {
        'total':     len(obras),
        'activas':   len([o for o in obras if o.activa]),
        'inactivas': len([o for o in obras if not o.activa]),
    }
    return render(request, 'accounts/panel_obras_sociales.html', {
        'obras': [o.to_dict() for o in obras],
        'stats': stats,
    })
