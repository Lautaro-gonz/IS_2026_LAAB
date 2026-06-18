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
    dni             = models.CharField(max_length=20,  blank=True, default='')

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
            'dni':             self.dni,
        }


class AuditoriaDB(models.Model):
    fecha    = models.DateTimeField(auto_now_add=True)
    usuario  = models.CharField(max_length=100)
    rol      = models.CharField(max_length=50)
    accion   = models.CharField(max_length=50)
    detalles = models.TextField()

    class Meta:
        db_table = 'auditoria'
        ordering = ['-fecha']


def registrar_auditoria(usuario, rol, accion, detalles):
    AuditoriaDB.objects.create(
        usuario=usuario,
        rol=rol,
        accion=accion,
        detalles=detalles
    )


def inicializar_usuarios():
    demos = [
        {'username': 'admin',      'password': 'admin123', 'rol': 'admin',      'nombre_completo': 'Administrador'},
        {'username': 'secretaria', 'password': 'secre123', 'rol': 'secretaria', 'nombre_completo': 'Maria Secretaria'},
        {'username': 'doctor1',    'password': 'doc123',   'rol': 'doctor',     'nombre_completo': 'Ana Garcia',
         'especialidad': 'Clínica Médica',  'matricula': 'MP-1001'},
        {'username': 'doctor2',    'password': 'doc123',   'rol': 'doctor',     'nombre_completo': 'Carlos Lopez',
         'especialidad': 'Pediatría',       'matricula': 'MP-1002'},
        {'username': 'doctor3',    'password': 'doc123',   'rol': 'doctor',     'nombre_completo': 'Laura Martinez',
         'especialidad': 'Cardiología',     'matricula': 'MP-1003'},
        {'username': 'doctor4',    'password': 'doc123',   'rol': 'doctor',     'nombre_completo': 'Sofia Romero',
         'especialidad': 'Ginecología',     'matricula': 'MP-1004'},
        {'username': 'doctor5',    'password': 'doc123',   'rol': 'doctor',     'nombre_completo': 'Diego Fernandez',
         'especialidad': 'Traumatología',   'matricula': 'MP-1005'},
        {'username': 'doctor6',    'password': 'doc123',   'rol': 'doctor',     'nombre_completo': 'Valeria Torres',
         'especialidad': 'Dermatología',    'matricula': 'MP-1006'},
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
