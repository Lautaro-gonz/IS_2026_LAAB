from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('',           views.login_view,   name='login'),
    path('login/',     views.login_view,   name='login'),
    path('registro/',  views.registro_view,name='registro'),
    path('logout/',    views.logout_view,  name='logout'),
    path('dashboard/', views.dashboard,    name='dashboard'),
    path('admin/',     views.panel_admin,  name='panel_admin'),
]
