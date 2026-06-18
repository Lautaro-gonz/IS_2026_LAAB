from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from datetime import date, datetime, timedelta
import calendar as cal_module
import io
import os
import json
import urllib.request
import urllib.error
from .logica import (
    validador, TurnoFactory,
    Paciente, HORARIOS, DURACIONES
)
from .models import TurnoDB, ObraSocialDB, NotificacionDB, InflacionDB
from accounts.models import UsuarioDB, registrar_auditoria


def rol_requerido(request, *roles):
    usuario = request.session.get('usuario')
    if not usuario:
        return False
    return usuario.get('rol') in roles


def _medicos_con_info():
    hoy = date.today()
    dia_semana = hoy.weekday()
    ahora = datetime.now().time()
    resultado = []
    for m in UsuarioDB.objects.filter(rol='doctor'):
        horario = HORARIOS.get(m.matricula, {})
        atiende_hoy_dia = dia_semana in horario.get('dias', [])
        horario_finalizado = False
        horario_por_comenzar = False
        if atiende_hoy_dia and horario.get('inicio') and horario.get('fin'):
            hora_inicio = datetime.strptime(horario['inicio'], '%H:%M').time()
            hora_fin    = datetime.strptime(horario['fin'],    '%H:%M').time()
            if hora_inicio <= ahora < hora_fin:
                atiende_hoy = True
            elif ahora >= hora_fin:
                atiende_hoy = False
                horario_finalizado = True
            else:
                atiende_hoy = False
                horario_por_comenzar = True
        else:
            atiende_hoy = atiende_hoy_dia
        pacientes_hoy = (
            TurnoDB.objects.filter(medico_matricula=m.matricula, fecha=hoy)
            .exclude(estado='CANCELADO')
            .count()
        ) if atiende_hoy else 0
        resultado.append({
            'id':                    m.id,
            'nombre_completo':       m.nombre_completo,
            'especialidad':          m.especialidad,
            'matricula':             m.matricula,
            'atiende_hoy':           atiende_hoy,
            'horario_finalizado':    horario_finalizado,
            'horario_por_comenzar':  horario_por_comenzar,
            'pacientes_hoy':         pacientes_hoy,
            'horario_inicio':        horario.get('inicio', ''),
            'horario_fin':           horario.get('fin', ''),
        })
    return resultado


# ── NOTIFICACIONES ────────────────────────────

class EmailObservadorDB:
    """Observador que persiste notificaciones de email en la base de datos."""
    def actualizar(self, turno_db, mensaje):
        NotificacionDB.objects.create(
            turno=turno_db,
            tipo='EMAIL',
            destinatario=turno_db.paciente_email or turno_db.paciente_nombre,
            mensaje=mensaje,
        )

_obs_email = EmailObservadorDB()


def _notificar(turno_db, mensaje, tipo='EMAIL'):
    NotificacionDB.objects.create(
        turno=turno_db,
        tipo=tipo,
        destinatario=turno_db.paciente_email or turno_db.paciente_nombre,
        mensaje=mensaje,
    )


def _es_vencido(turno_db):
    """True si el turno está PENDIENTE y su fecha+hora ya pasó."""
    if turno_db.estado != 'PENDIENTE':
        return False
    try:
        turno_dt = datetime.strptime(f"{turno_db.fecha} {turno_db.hora}", "%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return False
    return turno_dt < datetime.now()


def _log_vencido(turno_db):
    """Escribe el vencimiento en emails_log.txt."""
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        'emails_log.txt',
    )
    with open(log_path, 'a', encoding='utf-8') as f:
        f.write(f"[{now_str}] TURNO VENCIDO #{turno_db.pk}\n")
        f.write(f"  Paciente : {turno_db.paciente_nombre} | {turno_db.fecha} {turno_db.hora}\n")
        f.write(f"  Médico   : {turno_db.medico_nombre}\n")
        f.write(f"  NOTIF→PACIENTE : Turno vencido — cancelado automáticamente. Se solicitó reagendar.\n")
        f.write(f"  NOTIF→ADMIN    : Turno #{turno_db.pk} de {turno_db.paciente_nombre} venció sin confirmar.\n")
        f.write(f"  {'─' * 60}\n")


