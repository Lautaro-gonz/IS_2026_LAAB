from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from datetime import date, datetime, timedelta
import calendar as cal_module
from .logica import (
    validador, TurnoFactory, medico_repo,
    Paciente, ObraSocial, OBRAS_SOCIALES, HORARIOS, DURACIONES
)
from .models import TurnoDB


def rol_requerido(request, *roles):
    usuario = request.session.get('usuario')
    if not usuario:
        return False
    return usuario.get('rol') in roles


# ── SECRETARIA ────────────────────────────────

def panel_secretaria(request):
    if not rol_requerido(request, 'secretaria', 'admin'):
        messages.error(request, 'Acceso denegado.')
        return redirect('accounts:login')

    fecha_filtro = request.GET.get('fecha', '')
    qs = TurnoDB.objects.all()
    if fecha_filtro:
        qs = qs.filter(fecha=fecha_filtro)

    todos = TurnoDB.objects.all()
    context = {
        'turnos':       [t.to_dict() for t in qs.order_by('fecha', 'hora')],
        'fecha_filtro': fecha_filtro,
        'total':        todos.count(),
        'pendientes':   todos.filter(estado='PENDIENTE').count(),
        'confirmados':  todos.filter(estado='CONFIRMADO').count(),
        'en_atencion':  todos.filter(estado='EN ATENCION').count(),
        'completados':  todos.filter(estado='COMPLETADO').count(),
        'cancelados':   todos.filter(estado='CANCELADO').count(),
    }
    return render(request, 'turnos/panel_secretaria.html', context)


