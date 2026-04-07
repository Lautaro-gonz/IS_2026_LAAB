from django.shortcuts import render, redirect
from django.contrib import messages
from .usuarios import usuario_repo, Usuario
from turnos.logica import medico_repo, Especialidad


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

    todos = usuario_repo.todos()
    roles_stats = [
        (sum(1 for u in todos if u.rol == 'secretaria'), 'Secretarias', 'blue'),
        (sum(1 for u in todos if u.rol == 'doctor'),     'Doctores',    'green'),
        (sum(1 for u in todos if u.rol == 'paciente'),   'Pacientes',   'purple'),
        (sum(1 for u in todos if u.rol == 'admin'),      'Admins',      'amber'),
    ]
    return render(request, 'accounts/panel_admin.html', {
        'usuarios':      todos,
        'roles_stats':   roles_stats,
        'especialidades': ESPECIALIDADES,
    })
