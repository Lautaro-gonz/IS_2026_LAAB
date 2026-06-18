from datetime import datetime, timedelta
from django.shortcuts import redirect

TIMEOUT_MINUTOS = 15


class SesionInactivaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.session.get('usuario'):
            ultima = request.session.get('ultima_actividad')
            if ultima:
                diferencia = datetime.now() - datetime.fromisoformat(ultima)
                if diferencia > timedelta(minutes=TIMEOUT_MINUTOS):
                    request.session.flush()
                    return redirect('/login/?timeout=1')
            request.session['ultima_actividad'] = datetime.now().isoformat()

        return self.get_response(request)