def crear_turno(request):
    if not rol_requerido(request, 'secretaria', 'admin'):
        return redirect('accounts:login')

    error  = None
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
        elif not dni.isdigit() or not (7 <= len(dni) <= 8):
            error = 'El DNI debe contener solo números y tener 7 u 8 dígitos.'
        elif telefono and (not telefono.isdigit() or not (7 <= len(telefono) <= 15)):
            error = 'El teléfono debe contener solo números (7 a 15 dígitos).'
        else:
            try:
                os_obj   = ObraSocial(obra) if obra else None
                paciente = Paciente(nombre, dni, telefono, email, os_obj)
                medico   = medico_repo.buscar_por_indice(int(medico_i))

                if not medico:
                    error = 'Médico no encontrado.'
                else:
                    puede, msg = validador.validar(paciente)
                    if not puede:
                        error = msg
                    else:
                        # Validar duplicados en BD
                        if TurnoDB.objects.filter(
                            medico_matricula=medico.matricula,
                            fecha=fecha, hora=hora
                        ).exclude(estado='CANCELADO').exists():
                            error = f'El médico ya tiene un turno a las {hora} el {fecha}.'
                        elif TurnoDB.objects.filter(
                            paciente_dni=dni, fecha=fecha
                        ).exclude(estado='CANCELADO').exists():
                            error = f'El paciente ya tiene un turno el {fecha}.'
                        else:
                            # Validar con Factory (fecha pasada, horario)
                            turno_obj = TurnoFactory.crear(paciente, medico, fecha, hora)
                            costo = turno_obj.costo
                            TurnoDB.objects.create(
                                paciente_nombre      = paciente.nombre,
                                paciente_dni         = paciente.dni,
                                paciente_telefono    = paciente.telefono,
                                paciente_email       = paciente.email,
                                paciente_obra_social = os_obj.nombre if os_obj else '',
                                medico_nombre        = medico.nombre,
                                medico_especialidad  = medico.especialidad.value,
                                medico_matricula     = medico.matricula,
                                fecha                = fecha,
                                hora                 = hora,
                                duracion             = turno_obj.duracion,
                                costo_total          = costo['costo_total'],
                                cubre_os             = costo['cubre_os'],
                                paga_paciente        = costo['paga_paciente'],
                                detalle_costo        = costo['detalle'],
                            )
                            messages.success(request, f'Turno creado para {nombre}.')
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
    if not rol_requerido(request, 'secretaria', 'admin', 'doctor'):
        return redirect('accounts:login')

    try:
        turno = TurnoDB.objects.get(pk=turno_id)
    except TurnoDB.DoesNotExist:
        messages.error(request, 'Turno no encontrado.')
        return redirect('turnos:panel_secretaria')

    if request.method == 'POST':
        accion = request.POST.get('accion')
        try:
            if accion == 'confirmar':
                if turno.estado != 'PENDIENTE':
                    raise ValueError('Solo se puede confirmar un turno pendiente.')
                turno.estado = 'CONFIRMADO'
                turno.save()
                messages.success(request, f'Turno #{turno_id} confirmado.')

            elif accion == 'cancelar':
                if turno.estado not in ['PENDIENTE', 'CONFIRMADO']:
                    raise ValueError('No se puede cancelar en este estado.')
                fecha_hora = datetime.fromisoformat(f"{turno.fecha} {turno.hora}")
                if datetime.now() + timedelta(hours=24) > fecha_hora:
                    raise ValueError('No se puede cancelar con menos de 24 horas de anticipación.')
                turno.motivo_cancelacion = request.POST.get('motivo', '')
                turno.estado = 'CANCELADO'
                turno.save()
                messages.success(request, f'Turno #{turno_id} cancelado.')

            elif accion == 'reprogramar':
                nueva_fecha = request.POST.get('nueva_fecha')
                nueva_hora  = request.POST.get('nueva_hora')
                turno.fecha = nueva_fecha
                turno.hora  = nueva_hora
                if turno.estado == 'CONFIRMADO':
                    turno.estado = 'PENDIENTE'
                turno.save()
                messages.success(request, f'Turno #{turno_id} reprogramado.')

            elif accion == 'atender':
                if turno.estado != 'CONFIRMADO':
                    raise ValueError('El turno debe estar confirmado para atender.')
                turno.estado = 'EN ATENCION'
                turno.save()
                messages.success(request, f'Turno #{turno_id} en atención.')

            elif accion == 'completar':
                if turno.estado != 'EN ATENCION':
                    raise ValueError('El turno debe estar en atención para completar.')
                turno.estado = 'COMPLETADO'
                turno.save()
                messages.success(request, f'Turno #{turno_id} completado.')

        except ValueError as e:
            messages.error(request, str(e))

    if request.POST.get('next') == 'admin':
        return redirect('accounts:panel_admin')
    return redirect('turnos:panel_secretaria')


def detalle_turno(request, turno_id):
    if not rol_requerido(request, 'secretaria', 'admin', 'doctor'):
        return redirect('accounts:login')
    try:
        turno = TurnoDB.objects.get(pk=turno_id)
    except TurnoDB.DoesNotExist:
        messages.error(request, 'Turno no encontrado.')
        return redirect('turnos:panel_secretaria')
    return render(request, 'turnos/detalle_turno.html', {'turno': turno.to_dict()})


# ── DOCTOR ────────────────────────────────────

def panel_doctor(request):
    if not rol_requerido(request, 'doctor'):
        messages.error(request, 'Acceso denegado.')
        return redirect('accounts:login')

    usuario       = request.session.get('usuario')
    nombre_doctor = usuario.get('nombre_completo', '')
    fecha_filtro  = request.GET.get('fecha', '')

    qs = TurnoDB.objects.filter(medico_nombre=nombre_doctor)
    if fecha_filtro:
        qs = qs.filter(fecha=fecha_filtro)

    return render(request, 'turnos/panel_doctor.html', {
        'turnos':       [t.to_dict() for t in qs.order_by('hora')],
        'fecha_filtro': fecha_filtro,
        'doctor':       nombre_doctor,
    })


# ── PACIENTE ──────────────────────────────────