def _procesar_vencido(turno_db, usuario_log, rol_log):
    """Cancela el turno vencido, crea dos notificaciones y escribe el log."""
    turno_db.estado = 'CANCELADO'
    turno_db.motivo_cancelacion = 'Turno vencido — no fue confirmado a tiempo'
    turno_db.save()

    msg_paciente = (
        f"Tu turno del {turno_db.fecha} a las {turno_db.hora} con el Dr/a. {turno_db.medico_nombre} "
        f"no pudo confirmarse porque el horario ya pasó. "
        f"Por favor comunicate con la clínica para reagendar tu turno. "
        f"Disculpá los inconvenientes."
    )
    _notificar(turno_db, msg_paciente, tipo='SISTEMA')

    msg_admin = (
        f"El turno #{turno_db.pk} del paciente {turno_db.paciente_nombre} venció sin confirmar. "
        f"Fue cancelado automáticamente. Se notificó al paciente para que reagende."
    )
    NotificacionDB.objects.create(
        turno=turno_db,
        tipo='SISTEMA',
        destinatario='admin',
        mensaje=msg_admin,
    )

    _log_vencido(turno_db)
    registrar_auditoria(
        usuario_log, rol_log, 'TURNO_VENCIDO',
        f"Turno #{turno_db.pk} de {turno_db.paciente_nombre} cancelado por vencimiento.",
    )


# ── SECRETARIA ────────────────────────────────

def panel_secretaria(request):
    if not rol_requerido(request, 'secretaria', 'admin'):
        messages.error(request, 'Acceso denegado.')
        return redirect('accounts:login')

    fecha_filtro = request.GET.get('fecha', '').strip()
    fecha_obj = None
    if fecha_filtro:
        try:
            fecha_obj = date.fromisoformat(fecha_filtro)
        except ValueError:
            fecha_filtro = ''

    qs = TurnoDB.objects.all()
    if fecha_obj:
        qs = qs.filter(fecha=fecha_obj)

    ahora = datetime.now()

    def _vencido_dict(t):
        d = t.to_dict()
        if t.estado == 'PENDIENTE':
            try:
                turno_dt = datetime.strptime(f"{t.fecha} {t.hora}", "%Y-%m-%d %H:%M")
                d['vencido'] = turno_dt < ahora
            except (ValueError, TypeError):
                d['vencido'] = False
        else:
            d['vencido'] = False
        return d

    base = TurnoDB.objects.filter(fecha=fecha_obj) if fecha_obj else TurnoDB.objects.all()
    context = {
        'turnos':       [_vencido_dict(t) for t in qs.order_by('fecha', 'hora')],
        'fecha_filtro': fecha_filtro,
        'total':        base.count(),
        'pendientes':   base.filter(estado='PENDIENTE').count(),
        'confirmados':  base.filter(estado='CONFIRMADO').count(),
        'en_atencion':  base.filter(estado='EN ATENCION').count(),
        'completados':  base.filter(estado='COMPLETADO').count(),
        'cancelados':   base.filter(estado='CANCELADO').count(),
        'ausentes':     base.filter(estado='AUSENTE').count(),
    }
    return render(request, 'turnos/panel_secretaria.html', context)


