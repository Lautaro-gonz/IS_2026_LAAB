from werkzeug.security import generate_password_hash, check_password_hash


class Usuario:
    def __init__(self, username, password, rol, nombre_completo,
                 especialidad="", matricula=""):
        self.username        = username
        self.password_hash   = generate_password_hash(password)
        self.rol             = rol
        self.nombre_completo = nombre_completo
        self.especialidad    = especialidad  # solo para doctores
        self.matricula       = matricula     # solo para doctores

    def verificar_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'username':        self.username,
            'rol':             self.rol,
            'nombre_completo': self.nombre_completo,
            'especialidad':    self.especialidad,
            'matricula':       self.matricula,
        }


class UsuarioRepository:
    def __init__(self):
        self._usuarios = {}
        self._cargar_defaults()

    def _cargar_defaults(self):
        defaults = [
            Usuario("admin",      "admin123", "admin",      "Administrador"),
            Usuario("secretaria", "secre123", "secretaria", "Maria Secretaria"),
            Usuario("doctor1",    "doc123",   "doctor",     "Ana Garcia",
                    especialidad="Clinica Medica", matricula="MP-1001"),
            Usuario("paciente1",  "pac123",   "paciente",   "Juan Perez"),
        ]
        for u in defaults:
            self._usuarios[u.username] = u

    def buscar(self, username):
        return self._usuarios.get(username)

    def agregar(self, usuario):
        self._usuarios[usuario.username] = usuario

    def todos(self):
        return list(self._usuarios.values())

    def doctores(self):
        return [u for u in self._usuarios.values() if u.rol == 'doctor']

    def existe(self, username):
        return username in self._usuarios

    def eliminar(self, username):
        self._usuarios.pop(username, None)


# Instancia global
usuario_repo = UsuarioRepository()
