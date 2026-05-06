from django.urls import path, include

urlpatterns = [
    path('', include('accounts.urls', namespace='accounts')),
    path('turnos/', include('turnos.urls', namespace='turnos')),
]