def crear_turno(request):
    if not rol_requerido(request, 'secretaria', 'admin'):
        return redirect('accounts:login')

    error = None

    if request.method == 'POST':
        nombre         = request.POST.get('nombre', '').strip()
        dni            = request.POST.get('dni', '').strip()
        telefono       = request.POST.get('telefono', '').strip()
        email          = request.POST.get('email', '').strip()
        obra           = request.POST.get('obra_social', '')
        medico_i       = request.POST.get('medico', '')
        fecha          = request.POST.get('fecha', '').strip()
        hora           = request.POST.get('hora', '').strip()
        motivo_consulta = request.POST.get('motivo_consulta', '').strip()

        if not all([nombre, dni, medico_i, fecha, hora]):
            error = 'Completa todos los campos obligatorios.'
        elif not dni.isdigit() or not (7 <= len(dni) <= 8):
            error = 'El DNI debe contener solo números y tener 7 u 8 dígitos.'
        elif telefono and (not telefono.isdigit() or not (7 <= len(telefono) <= 15)):
            error = 'El teléfono debe contener solo números (7 a 15 dígitos).'
        else:
            try:
                try:
                    os_obj = ObraSocialDB.objects.get(nombre=obra) if obra else None
                except ObraSocialDB.DoesNotExist:
                    os_obj = None
                paciente = Paciente(nombre, dni, telefono, email, os_obj)
                try:
                    medico = UsuarioDB.objects.get(id=int(medico_i))
                except (ValueError, UsuarioDB.DoesNotExist):
                    medico = None

                if not medico:
                    error = 'Médico no encontrado.'
                else:
                    puede, msg = validador.validar(paciente)
                    if not puede:
                        error = msg
                    else:
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
                            turno_obj = TurnoFactory.crear(paciente, medico, fecha, hora)
                            costo = turno_obj.costo
                            turno_db = TurnoDB.objects.create(
                                paciente_nombre      = paciente.nombre,
                                paciente_dni         = paciente.dni,
                                paciente_telefono    = paciente.telefono,
                                paciente_email       = paciente.email,
                                paciente_obra_social = os_obj.nombre if os_obj else '',
                                medico_nombre        = medico.nombre_completo,
                                medico_especialidad  = medico.especialidad,
                                medico_matricula     = medico.matricula,
                                fecha                = fecha,
                                hora                 = hora,
                                duracion             = turno_obj.duracion,
                                costo_total          = costo['costo_total'],
                                cubre_os             = costo['cubre_os'],
                                paga_paciente        = costo['paga_paciente'],
                                detalle_costo        = costo['detalle'],
                                motivo_consulta      = motivo_consulta,
                            )
                            _notificar(turno_db,
                                f"Turno agendado para el {fecha} a las {hora} con Dr/a. {medico.nombre_completo}.")
                            usuario_log = request.session.get('usuario', {}).get('username', 'desconocido')
                            rol_log = request.session.get('usuario', {}).get('rol', 'desconocido')
                            registrar_auditoria(usuario_log, rol_log, 'CREAR_TURNO',
                                f"Turno creado para paciente '{nombre}' con médico '{medico.nombre_completo}'.")
                            messages.success(request, f'Turno creado para {nombre}.')
                            return redirect('turnos:panel_secretaria')
            except Exception as e:
                error = str(e)

    context = {
        'medicos':        _medicos_con_info(),
        'obras_sociales': [os.nombre for os in ObraSocialDB.objects.all()],
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
        usuario_log = request.session.get('usuario', {}).get('username', 'desconocido')
        rol_log = request.session.get('usuario', {}).get('rol', 'desconocido')
        try:
            if accion == 'confirmar':
                if turno.estado != 'PENDIENTE':
                    raise ValueError('Solo se puede confirmar un turno pendiente.')
                if _es_vencido(turno):
                    _procesar_vencido(turno, usuario_log, rol_log)
                    messages.warning(request,
                        f"El turno de {turno.paciente_nombre} venció. "
                        f"Se canceló automáticamente y se notificó al paciente para que reagende su turno.")
                else:
                    turno.estado = 'CONFIRMADO'
                    turno.save()
                    _notificar(turno,
                        f"Tu turno del {turno.fecha} a las {turno.hora} con Dr/a. {turno.medico_nombre} fue confirmado.")
                    registrar_auditoria(usuario_log, rol_log, 'CONFIRMAR_TURNO', f"Turno #{turno_id} confirmado.")
                    messages.success(request, f'Turno #{turno_id} confirmado.')

            elif accion == 'cancelar_vencido':
                if turno.estado != 'PENDIENTE':
                    raise ValueError('Solo se puede procesar el vencimiento de un turno pendiente.')
                if not _es_vencido(turno):
                    raise ValueError('El turno aún no está vencido.')
                _procesar_vencido(turno, usuario_log, rol_log)
                messages.warning(request,
                    f"El turno de {turno.paciente_nombre} venció. "
                    f"Se canceló automáticamente y se notificó al paciente para que reagende su turno.")

            elif accion == 'cancelar':
                if turno.estado not in ['PENDIENTE', 'CONFIRMADO']:
                    raise ValueError('No se puede cancelar en este estado.')
                fecha_hora = datetime.fromisoformat(f"{turno.fecha} {turno.hora}")
                if datetime.now() + timedelta(hours=24) > fecha_hora:
                    raise ValueError('No se puede cancelar con menos de 24 horas de anticipación.')
                turno.motivo_cancelacion = request.POST.get('motivo', '')
                turno.estado = 'CANCELADO'
                turno.save()
                _notificar(turno,
                    f"Tu turno del {turno.fecha} fue cancelado. Motivo: {turno.motivo_cancelacion}",
                    tipo='SISTEMA')
                registrar_auditoria(usuario_log, rol_log, 'CANCELAR_TURNO', f"Turno #{turno_id} cancelado.")
                messages.success(request, f'Turno #{turno_id} cancelado.')

            elif accion == 'reprogramar':
                nueva_fecha = request.POST.get('nueva_fecha')
                nueva_hora  = request.POST.get('nueva_hora')
                turno.fecha = nueva_fecha
                turno.hora  = nueva_hora
                if turno.estado == 'CONFIRMADO':
                    turno.estado = 'PENDIENTE'
                turno.save()
                _notificar(turno,
                    f"Tu turno fue reprogramado para el {nueva_fecha} a las {nueva_hora}.")
                registrar_auditoria(usuario_log, rol_log, 'REPROGRAMAR_TURNO',
                    f"Turno #{turno_id} reprogramado a {nueva_fecha} {nueva_hora}.")
                messages.success(request, f'Turno #{turno_id} reprogramado.')

            elif accion == 'atender':
                if turno.estado != 'CONFIRMADO':
                    raise ValueError('El turno debe estar confirmado para atender.')
                turno.estado = 'EN ATENCION'
                turno.save()
                _notificar(turno,
                    f"Tu turno del {turno.fecha} está siendo atendido por Dr/a. {turno.medico_nombre}.",
                    tipo='SISTEMA')
                registrar_auditoria(usuario_log, rol_log, 'ATENDER_TURNO', f"Turno #{turno_id} en atención.")
                messages.success(request, f'Turno #{turno_id} en atención.')

            elif accion == 'completar':
                if turno.estado != 'EN ATENCION':
                    raise ValueError('El turno debe estar en atención para completar.')
                notas = request.POST.get('notas_medico', '').strip()
                turno.notas_medico = notas
                turno.estado = 'COMPLETADO'
                turno.save()
                _notificar(turno,
                    f"Tu consulta del {turno.fecha} con Dr/a. {turno.medico_nombre} fue completada.",
                    tipo='SISTEMA')
                registrar_auditoria(usuario_log, rol_log, 'COMPLETAR_TURNO', f"Turno #{turno_id} completado.")
                messages.success(request, f'Turno #{turno_id} completado.')

            elif accion == 'ausente':
                if turno.estado != 'CONFIRMADO':
                    raise ValueError('Solo se puede marcar como ausente un turno confirmado.')
                turno.estado = 'AUSENTE'
                turno.save()
                _notificar(turno,
                    f"El paciente no se presentó al turno del {turno.fecha} a las {turno.hora}.",
                    tipo='SISTEMA')
                registrar_auditoria(usuario_log, rol_log, 'AUSENTE_TURNO', f"Turno #{turno_id} marcado como ausente.")
                messages.success(request, f'Turno #{turno_id} marcado como ausente.')

        except ValueError as e:
            messages.error(request, str(e))

    if request.POST.get('next') == 'admin':
        return redirect('accounts:panel_admin')
    if request.POST.get('next') == 'doctor':
        return redirect('turnos:panel_doctor')
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

    usuario = request.session.get('usuario', {})
    nombre_paciente = usuario.get('nombre_completo', '')
    username = usuario.get('username', '')

    error = None
    if request.method == 'POST':
        dni             = request.POST.get('dni', '').strip()
        telefono        = request.POST.get('telefono', '').strip()
        email           = request.POST.get('email', '').strip()
        obra            = request.POST.get('obra_social', '')
        medico_i        = request.POST.get('medico', '')
        fecha           = request.POST.get('fecha', '').strip()
        hora            = request.POST.get('hora', '').strip()
        motivo_consulta = request.POST.get('motivo_consulta', '').strip()

        if not all([dni, medico_i, fecha, hora]):
            error = 'Completa todos los campos obligatorios.'
        elif not dni.isdigit() or not (7 <= len(dni) <= 8):
            error = 'El DNI debe contener solo números y tener 7 u 8 dígitos.'
        elif telefono and (not telefono.isdigit() or not (7 <= len(telefono) <= 15)):
            error = 'El teléfono debe contener solo números (7 a 15 dígitos).'
        else:
            try:
                try:
                    os_obj = ObraSocialDB.objects.get(nombre=obra) if obra else None
                except ObraSocialDB.DoesNotExist:
                    os_obj = None
                paciente = Paciente(nombre_paciente, dni, telefono, email, os_obj)
                try:
                    medico = UsuarioDB.objects.get(id=int(medico_i))
                except (ValueError, UsuarioDB.DoesNotExist):
                    medico = None

                if not medico:
                    error = 'Médico no encontrado.'
                else:
                    puede, msg = validador.validar(paciente)
                    if not puede:
                        error = msg
                    else:
                        if TurnoDB.objects.filter(
                            medico_matricula=medico.matricula,
                            fecha=fecha, hora=hora
                        ).exclude(estado='CANCELADO').exists():
                            error = f'El médico ya tiene un turno a las {hora} el {fecha}.'
                        elif TurnoDB.objects.filter(
                            paciente_dni=dni, fecha=fecha
                        ).exclude(estado='CANCELADO').exists():
                            error = f'Ya tienes un turno agendado el {fecha}.'
                        else:
                            turno_obj = TurnoFactory.crear(paciente, medico, fecha, hora)
                            costo = turno_obj.costo
                            turno_db = TurnoDB.objects.create(
                                paciente_nombre      = paciente.nombre,
                                paciente_dni         = paciente.dni,
                                paciente_telefono    = paciente.telefono,
                                paciente_email       = paciente.email,
                                paciente_obra_social = os_obj.nombre if os_obj else '',
                                medico_nombre        = medico.nombre_completo,
                                medico_especialidad  = medico.especialidad,
                                medico_matricula     = medico.matricula,
                                fecha                = fecha,
                                hora                 = hora,
                                duracion             = turno_obj.duracion,
                                costo_total          = costo['costo_total'],
                                cubre_os             = costo['cubre_os'],
                                paga_paciente        = costo['paga_paciente'],
                                detalle_costo        = costo['detalle'],
                                motivo_consulta      = motivo_consulta,
                            )
                            _notificar(turno_db,
                                f"Turno solicitado para el {fecha} a las {hora} con Dr/a. {medico.nombre_completo}.")
                            registrar_auditoria(username, 'paciente', 'CREAR_TURNO',
                                f"El paciente '{nombre_paciente}' agendó un turno con '{medico.nombre_completo}'.")
                            messages.success(request, '¡Turno solicitado exitosamente!')
                            return redirect('turnos:panel_paciente')
            except Exception as e:
                error = str(e)

    turnos = TurnoDB.objects.filter(paciente_nombre=nombre_paciente).order_by('fecha', 'hora')

    return render(request, 'turnos/panel_paciente.html', {
        'turnos':          [t.to_dict() for t in turnos],
        'nombre_paciente': nombre_paciente,
        'medicos':         _medicos_con_info(),
        'obras_sociales':  [os.nombre for os in ObraSocialDB.objects.all()],
        'error':           error,
    })


# ── NOTIFICACIONES ────────────────────────────

def historial_notificaciones(request):
    usuario = request.session.get('usuario')
    if not usuario:
        return redirect('accounts:login')
    rol = usuario.get('rol')
    if rol not in ['admin', 'secretaria', 'paciente']:
        messages.error(request, 'Acceso denegado.')
        return redirect('accounts:login')

    if rol in ['admin', 'secretaria']:
        notifs = NotificacionDB.objects.select_related('turno').all()
        NotificacionDB.objects.filter(leida=False).update(leida=True)
    else:
        nombre = usuario.get('nombre_completo', '')
        notifs = NotificacionDB.objects.filter(
            turno__paciente_nombre=nombre
        ).select_related('turno')
        NotificacionDB.objects.filter(
            leida=False,
            turno__paciente_nombre=nombre,
        ).update(leida=True)

    return render(request, 'turnos/notificaciones.html', {
        'notificaciones': notifs,
    })


# ── INFLACIÓN ────────────────────────────────

_INDEC_URL = (
    'https://apis.datos.gob.ar/series/api/series/'
    '?ids=148.3_INIVELNAL_DICI_M_26&limit=2&sort=desc&representation_mode=percent_change'
)


def obtener_indec(request):
    """Consulta la API pública del INDEC y devuelve el último IPC mensual."""
    if not rol_requerido(request, 'admin'):
        return JsonResponse({'ok': False, 'error': 'Acceso denegado.'}, status=403)
    try:
        req = urllib.request.Request(
            _INDEC_URL,
            headers={'User-Agent': 'laab-clinica/1.0', 'Accept': 'application/json'},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))

        # Tomar el primer punto con valor no nulo (el más reciente puede estar pendiente)
        punto = next((p for p in data['data'] if p[1] is not None), None)
        if punto is None:
            raise ValueError('El INDEC aún no publicó el dato del último período.')
        fecha_str  = punto[0]          # "2024-10-01"
        porcentaje = round(float(punto[1]), 2)  # ya viene como variación % (ej: 3.3)
        periodo    = fecha_str[:7]     # "2024-10"

        return JsonResponse({
            'ok':               True,
            'porcentaje':       porcentaje,
            'periodo':          periodo,
            'fecha_publicacion': fecha_str,
            'fuente':           f'INDEC — IPC Nacional · publicado {fecha_str}',
        })

    except urllib.error.URLError:
        return JsonResponse({
            'ok':    False,
            'error': 'No se pudo conectar con el INDEC. Podés ingresar el porcentaje manualmente.',
        })
    except (KeyError, IndexError, ValueError, TypeError) as exc:
        return JsonResponse({
            'ok':    False,
            'error': f'Error al procesar la respuesta del INDEC: {exc}',
        })