def panel_paciente(request):
    if not rol_requerido(request, 'paciente'):
        messages.error(request, 'Acceso denegado.')
        return redirect('accounts:login')

    dni    = request.GET.get('dni', '').strip()
    turnos = []
    if request.method == 'POST':
        dni    = request.POST.get('dni', '').strip()
        turnos = TurnoDB.objects.filter(paciente_dni=dni).order_by('fecha', 'hora')

    return render(request, 'turnos/panel_paciente.html', {
        'turnos': [t.to_dict() for t in turnos],
        'dni':    dni,
    })


# ── API DISPONIBILIDAD ────────────────────────

def disponibilidad_dia(request):
    medico_idx = request.GET.get('medico', '')
    fecha_str  = request.GET.get('fecha', '')
    if not medico_idx or not fecha_str:
        return JsonResponse({'error': 'Parámetros faltantes'}, status=400)
    try:
        medico    = medico_repo.buscar_por_indice(int(medico_idx))
        fecha_obj = date.fromisoformat(fecha_str)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Parámetros inválidos'}, status=400)
    if not medico:
        return JsonResponse({'error': 'Médico no encontrado'}, status=404)
    if fecha_obj < date.today():
        return JsonResponse({'disponible': False, 'slots': [], 'razon': 'Fecha pasada'})

    horario    = HORARIOS.get(medico.matricula, {})
    dia_semana = fecha_obj.weekday()
    if dia_semana not in horario.get('dias', []):
        return JsonResponse({'disponible': False, 'slots': [], 'razon': 'El médico no atiende este día'})

    duracion = DURACIONES.get(medico.especialidad.value, 20)
    inicio   = datetime.strptime(horario['inicio'], '%H:%M')
    fin      = datetime.strptime(horario['fin'],    '%H:%M')

    ocupados = set(
        TurnoDB.objects.filter(
            medico_matricula=medico.matricula, fecha=fecha_str
        ).exclude(estado='CANCELADO').values_list('hora', flat=True)
    )

    slots, current = [], inicio
    while current + timedelta(minutes=duracion) <= fin:
        hora_str = current.strftime('%H:%M')
        if hora_str not in ocupados:
            slots.append(hora_str)
        current += timedelta(minutes=duracion)

    return JsonResponse({
        'disponible': True,
        'slots':      slots,
        'duracion':   duracion,
        'horario':    f"{horario['inicio']} — {horario['fin']}",
    })


def disponibilidad_mes(request):
    medico_idx = request.GET.get('medico', '')
    anio       = int(request.GET.get('anio', date.today().year))
    mes        = int(request.GET.get('mes',  date.today().month))
    if not medico_idx:
        return JsonResponse({})
    try:
        medico = medico_repo.buscar_por_indice(int(medico_idx))
    except (ValueError, TypeError):
        return JsonResponse({})
    if not medico:
        return JsonResponse({})

    horario   = HORARIOS.get(medico.matricula, {})
    duracion  = DURACIONES.get(medico.especialidad.value, 20)
    hoy       = date.today()
    resultado = {}

    for dia in range(1, cal_module.monthrange(anio, mes)[1] + 1):
        fecha      = date(anio, mes, dia)
        dia_semana = fecha.weekday()
        if fecha < hoy:
            resultado[dia] = 'pasado'
        elif dia_semana not in horario.get('dias', []):
            resultado[dia] = 'no_atiende'
        else:
            ocupados = TurnoDB.objects.filter(
                medico_matricula=medico.matricula, fecha=fecha
            ).exclude(estado='CANCELADO').count()
            inicio = datetime.strptime(horario['inicio'], '%H:%M')
            fin    = datetime.strptime(horario['fin'],    '%H:%M')
            total  = int((fin - inicio).total_seconds() // 60) // duracion
            if ocupados == 0:
                resultado[dia] = 'disponible'
            elif ocupados >= total:
                resultado[dia] = 'lleno'
            else:
                resultado[dia] = 'parcial'

    return JsonResponse(resultado)
