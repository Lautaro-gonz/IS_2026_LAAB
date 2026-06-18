from django.db import models


class TurnoDB(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE',   'Pendiente'),
        ('CONFIRMADO',  'Confirmado'),
        ('EN ATENCION', 'En Atención'),
        ('COMPLETADO',  'Completado'),
        ('CANCELADO',   'Cancelado'),
        ('AUSENTE',     'Ausente'),
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
    motivo_consulta      = models.CharField(max_length=500, blank=True, default='')
    notas_medico         = models.TextField(blank=True, default='')
    costo_anterior       = models.FloatField(null=True, blank=True)
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
            'motivo_consulta':    self.motivo_consulta,
            'notas_medico':       self.notas_medico,
            'costo_anterior':     self.costo_anterior,
            'costo': {
                'costo_total':   self.costo_total,
                'cubre_os':      self.cubre_os,
                'paga_paciente': self.paga_paciente,
                'detalle':       self.detalle_costo,
            },
        }


class ObraSocialDB(models.Model):
    nombre    = models.CharField(max_length=100, unique=True)
    cobertura = models.FloatField(default=0.0)

    class Meta:
        db_table = 'obras_sociales'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} (cubre {self.cobertura}%)"

    def to_dict(self):
        return {
            'id':        self.pk,
            'nombre':    self.nombre,
            'cobertura': self.cobertura,
        }


class NotificacionDB(models.Model):
    TIPO_CHOICES = [
        ('EMAIL',   'Email'),
        ('SMS',     'SMS'),
        ('SISTEMA', 'Sistema'),
    ]
    turno        = models.ForeignKey(TurnoDB, on_delete=models.CASCADE, related_name='notificaciones')
    tipo         = models.CharField(max_length=10, choices=TIPO_CHOICES)
    destinatario = models.CharField(max_length=100)
    mensaje      = models.TextField()
    leida        = models.BooleanField(default=False)
    enviado_en   = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notificaciones'
        ordering = ['-enviado_en']

    def __str__(self):
        return f"[{self.tipo}] Turno #{self.turno_id} → {self.destinatario}"


class InflacionDB(models.Model):
    periodo       = models.CharField(max_length=7, unique=True)  # YYYY-MM
    porcentaje    = models.FloatField()
    fuente        = models.CharField(max_length=200, blank=True, default='Manual')
    registrado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'inflacion'
        ordering = ['-registrado_en']

    def __str__(self):
        return f"{self.periodo} — {self.porcentaje}%"