def cargar_inflacion(request):
    if not rol_requerido(request, 'admin'):
        messages.error(request, 'Acceso denegado.')
        return redirect('accounts:login')

    error          = None
    resultado      = None   # resultado del ajuste aplicado
    historial      = InflacionDB.objects.all()
    usuario_log    = request.session.get('usuario', {}).get('username', 'admin')

    if request.method == 'POST':
        accion = request.POST.get('accion', 'registrar')

        # ── Registrar nuevo porcentaje ──────────────────────────────────
        if accion == 'registrar':
            periodo      = request.POST.get('periodo', '').strip()
            porcentaje_s = request.POST.get('porcentaje', '').strip()
            try:
                if not periodo or len(periodo) != 7 or periodo[4] != '-':
                    raise ValueError('Período inválido. Formato esperado: YYYY-MM (ej: 2025-01)')
                porcentaje = float(porcentaje_s)
                if porcentaje <= 0:
                    raise ValueError('El porcentaje debe ser mayor a 0.')
                fuente = request.POST.get('fuente', 'Manual').strip() or 'Manual'
                InflacionDB.objects.update_or_create(
                    periodo=periodo,
                    defaults={'porcentaje': porcentaje, 'fuente': fuente},
                )
                registrar_auditoria(usuario_log, 'admin', 'CARGAR_INFLACION',
                    f"Inflación {periodo}: {porcentaje}% (fuente: {fuente})")
                messages.success(request, f'Inflación {periodo} registrada: {porcentaje}%.')
                return redirect('turnos:cargar_inflacion')
            except ValueError as e:
                error = str(e)

        # ── Aplicar ajuste sobre turnos futuros ────────────────────────
        elif accion == 'aplicar':
            try:
                inflacion = InflacionDB.objects.latest('registrado_en')
            except InflacionDB.DoesNotExist:
                error = 'No hay porcentaje de inflación registrado. Cargá uno primero.'
                inflacion = None

            if inflacion:
                porcentaje = inflacion.porcentaje
                factor     = 1 + porcentaje / 100
                hoy        = date.today()

                turnos_futuros = TurnoDB.objects.filter(
                    fecha__gte=hoy,
                    estado__in=['PENDIENTE', 'CONFIRMADO'],
                )

                detalle = []
                for turno in turnos_futuros:
                    precio_anterior = turno.costo_total
                    turno.costo_anterior = precio_anterior
                    turno.costo_total    = round(precio_anterior        * factor, 2)
                    turno.cubre_os       = round(turno.cubre_os         * factor, 2)
                    turno.paga_paciente  = round(turno.paga_paciente    * factor, 2)
                    turno.save()
                    detalle.append({
                        'id':              turno.pk,
                        'paciente':        turno.paciente_nombre,
                        'fecha':           str(turno.fecha),
                        'precio_anterior': precio_anterior,
                        'precio_nuevo':    turno.costo_total,
                    })

                resultado = {
                    'porcentaje': porcentaje,
                    'periodo':    inflacion.periodo,
                    'cantidad':   len(detalle),
                    'detalle':    detalle,
                }
                registrar_auditoria(
                    usuario_log, 'admin', 'APLICAR_INFLACION',
                    f"Ajuste {porcentaje}% ({inflacion.periodo}) aplicado a {len(detalle)} turno(s).",
                )

    return render(request, 'turnos/cargar_inflacion.html', {
        'historial': InflacionDB.objects.all(),
        'error':     error,
        'resultado': resultado,
    })


