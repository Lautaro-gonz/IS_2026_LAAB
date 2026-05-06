from django.db import models


class TurnoDB(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE',   'Pendiente'),
        ('CONFIRMADO',  'Confirmado'),
        ('EN ATENCION', 'En Atención'),
        ('COMPLETADO',  'Completado'),
        ('CANCELADO',   'Cancelado'),
    ]

    paciente_nombre      = models.CharField(max_length=100)
    paciente_dni         = models.CharField(max_length=20)
    paciente_telefono    = models.CharField(max_length=30,  blank=True, default='')
    paciente_email       = models.CharField(max_length=100, blank=True, default='')
    paciente_obra_social = models.CharField(max_length=100, blank=True, default='')

    medico_nombre        = models.CharField(max_length=100)
    medico_especialidad  = models.CharField(max_length=100)
    medico_matricula     = models.CharField(max_length=20)

    fecha                = models.DateField()
    hora                 = models.CharField(max_length=10)
    estado               = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='PENDIENTE')
    duracion             = models.IntegerField(default=20)

    costo_total          = models.FloatField(default=10000.0)
    cubre_os             = models.FloatField(default=0.0)
    paga_paciente        = models.FloatField(default=10000.0)
    detalle_costo        = models.CharField(max_length=200, default='')
    motivo_cancelacion   = models.CharField(max_length=300, blank=True, default='')
    creado_en            = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'turnos'
        ordering = ['fecha', 'hora']

    def __str__(self):
        return f"#{self.pk} {self.paciente_nombre} - {self.medico_nombre} {self.fecha} {self.hora}"

    def to_dict(self):
        return {
            'id':                 self.pk,
            'paciente':           self.paciente_nombre,
            'dni':                self.paciente_dni,
            'telefono':           self.paciente_telefono,
            'email':              self.paciente_email,
            'obra_social':        self.paciente_obra_social,
            'medico':             self.medico_nombre,
            'especialidad':       self.medico_especialidad,
            'matricula':          self.medico_matricula,
            'fecha':              str(self.fecha),
            'hora':               self.hora,
            'estado':             self.estado,
            'duracion':           self.duracion,
            'motivo_cancelacion': self.motivo_cancelacion,
            'costo': {
                'costo_total':   self.costo_total,
                'cubre_os':      self.cubre_os,
                'paga_paciente': self.paga_paciente,
                'detalle':       self.detalle_costo,
            },
        }
