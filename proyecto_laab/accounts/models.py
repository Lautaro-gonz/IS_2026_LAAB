from django.db import models
from werkzeug.security import generate_password_hash, check_password_hash


class UsuarioDB(models.Model):
    ROL_CHOICES = [
        ('admin',      'Administrador'),
        ('secretaria', 'Secretaria'),
        ('doctor',     'Doctor'),
        ('paciente',   'Paciente'),
    ]
    username        = models.CharField(max_length=50, unique=True)
    password_hash   = models.CharField(max_length=256)
    rol             = models.CharField(max_length=20, choices=ROL_CHOICES)
    nombre_completo = models.CharField(max_length=100)
    especialidad    = models.CharField(max_length=100, blank=True, default='')
    matricula       = models.CharField(max_length=50,  blank=True, default='')

    class Meta:
        db_table = 'usuarios'

    def set_password(self, raw):
        self.password_hash = generate_password_hash(raw)

    def verificar_password(self, raw):
        return check_password_hash(self.password_hash, raw)

    def to_dict(self):
        return {
            'username':        self.username,
            'rol':             self.rol,
            'nombre_completo': self.nombre_completo,
            'especialidad':    self.especialidad,
            'matricula':       self.matricula,
        }


def inicializar_usuarios():
    demos = [
        {'username': 'admin',      'password': 'admin123', 'rol': 'admin',      'nombre_completo': 'Administrador'},
        {'username': 'secretaria', 'password': 'secre123', 'rol': 'secretaria', 'nombre_completo': 'Maria Secretaria'},
        {'username': 'doctor1',    'password': 'doc123',   'rol': 'doctor',     'nombre_completo': 'Ana Garcia',
         'especialidad': 'Clinica Medica', 'matricula': 'MP-1001'},
        {'username': 'paciente1',  'password': 'pac123',   'rol': 'paciente',   'nombre_completo': 'Juan Perez'},
    ]
    for d in demos:
        if not UsuarioDB.objects.filter(username=d['username']).exists():
            u = UsuarioDB(
                username=d['username'],
                rol=d['rol'],
                nombre_completo=d['nombre_completo'],
                especialidad=d.get('especialidad', ''),
                matricula=d.get('matricula', ''),
            )
            u.set_password(d['password'])
            u.save()