# ── ESTADÍSTICAS ─────────────────────────────

_DIAS   = ['Lunes','Martes','Miércoles','Jueves','Viernes','Sábado','Domingo']
_MESES  = ['Enero','Febrero','Marzo','Abril','Mayo','Junio',
           'Julio','Agosto','Septiembre','Octubre','Noviembre','Diciembre']
_COLS   = ['fecha','especialidad','estado','duracion_min','costo_total','cubre_os',
           'paga_paciente','obra_social','dias_anticipacion','franja_horaria',
           'porcentaje_cobertura','dia_semana','mes','notif_enviadas','motivo_consulta']


def _franja(hora_str):
    try:
        h = int(hora_str.split(':')[0])
        return 'mañana' if h < 12 else ('tarde' if h < 17 else 'noche')
    except (ValueError, IndexError):
        return ''


def _fila(t):
    dias_ant = (t.fecha - t.creado_en.date()).days if t.creado_en else 0
    pct      = round(t.cubre_os / t.costo_total * 100, 1) if t.costo_total else 0
    return [
        str(t.fecha), t.medico_especialidad, t.estado, str(t.duracion),
        str(round(t.costo_total, 2)), str(round(t.cubre_os, 2)),
        str(round(t.paga_paciente, 2)), t.paciente_obra_social or 'Sin OS',
        str(dias_ant), _franja(t.hora), str(pct),
        _DIAS[t.fecha.weekday()], _MESES[t.fecha.month - 1],
        str(t.notificaciones.count()), t.motivo_consulta or '',
    ]


