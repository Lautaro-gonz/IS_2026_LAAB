from django.shortcuts import render, redirect
from django.contrib import messages
from .logica import (
    repositorio, validador, TurnoFactory, medico_repo,
    Paciente, ObraSocial, obra_social_repo, auditoria
)


def rol_requerido(request, *roles):
    usuario = request.session.get('usuario')
    if not usuario:
        return False
    return usuario.get('rol') in roles


def _usuario_actual(request):
    u = request.session.get('usuario', {})
    return u.get('nombre_completo', '?'), u.get('rol', '?')


# ──────────────────────────────────────────────
# SECRETARIA
# ──────────────────────────────────────────────

def panel_secretaria(request):
    if not rol_requerido(request, 'secretaria', 'admin'):
        messages.error(request, 'Acceso denegado.')
        return redirect('accounts:login')

    fecha_filtro = request.GET.get('fecha', '')
    todos = repositorio.todos()
    turnos = [t for t in todos if t.fecha == fecha_filtro] if fecha_filtro else todos

    return render(request, 'turnos/panel_secretaria.html', {
        'turnos':       [t.to_dict() for t in turnos],
        'fecha_filtro': fecha_filtro,
        'total':        len(todos),
    })


def crear_turno(request):
    if not rol_requerido(request, 'secretaria', 'admin'):
        return redirect('accounts:login')

    error   = None
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
                        nombre_u, rol_u = _usuario_actual(request)
                        auditoria.registrar(nombre_u, rol_u, 'Crear turno',
                            f'Turno #{turno.id} para {nombre} con {medico.nombre} el {fecha} {hora}')
                        messages.success(request, f'Turno #{turno.id} creado para {nombre}.')
                        return redirect('turnos:panel_secretaria')
            except Exception as e:
                error = str(e)

    return render(request, 'turnos/form_turno.html', {
        'medicos':        [(i, str(m)) for i, m in enumerate(medicos)],
        'obras_sociales': [o.nombre for o in obra_social_repo.activas()],
        'error':          error,
    })


def accion_turno(request, turno_id):
    if not rol_requerido(request, 'secretaria', 'admin'):
        return redirect('accounts:login')

    turno = repositorio.buscar_por_id(turno_id)
    if not turno:
        messages.error(request, 'Turno no encontrado.')
        return redirect('turnos:panel_secretaria')

    if request.method == 'POST':
        accion   = request.POST.get('accion')
        nombre_u, rol_u = _usuario_actual(request)
        try:
            if accion == 'confirmar':
                turno.confirmar()
                auditoria.registrar(nombre_u, rol_u, 'Confirmar turno',
                    f'Turno #{turno_id} — {turno.paciente.nombre}')
                messages.success(request, f'Turno #{turno_id} confirmado.')
            elif accion == 'cancelar':
                motivo = request.POST.get('motivo', '')
                turno.cancelar(motivo)
                auditoria.registrar(nombre_u, rol_u, 'Cancelar turno',
                    f'Turno #{turno_id} — {turno.paciente.nombre}. Motivo: {motivo}')
                messages.success(request, f'Turno #{turno_id} cancelado.')
            elif accion == 'reprogramar':
                nueva_fecha = request.POST.get('nueva_fecha')
                nueva_hora  = request.POST.get('nueva_hora')
                turno.reprogramar(nueva_fecha, nueva_hora)
                auditoria.registrar(nombre_u, rol_u, 'Reprogramar turno',
                    f'Turno #{turno_id} — nuevo: {nueva_fecha} {nueva_hora}')
                messages.success(request, f'Turno #{turno_id} reprogramado.')
            elif accion == 'atender':
                turno.atender()
                auditoria.registrar(nombre_u, rol_u, 'Atender turno',
                    f'Turno #{turno_id} — {turno.paciente.nombre}')
                messages.success(request, f'Turno #{turno_id} en atencion.')
            elif accion == 'completar':
                turno.completar()
                auditoria.registrar(nombre_u, rol_u, 'Completar turno',
                    f'Turno #{turno_id} — {turno.paciente.nombre}')
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
        turnos = [t for t in todos if nombre_doctor in t.medico.nombre and t.fecha == fecha_filtro]
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


