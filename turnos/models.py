from django.db import models
from accounts.models import Usuario

class ObraSocial(models.Model):
    nombre = models.CharField(max_length=255, unique=True)
    cobertura = models.FloatField()
    activa = models.BooleanField(default=True)
    motivo_baja = models.CharField(max_length=255, blank=True, null=True)
    creada_en = models.CharField(max_length=50) # To match the existing string format

    def to_dict(self):
        return {
            'nombre':      self.nombre,
            'cobertura':   self.cobertura,
            'activa':      self.activa,
            'motivo_baja': self.motivo_baja or "",
            'creada_en':   self.creada_en,
        }

    def __str__(self):
        return self.nombre


class Medico(models.Model):
    nombre = models.CharField(max_length=255)
    especialidad = models.CharField(max_length=100)
    matricula = models.CharField(max_length=50, unique=True)
    hora_inicio = models.CharField(max_length=10, default="08:00")
    hora_fin = models.CharField(max_length=10, default="12:00")
    duracion_min = models.IntegerField(default=30)

    def to_dict(self):
        return {
            'nombre':       self.nombre,
            'especialidad': self.especialidad,
            'matricula':    self.matricula,
            'hora_inicio':  self.hora_inicio,
            'hora_fin':     self.hora_fin,
            'duracion_min': self.duracion_min,
        }

    def generar_horarios(self):
        from datetime import datetime, timedelta
        horarios = []
        inicio = datetime.strptime(self.hora_inicio, "%H:%M")
        fin    = datetime.strptime(self.hora_fin,    "%H:%M")
        while inicio < fin:
            horarios.append(inicio.strftime("%H:%M"))
            inicio += timedelta(minutes=self.duracion_min)
        return horarios

    def __str__(self):
        return f"{self.nombre} - {self.especialidad}"


class Paciente(models.Model):
    nombre = models.CharField(max_length=255)
    dni = models.CharField(max_length=50, unique=True)
    telefono = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    obra_social = models.ForeignKey(ObraSocial, on_delete=models.SET_NULL, null=True, blank=True)

    def to_dict(self):
        return {
            'nombre': self.nombre,
            'dni': self.dni,
            'telefono': self.telefono,
            'email': self.email,
            'obra_social': self.obra_social.nombre if self.obra_social else None
        }

    def __str__(self):
        return self.nombre


class Turno(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    fecha = models.CharField(max_length=20)
    hora = models.CharField(max_length=10)
    estado = models.CharField(max_length=50, default="PENDIENTE")
    
    # Costos
    costo_total = models.FloatField(default=10000.0)
    cubre_os = models.FloatField(default=0.0)
    paga_paciente = models.FloatField(default=10000.0)
    detalle_costo = models.CharField(max_length=255, blank=True, null=True)
    
    motivo_cancelacion = models.CharField(max_length=255, blank=True, null=True)

    def to_dict(self):
        return {
            'id':                self.id,
            'paciente':          self.paciente.nombre,
            'dni':               self.paciente.dni,
            'medico':            self.medico.nombre,
            'especialidad':      self.medico.especialidad,
            'fecha':             self.fecha,
            'hora':              self.hora,
            'estado':            self.estado,
            'costo':             {
                'costo_total': self.costo_total,
                'cubre_os': self.cubre_os,
                'paga_paciente': self.paga_paciente,
                'detalle': self.detalle_costo
            },
            'motivo_cancelacion': self.motivo_cancelacion or "",
        }

    def _notificar(self, mensaje):
        print(f"[LOG] Turno #{self.id} | {self.estado} | {mensaje}")
        if self.paciente.email:
            print(f"[EMAIL -> {self.paciente.email}] Turno #{self.id}: {mensaje}")
        if self.paciente.telefono:
            print(f"[SMS -> {self.paciente.telefono}] Turno #{self.id}: {mensaje}")

    def confirmar(self):
        if self.estado != "PENDIENTE": raise ValueError("Solo se puede confirmar un turno PENDIENTE.")
        self.estado = "CONFIRMADO"
        self.save()
        self._notificar("Tu turno fue CONFIRMADO")
        
    def atender(self):
        if self.estado != "CONFIRMADO": raise ValueError("Solo se puede atender un turno CONFIRMADO.")
        self.estado = "EN ATENCION"
        self.save()
        self._notificar("El paciente está siendo ATENDIDO")
        
    def completar(self):
        if self.estado != "EN ATENCION": raise ValueError("Solo se puede completar un turno EN ATENCION.")
        self.estado = "COMPLETADO"
        self.save()
        self._notificar("Consulta COMPLETADA. Hasta pronto!")
        
    def cancelar(self, motivo=""):
        if self.estado in ["COMPLETADO", "CANCELADO", "EN ATENCION"]:
            raise ValueError(f"No se puede cancelar un turno en estado {self.estado}.")
        self.estado = "CANCELADO"
        self.motivo_cancelacion = motivo
        self.save()
        self._notificar(f"Tu turno fue CANCELADO. Motivo: {motivo}")
        
    def reprogramar(self, nueva_fecha, nueva_hora):
        if self.estado not in ["PENDIENTE", "CONFIRMADO"]:
            raise ValueError(f"No se puede reprogramar un turno en estado {self.estado}.")
        self.fecha = nueva_fecha
        self.hora = nueva_hora
        self.estado = "PENDIENTE"
        self.save()
        self._notificar(f"Turno REPROGRAMADO al {nueva_fecha} a las {nueva_hora}")

    def __str__(self):
        return f"Turno {self.id} - {self.paciente.nombre} con {self.medico.nombre}"


class AuditoriaLog(models.Model):
    usuario = models.CharField(max_length=255)
    rol = models.CharField(max_length=50)
    accion = models.CharField(max_length=255)
    detalle = models.TextField(blank=True, null=True)
    timestamp = models.CharField(max_length=50)

    def to_dict(self):
        return {
            'id':        self.id,
            'usuario':   self.usuario,
            'rol':       self.rol,
            'accion':    self.accion,
            'detalle':   self.detalle or "",
            'timestamp': self.timestamp,
        }

    def __str__(self):
        return f"{self.timestamp} - {self.usuario}: {self.accion}"
