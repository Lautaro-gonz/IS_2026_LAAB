from django.urls import path
from . import views

app_name = 'turnos'

urlpatterns = [
    path('secretaria/',              views.panel_secretaria, name='panel_secretaria'),
    path('crear/',                   views.crear_turno,      name='crear_turno'),
    path('accion/<int:turno_id>/',   views.accion_turno,     name='accion_turno'),
    path('detalle/<int:turno_id>/',  views.detalle_turno,    name='detalle_turno'),
    path('doctor/',                  views.panel_doctor,     name='panel_doctor'),
    path('paciente/',                views.panel_paciente,   name='panel_paciente'),
]
