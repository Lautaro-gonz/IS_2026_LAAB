from django.shortcuts import render, redirect
from django.contrib import messages
from .logica import (
    repositorio, validador, TurnoFactory, medico_repo,
    Paciente, ObraSocial, OBRAS_SOCIALES
)


def rol_requerido(request, *roles):
    usuario = request.session.get('usuario')
    if not usuario:
        return False
    return usuario.get('rol') in roles


# ──────────────────────────────────────────────
# SECRETARIA
# ──────────────────────────────────────────────

def panel_secretaria(request):
    if not rol_requerido(request, 'secretaria', 'admin'):
        messages.error(request, 'Acceso denegado.')
        return redirect('accounts:login')

    fecha_filtro = request.GET.get('fecha', '')
    todos = repositorio.todos()

    if fecha_filtro:
        turnos = [t for t in todos if t.fecha == fecha_filtro]
    else:
        turnos = todos

    context = {
        'turnos':       [t.to_dict() for t in turnos],
        'fecha_filtro': fecha_filtro,
        'total':        len(todos),
    }
    return render(request, 'turnos/panel_secretaria.html', context)


def crear_turno(request):
    if not rol_requerido(request, 'secretaria', 'admin'):
        return redirect('accounts:login')

    error = None
    medicos = medico_repo.todos()

    if request.method == 'POST':
        nombre   = request.POST.get('nombre', '').strip()
        dni      = request.POST.get('dni', '').strip()
        telefono = request.POST.get('telefono', '').strip()
        email    = request.POST.get('email', '').strip()
        obra     = request.POST.get('obra_social', '')
        medico_i = request.POST.get('medico', '')
        fecha    = request.POST.get('fecha', '').strip()
        hora     = request.POST.get('hora', '').strip()

        if not all([nombre, dni, medico_i, fecha, hora]):
            error = 'Completa todos los campos obligatorios.'
        else:
            try:
                os_obj   = ObraSocial(obra) if obra else None
                paciente = Paciente(nombre, dni, telefono, email, os_obj)
                medico   = medico_repo.buscar_por_indice(int(medico_i))

                if not medico:
                    error = 'Medico no encontrado.'
                else:
                    puede, msg = validador.validar(paciente)
                    if not puede:
                        error = msg
                    else:
                        turno = TurnoFactory.crear(paciente, medico, fecha, hora)
                        repositorio.agregar(turno)
                        messages.success(request, f'Turno #{turno.id} creado para {nombre}.')
                        return redirect('turnos:panel_secretaria')
            except Exception as e:
                error = str(e)

    context = {
        'medicos':        [(i, str(m)) for i, m in enumerate(medicos)],
        'obras_sociales': OBRAS_SOCIALES,
        'error':          error,
    }
    return render(request, 'turnos/form_turno.html', context)


def accion_turno(request, turno_id):
    if not rol_requerido(request, 'secretaria', 'admin'):
        return redirect('accounts:login')

    turno = repositorio.buscar_por_id(turno_id)
    if not turno:
        messages.error(request, 'Turno no encontrado.')
        return redirect('turnos:panel_secretaria')

    if request.method == 'POST':
        accion = request.POST.get('accion')
        try:
            if accion == 'confirmar':
                turno.confirmar()
                messages.success(request, f'Turno #{turno_id} confirmado.')
            elif accion == 'cancelar':
                motivo = request.POST.get('motivo', '')
                turno.cancelar(motivo)
                messages.success(request, f'Turno #{turno_id} cancelado.')
            elif accion == 'reprogramar':
                nueva_fecha = request.POST.get('nueva_fecha')
                nueva_hora  = request.POST.get('nueva_hora')
                turno.reprogramar(nueva_fecha, nueva_hora)
                messages.success(request, f'Turno #{turno_id} reprogramado.')
            elif accion == 'atender':
                turno.atender()
                messages.success(request, f'Turno #{turno_id} en atencion.')
            elif accion == 'completar':
                turno.completar()
                messages.success(request, f'Turno #{turno_id} completado.')
        except ValueError as e:
            messages.error(request, str(e))

    return redirect('turnos:panel_secretaria')


def detalle_turno(request, turno_id):
    if not rol_requerido(request, 'secretaria', 'admin', 'doctor'):
        return redirect('accounts:login')

    turno = repositorio.buscar_por_id(turno_id)
    if not turno:
        messages.error(request, 'Turno no encontrado.')
        return redirect('turnos:panel_secretaria')

    return render(request, 'turnos/detalle_turno.html', {'turno': turno.to_dict()})


# ──────────────────────────────────────────────
# DOCTOR
# ──────────────────────────────────────────────

def panel_doctor(request):
    if not rol_requerido(request, 'doctor'):
        messages.error(request, 'Acceso denegado.')
        return redirect('accounts:login')

    usuario       = request.session.get('usuario')
    nombre_doctor = usuario.get('nombre_completo', '')
    fecha_filtro  = request.GET.get('fecha', '')
    todos         = repositorio.todos()

    if fecha_filtro:
        turnos = [t for t in todos
                  if nombre_doctor in t.medico.nombre and t.fecha == fecha_filtro]
    else:
        turnos = [t for t in todos if nombre_doctor in t.medico.nombre]

    return render(request, 'turnos/panel_doctor.html', {
        'turnos':       [t.to_dict() for t in turnos],
        'fecha_filtro': fecha_filtro,
        'doctor':       usuario.get('nombre_completo'),
    })


# ──────────────────────────────────────────────
# PACIENTE
# ──────────────────────────────────────────────

def panel_paciente(request):
    if not rol_requerido(request, 'paciente'):
        messages.error(request, 'Acceso denegado.')
        return redirect('accounts:login')

    dni    = request.GET.get('dni', '').strip()
    turnos = []

    if request.method == 'POST':
        dni    = request.POST.get('dni', '').strip()
        turnos = repositorio.buscar_por_paciente(dni)

    return render(request, 'turnos/panel_paciente.html', {
        'turnos': [t.to_dict() for t in turnos],
        'dni':    dni,
    })