def estadisticas(request):
    if not rol_requerido(request, 'admin', 'secretaria'):
        messages.error(request, 'Acceso denegado.')
        return redirect('accounts:login')

    turnos = TurnoDB.objects.prefetch_related('notificaciones').order_by('fecha', 'hora')
    resumen = {
        'total':       turnos.count(),
        'completados': turnos.filter(estado='COMPLETADO').count(),
        'cancelados':  turnos.filter(estado='CANCELADO').count(),
        'ausentes':    turnos.filter(estado='AUSENTE').count(),
        'con_motivo':  turnos.exclude(motivo_consulta='').count(),
        'con_os':      turnos.exclude(paciente_obra_social='').count(),
    }
    return render(request, 'turnos/estadisticas.html', {
        'resumen':  resumen,
        'columnas': _COLS,
    })


def descargar_txt(request):
    if not rol_requerido(request, 'admin', 'secretaria'):
        return HttpResponse('Acceso denegado', status=403)

    turnos = TurnoDB.objects.prefetch_related('notificaciones').order_by('fecha', 'hora')
    lineas = ['\t'.join(_COLS)]
    for t in turnos:
        lineas.append('\t'.join(_fila(t)))

    resp = HttpResponse('\n'.join(lineas), content_type='text/plain; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="turnos_estadistica_{date.today()}.txt"'
    return resp


def descargar_pdf(request):
    if not rol_requerido(request, 'admin', 'secretaria'):
        return HttpResponse('Acceso denegado', status=403)
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError:
        return HttpResponse('reportlab no instalado. Ejecutá: pip install reportlab', status=500)

    turnos = list(TurnoDB.objects.prefetch_related('notificaciones').order_by('fecha', 'hora'))
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                            leftMargin=18, rightMargin=18,
                            topMargin=28, bottomMargin=28)
    styles   = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph('Estadística de Turnos — Clínica LAAB', styles['Title']))
    elements.append(Paragraph(
        f'Generado el {date.today().strftime("%d/%m/%Y")} · {len(turnos)} turno(s)',
        styles['Normal']))
    elements.append(Spacer(1, 14))

    data  = [_COLS] + [_fila(t) for t in turnos]
    col_w = [52, 68, 58, 42, 52, 48, 52, 68, 52, 46, 58, 52, 46, 42, 76]

    estilo = [
        ('BACKGROUND',    (0,0), (-1,0),  colors.HexColor('#1a56db')),
        ('TEXTCOLOR',     (0,0), (-1,0),  colors.white),
        ('FONTNAME',      (0,0), (-1,0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0,0), (-1,0),  6.5),
        ('FONTSIZE',      (0,1), (-1,-1), 6),
        ('GRID',          (0,0), (-1,-1), 0.35, colors.HexColor('#e4e9f5')),
        ('ALIGN',         (0,0), (-1,-1), 'CENTER'),
        ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING',    (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            estilo.append(('BACKGROUND', (0,i), (-1,i), colors.HexColor('#f0f4ff')))

    table = Table(data, colWidths=col_w, repeatRows=1)
    table.setStyle(TableStyle(estilo))
    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    resp = HttpResponse(buffer, content_type='application/pdf')
    resp['Content-Disposition'] = f'attachment; filename="turnos_estadistica_{date.today()}.pdf"'
    return resp


# ── API DISPONIBILIDAD ────────────────────────

def disponibilidad_dia(request):
    medico_idx = request.GET.get('medico', '')
    fecha_str  = request.GET.get('fecha', '')
    if not medico_idx or not fecha_str:
        return JsonResponse({'error': 'Parámetros faltantes'}, status=400)
    try:
        medico    = UsuarioDB.objects.get(id=int(medico_idx))
        fecha_obj = date.fromisoformat(fecha_str)
    except (ValueError, TypeError, UsuarioDB.DoesNotExist):
        return JsonResponse({'error': 'Parámetros inválidos'}, status=400)
    if not medico:
        return JsonResponse({'error': 'Médico no encontrado'}, status=404)
    if fecha_obj < date.today():
        return JsonResponse({'disponible': False, 'slots': [], 'razon': 'Fecha pasada'})

    horario    = HORARIOS.get(medico.matricula, {})
    dia_semana = fecha_obj.weekday()
    if dia_semana not in horario.get('dias', []):
        return JsonResponse({'disponible': False, 'slots': [], 'razon': 'El médico no atiende este día'})

    duracion = DURACIONES.get(medico.especialidad, 20)
    inicio   = datetime.strptime(horario['inicio'], '%H:%M')
    fin      = datetime.strptime(horario['fin'],    '%H:%M')

    ocupados = set(
        TurnoDB.objects.filter(
            medico_matricula=medico.matricula, fecha=fecha_str
        ).exclude(estado='CANCELADO').values_list('hora', flat=True)
    )

    ahora = datetime.now()

    slots, current = [], inicio
    while current + timedelta(minutes=duracion) <= fin:
        hora_str = current.strftime('%H:%M')
        if fecha_obj == date.today():
            hora_slot = datetime.strptime(hora_str, '%H:%M').replace(
                year=ahora.year, month=ahora.month, day=ahora.day)
            if hora_slot <= ahora:
                current += timedelta(minutes=duracion)
                continue
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
        medico = UsuarioDB.objects.get(id=int(medico_idx))
    except (ValueError, TypeError, UsuarioDB.DoesNotExist):
        return JsonResponse({})
    if not medico:
        return JsonResponse({})

    horario   = HORARIOS.get(medico.matricula, {})
    duracion  = DURACIONES.get(medico.especialidad, 20)
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
            inicio = datetime.strptime(horario['inicio'], '%H:%M')
            fin    = datetime.strptime(horario['fin'],    '%H:%M')

            if fecha == hoy:
                ahora = datetime.now()
                total = 0
                current = inicio
                while current + timedelta(minutes=duracion) <= fin:
                    slot_dt = current.replace(
                        year=ahora.year, month=ahora.month, day=ahora.day)
                    if slot_dt > ahora:
                        total += 1
                    current += timedelta(minutes=duracion)
                hora_ahora_str = ahora.strftime('%H:%M')
                ocupados = TurnoDB.objects.filter(
                    medico_matricula=medico.matricula, fecha=fecha
                ).exclude(estado='CANCELADO').filter(hora__gt=hora_ahora_str).count()
            else:
                total = int((fin - inicio).total_seconds() // 60) // duracion
                ocupados = TurnoDB.objects.filter(
                    medico_matricula=medico.matricula, fecha=fecha
                ).exclude(estado='CANCELADO').count()

            if total == 0 or ocupados >= total:
                resultado[dia] = 'lleno'
            elif ocupados == 0:
                resultado[dia] = 'disponible'
            else:
                resultado[dia] = 'parcial'

    return JsonResponse(resultado)
