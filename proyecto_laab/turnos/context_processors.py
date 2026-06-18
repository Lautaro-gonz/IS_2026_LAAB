from .models import NotificacionDB


def notificaciones_no_leidas(request):
    usuario = request.session.get('usuario')
    if not usuario:
        return {'notif_no_leidas': 0}

    rol = usuario.get('rol')

    if rol in ('admin', 'secretaria'):
        count = NotificacionDB.objects.filter(leida=False).count()
    elif rol == 'paciente':
        nombre = usuario.get('nombre_completo', '')
        count = NotificacionDB.objects.filter(
            leida=False,
            turno__paciente_nombre=nombre,
        ).count()
    else:
        count = 0

    return {'notif_no_leidas': min(count, 100)}
