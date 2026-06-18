from django.urls import path
from . import views

app_name = 'turnos'

urlpatterns = [
    path('secretaria/',              views.panel_secretaria,        name='panel_secretaria'),
    path('crear/',                   views.crear_turno,             name='crear_turno'),
    path('accion/<int:turno_id>/',   views.accion_turno,            name='accion_turno'),
    path('detalle/<int:turno_id>/',  views.detalle_turno,           name='detalle_turno'),
    path('doctor/',                  views.panel_doctor,            name='panel_doctor'),
    path('paciente/',                views.panel_paciente,          name='panel_paciente'),
    path('notificaciones/',          views.historial_notificaciones, name='notificaciones'),
    path('inflacion/',               views.cargar_inflacion,        name='cargar_inflacion'),
    path('inflacion/indec/',         views.obtener_indec,           name='obtener_indec'),
    path('estadisticas/',            views.estadisticas,            name='estadisticas'),
    path('estadisticas/txt/',        views.descargar_txt,           name='descargar_txt'),
    path('estadisticas/pdf/',        views.descargar_pdf,           name='descargar_pdf'),
    path('api/disponibilidad-dia/',  views.disponibilidad_dia,      name='disponibilidad_dia'),
    path('api/disponibilidad-mes/',  views.disponibilidad_mes,      name='disponibilidad_mes'),
]
