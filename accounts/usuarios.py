from accounts.models import Usuario
from django.db.utils import OperationalError, ProgrammingError

class UsuarioRepository:
    def __init__(self):
        self._cargar_defaults()

    def _cargar_defaults(self):
        try:
            if not Usuario.objects.exists():
                defaults = [
                    ("admin",      "admin123", "admin",      "Administrador", "", ""),
                    ("secretaria", "secre123", "secretaria", "Maria Secretaria", "", ""),
                    ("doctor1",    "doc123",   "doctor",     "Ana Garcia", "Clinica Medica", "MP-1001"),
                    ("paciente1",  "pac123",   "paciente",   "Juan Perez", "", ""),
                ]
                for u in defaults:
                    usr = Usuario(username=u[0], rol=u[2], nombre_completo=u[3], especialidad=u[4], matricula=u[5])
                    usr.set_password(u[1])
                    usr.save()
        except (OperationalError, ProgrammingError):
            pass # Ignorar si la base de datos aun no esta migrada

    def buscar(self, username):
        return Usuario.objects.filter(username=username).first()

    def agregar(self, usuario):
        usuario.save()

    def todos(self):
        return list(Usuario.objects.all())

    def doctores(self):
        return list(Usuario.objects.filter(rol='doctor'))

    def existe(self, username):
        return Usuario.objects.filter(username=username).exists()

    def eliminar(self, username):
        Usuario.objects.filter(username=username).delete()

# Instancia global
usuario_repo = UsuarioRepository()