def solicitar_turno(request):
    if not rol_requerido(request, 'paciente'):
        return redirect('accounts:login')

    medicos = medico_repo.todos()
    return render(request, 'turnos/solicitar_turno.html', {
        'medicos': [(i, m) for i, m in enumerate(medicos)],
    })


def horarios_disponibles(request):
    if not rol_requerido(request, 'paciente'):
        from django.http import JsonResponse
        return JsonResponse({'error': 'No autorizado'}, status=403)

    from django.http import JsonResponse
    from datetime import date

    medico_idx = request.GET.get('medico', '')
    fecha      = request.GET.get('fecha', '')

    if not medico_idx or not fecha:
        return JsonResponse({'horarios': []})

    try:
        medico = medico_repo.buscar_por_indice(int(medico_idx))
        if not medico:
            return JsonResponse({'horarios': []})

        hoy = date.today().strftime("%Y-%m-%d")
        if fecha < hoy:
            return JsonResponse({'horarios': [], 'error': 'Fecha pasada'})

        horarios = repositorio.horarios_disponibles(medico, fecha)
        return JsonResponse({
            'horarios':     horarios,
            'medico':       medico.nombre,
            'especialidad': medico.especialidad.value,
            'franja':       f"{medico.hora_inicio} a {medico.hora_fin}",
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


def confirmar_solicitud(request):
    if not rol_requerido(request, 'paciente'):
        return redirect('accounts:login')

    if request.method != 'POST':
        return redirect('turnos:solicitar_turno')

    usuario    = request.session.get('usuario')
    medico_idx = request.POST.get('medico', '')
    fecha      = request.POST.get('fecha', '')
    hora       = request.POST.get('hora', '')
    obra       = request.POST.get('obra_social', '')
    dni        = request.POST.get('dni', '').strip()

    if not all([medico_idx, fecha, hora, dni]):
        messages.error(request, 'Faltan datos. Volvé a intentarlo.')
        return redirect('turnos:solicitar_turno')

    try:
        from datetime import date
        hoy = date.today().strftime("%Y-%m-%d")
        if fecha < hoy:
            messages.error(request, 'No podés reservar en una fecha pasada.')
            return redirect('turnos:solicitar_turno')

        medico = medico_repo.buscar_por_indice(int(medico_idx))
        if not medico:
            messages.error(request, 'Médico no encontrado.')
            return redirect('turnos:solicitar_turno')

        ocupados = repositorio.horarios_ocupados(medico.nombre, fecha)
        if hora in ocupados:
            messages.error(request, f'El horario {hora} ya fue reservado. Elegí otro.')
            return redirect('turnos:solicitar_turno')

        os_obj   = ObraSocial(obra) if obra else None
        paciente = Paciente(
            nombre      = usuario.get('nombre_completo'),
            dni         = dni,
            obra_social = os_obj,
        )

        puede, msg = validador.validar(paciente)
        if not puede:
            messages.error(request, msg)
            return redirect('turnos:solicitar_turno')

        turno = TurnoFactory.crear(paciente, medico, fecha, hora)
        repositorio.agregar(turno)

        nombre_u, rol_u = _usuario_actual(request)
        auditoria.registrar(nombre_u, rol_u, 'Solicitar turno',
            f'Turno #{turno.id} con {medico.nombre} el {fecha} a las {hora}')

        messages.success(request, f'Turno #{turno.id} reservado para el {fecha} a las {hora}.')
        return redirect('turnos:panel_paciente')

    except Exception as e:
        messages.error(request, f'Error al reservar: {e}')
        return redirect('turnos:solicitar_turno')