from django.db import models
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password_hash = models.CharField(max_length=255)
    rol = models.CharField(max_length=50)
    nombre_completo = models.CharField(max_length=255)
    especialidad = models.CharField(max_length=100, blank=True, null=True)
    matricula = models.CharField(max_length=50, blank=True, null=True)

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def verificar_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'username':        self.username,
            'rol':             self.rol,
            'nombre_completo': self.nombre_completo,
            'especialidad':    self.especialidad or "",
            'matricula':       self.matricula or "",
        }

    def __str__(self):
        return self.username
