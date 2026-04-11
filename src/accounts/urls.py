from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('',           views.login_view,       name='login'),
    path('login/',     views.login_view,       name='login'),
    path('logout/',    views.logout_view,      name='logout'),
    path('dashboard/', views.dashboard,        name='dashboard'),
    path('admin/',     views.panel_admin,      name='panel_admin'),
    path('auditoria/', views.panel_auditoria,  name='panel_auditoria'),
    path('pacientes/', views.panel_pacientes,  name='panel_pacientes'),
]
