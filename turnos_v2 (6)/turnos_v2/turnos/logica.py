import threading
from abc import ABC, abstractmethod
from enum import Enum
from datetime import datetime, date, timedelta


# ══════════════════════════════════════════════════════════════
# OBSERVER
# ══════════════════════════════════════════════════════════════

class ObservadorTurno(ABC):
    @abstractmethod
    def actualizar(self, turno, mensaje): pass


class EmailObservador(ObservadorTurno):
    def __init__(self, email):
        self.email = email
    def actualizar(self, turno, mensaje):
        print(f"[EMAIL → {self.email}] Turno #{turno.id}: {mensaje}")


class SMSObservador(ObservadorTurno):
    def __init__(self, telefono):
        self.telefono = telefono
    def actualizar(self, turno, mensaje):
        print(f"[SMS → {self.telefono}] Turno #{turno.id}: {mensaje}")


class ConsoleObservador(ObservadorTurno):
    def actualizar(self, turno, mensaje):
        print(f"[LOG] Turno #{turno.id} | {turno.estado} | {mensaje}")


# ══════════════════════════════════════════════════════════════
# STATE
# ══════════════════════════════════════════════════════════════

class EstadoTurno(ABC):
    @abstractmethod
    def confirmar(self, turno): pass
    @abstractmethod
    def atender(self, turno): pass
    @abstractmethod
    def completar(self, turno): pass
    @abstractmethod
    def cancelar(self, turno, motivo=""): pass
    @abstractmethod
    def reprogramar(self, turno, nueva_fecha, nueva_hora): pass
    @abstractmethod
    def nombre(self): pass


class EstadoPendiente(EstadoTurno):
    def confirmar(self, turno):
        turno.set_estado(EstadoConfirmado())
        turno.notificar("Tu turno fue CONFIRMADO")
    def atender(self, turno):
        raise ValueError("El turno debe confirmarse antes de atender.")
    def completar(self, turno):
        raise ValueError("El turno debe confirmarse antes de completar.")
    def cancelar(self, turno, motivo=""):
        turno.motivo_cancelacion = motivo
        turno.set_estado(EstadoCancelado())
        turno.notificar(f"Tu turno fue CANCELADO. Motivo: {motivo}")
    def reprogramar(self, turno, nueva_fecha, nueva_hora):
        turno.fecha = nueva_fecha
        turno.hora  = nueva_hora
        turno.notificar(f"Turno REPROGRAMADO al {nueva_fecha} a las {nueva_hora}")
    def nombre(self): return "PENDIENTE"


class EstadoConfirmado(EstadoTurno):
    def confirmar(self, turno):
        raise ValueError("El turno ya está confirmado.")
    def atender(self, turno):
        turno.set_estado(EstadoEnAtencion())
        turno.notificar("El paciente está siendo ATENDIDO")
    def completar(self, turno):
        raise ValueError("El turno debe pasar por atención primero.")
    def cancelar(self, turno, motivo=""):
        turno.motivo_cancelacion = motivo
        turno.set_estado(EstadoCancelado())
        turno.notificar(f"Tu turno fue CANCELADO. Motivo: {motivo}")
    def reprogramar(self, turno, nueva_fecha, nueva_hora):
        turno.fecha = nueva_fecha
        turno.hora  = nueva_hora
        turno.set_estado(EstadoPendiente())
        turno.notificar(f"Turno REPROGRAMADO al {nueva_fecha} a las {nueva_hora}")
    def nombre(self): return "CONFIRMADO"


class EstadoEnAtencion(EstadoTurno):
    def confirmar(self, turno): raise ValueError("El turno ya está en atención.")
    def atender(self, turno):   raise ValueError("El turno ya está en atención.")
    def completar(self, turno):
        turno.set_estado(EstadoCompletado())
        turno.notificar("Consulta COMPLETADA. Hasta pronto!")
    def cancelar(self, turno, motivo=""):
        raise ValueError("No se puede cancelar un turno en atención.")
    def reprogramar(self, turno, nf, nh):
        raise ValueError("No se puede reprogramar un turno en atención.")
    def nombre(self): return "EN ATENCION"


class EstadoCompletado(EstadoTurno):
    def confirmar(self, turno):            raise ValueError("Turno ya completado.")
    def atender(self, turno):              raise ValueError("Turno ya completado.")
    def completar(self, turno):            raise ValueError("Turno ya completado.")
    def cancelar(self, turno, motivo=""):  raise ValueError("No se puede cancelar un turno completado.")
    def reprogramar(self, turno, nf, nh):  raise ValueError("Turno ya completado.")
    def nombre(self): return "COMPLETADO"


class EstadoCancelado(EstadoTurno):
    def confirmar(self, turno):            raise ValueError("Turno cancelado.")
    def atender(self, turno):              raise ValueError("Turno cancelado.")
    def completar(self, turno):            raise ValueError("Turno cancelado.")
    def cancelar(self, turno, motivo=""):  raise ValueError("El turno ya está cancelado.")
    def reprogramar(self, turno, nf, nh):  raise ValueError("Turno cancelado.")
    def nombre(self): return "CANCELADO"


# ══════════════════════════════════════════════════════════════
# OBRAS SOCIALES — REPOSITORIO DINÁMICO
# ══════════════════════════════════════════════════════════════

class ObraSocialEntry:
    def __init__(self, nombre, cobertura, activa=True, motivo_baja=""):
        self.nombre       = nombre
        self.cobertura    = float(cobertura)
        self.activa       = activa
        self.motivo_baja  = motivo_baja
        self.creada_en    = datetime.now().strftime("%d/%m/%Y %H:%M")

    def to_dict(self):
        return {
            'nombre':      self.nombre,
            'cobertura':   self.cobertura,
            'activa':      self.activa,
            'motivo_baja': self.motivo_baja,
            'creada_en':   self.creada_en,
        }


class ObraSocialRepository:
    def __init__(self):
        self._obras = {}
        self._cargar_defaults()

    def _cargar_defaults(self):
        defaults = [
            ObraSocialEntry("IPS Misiones", 80.0),
            ObraSocialEntry("OSECAC",       75.0),
            ObraSocialEntry("OSDE",         90.0),
        ]
        for o in defaults:
            self._obras[o.nombre] = o

    def todas(self):
        return list(self._obras.values())

    def activas(self):
        return [o for o in self._obras.values() if o.activa]

    def buscar(self, nombre):
        return self._obras.get(nombre)

    def agregar(self, nombre, cobertura):
        if nombre in self._obras:
            raise ValueError(f"La obra social '{nombre}' ya existe.")
        if not (0 < float(cobertura) <= 100):
            raise ValueError("El porcentaje debe estar entre 1 y 100.")
        self._obras[nombre] = ObraSocialEntry(nombre, float(cobertura))

    def modificar_cobertura(self, nombre, nueva_cobertura):
        obra = self.buscar(nombre)
        if not obra:
            raise ValueError(f"Obra social '{nombre}' no encontrada.")
        if not (0 < float(nueva_cobertura) <= 100):
            raise ValueError("El porcentaje debe estar entre 1 y 100.")
        obra.cobertura = float(nueva_cobertura)

    def desactivar(self, nombre, motivo=""):
        obra = self.buscar(nombre)
        if not obra:
            raise ValueError(f"Obra social '{nombre}' no encontrada.")
        obra.activa      = False
        obra.motivo_baja = motivo

    def activar(self, nombre):
        obra = self.buscar(nombre)
        if not obra:
            raise ValueError(f"Obra social '{nombre}' no encontrada.")
        obra.activa      = True
        obra.motivo_baja = ""

    def eliminar(self, nombre):
        self._obras.pop(nombre, None)

    def existe(self, nombre):
        return nombre in self._obras


# ══════════════════════════════════════════════════════════════
# MODELOS
# ══════════════════════════════════════════════════════════════

class Especialidad(Enum):
    CLINICA_MEDICA = "Clinica Medica"
    PEDIATRIA      = "Pediatria"
    CARDIOLOGIA    = "Cardiologia"
    GINECOLOGIA    = "Ginecologia"
    TRAUMATOLOGIA  = "Traumatologia"
    DERMATOLOGIA   = "Dermatologia"


class ObraSocial:
    def __init__(self, nombre):
        obra = obra_social_repo.buscar(nombre)
        if not obra:
            raise ValueError(f"Obra social '{nombre}' no encontrada.")
        if not obra.activa:
            raise ValueError(f"La obra social '{nombre}' no está operativa actualmente. Motivo: {obra.motivo_baja}")
        self.nombre    = nombre
        self.cobertura = obra.cobertura

    def __str__(self):
        return f"{self.nombre} (cubre {self.cobertura}%)"


class Paciente:
    def __init__(self, nombre, dni, telefono="", email="", obra_social=None):
        self.nombre      = nombre
        self.dni         = dni
        self.telefono    = telefono
        self.email       = email
        self.obra_social = obra_social

    def __str__(self):
        os = str(self.obra_social) if self.obra_social else "Sin obra social"
        return f"{self.nombre} (DNI: {self.dni}) [{os}]"


class Medico:
    def __init__(self, nombre, especialidad, matricula,
                 hora_inicio="08:00", hora_fin="12:00", duracion_min=30):
        self.nombre       = nombre
        self.especialidad = especialidad
        self.matricula    = matricula
        self.hora_inicio  = hora_inicio
        self.hora_fin     = hora_fin
        self.duracion_min = duracion_min

    def generar_horarios(self):
        horarios = []
        inicio = datetime.strptime(self.hora_inicio, "%H:%M")
        fin    = datetime.strptime(self.hora_fin,    "%H:%M")
        while inicio < fin:
            horarios.append(inicio.strftime("%H:%M"))
            inicio += timedelta(minutes=self.duracion_min)
        return horarios

    def __str__(self):
        return f"Dr/a. {self.nombre} — {self.especialidad.value} (Mat: {self.matricula})"


class CalculoCosto:
    COSTO_CONSULTA = 10000.0

    @staticmethod
    def calcular(paciente):
        if paciente.obra_social is None:
            return {
                "costo_total":   CalculoCosto.COSTO_CONSULTA,
                "cubre_os":      0.0,
                "paga_paciente": CalculoCosto.COSTO_CONSULTA,
                "detalle":       "Sin obra social — paga consulta completa"
            }
        cob            = paciente.obra_social.cobertura
        monto_os       = round(CalculoCosto.COSTO_CONSULTA * cob / 100, 2)
        monto_paciente = round(CalculoCosto.COSTO_CONSULTA - monto_os, 2)
        return {
            "costo_total":   CalculoCosto.COSTO_CONSULTA,
            "cubre_os":      monto_os,
            "paga_paciente": monto_paciente,
            "detalle":       f"{paciente.obra_social.nombre} cubre {cob}%"
        }


class Turno:
    _contador = 0

    def __init__(self, paciente, medico, fecha, hora):
        Turno._contador       += 1
        self.id                = Turno._contador
        self.paciente          = paciente
        self.medico            = medico
        self.fecha             = fecha
        self.hora              = hora
        self._estado           = EstadoPendiente()
        self._observadores     = []
        self.costo             = CalculoCosto.calcular(paciente)
        self.motivo_cancelacion = ""

    @property
    def estado(self):
        return self._estado.nombre()

    def set_estado(self, nuevo_estado):
        self._estado = nuevo_estado

    def suscribir(self, obs):
        self._observadores.append(obs)

    def notificar(self, mensaje):
        for obs in self._observadores:
            obs.actualizar(self, mensaje)

    def confirmar(self):            self._estado.confirmar(self)
    def atender(self):              self._estado.atender(self)
    def completar(self):            self._estado.completar(self)
    def cancelar(self, motivo=""):  self._estado.cancelar(self, motivo)
    def reprogramar(self, nf, nh):  self._estado.reprogramar(self, nf, nh)

    def to_dict(self):
        return {
            'id':                self.id,
            'paciente':          self.paciente.nombre,
            'dni':               self.paciente.dni,
            'medico':            self.medico.nombre,
            'especialidad':      self.medico.especialidad.value,
            'fecha':             self.fecha,
            'hora':              self.hora,
            'estado':            self.estado,
            'costo':             self.costo,
            'motivo_cancelacion': self.motivo_cancelacion,
        }


# ══════════════════════════════════════════════════════════════
# SINGLETON — Validador de cobertura
# ══════════════════════════════════════════════════════════════

class ValidadorCobertura:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def validar(self, paciente):
        if paciente.obra_social is None:
            return True, "Sin obra social — pagará el 100% ($10.000)"
        obra = obra_social_repo.buscar(paciente.obra_social.nombre)
        if not obra:
            return False, f"Obra social no reconocida."
        if not obra.activa:
            return False, f"'{obra.nombre}' no está operativa. Motivo: {obra.motivo_baja}"
        return True, f"Cobertura válida: {paciente.obra_social}"


# ══════════════════════════════════════════════════════════════
# FACTORY METHOD
# ══════════════════════════════════════════════════════════════

class TurnoFactory:
    @staticmethod
    def crear(paciente, medico, fecha, hora):
        turno = Turno(paciente, medico, fecha, hora)
        if paciente.email:
            turno.suscribir(EmailObservador(paciente.email))
        if paciente.telefono:
            turno.suscribir(SMSObservador(paciente.telefono))
        turno.suscribir(ConsoleObservador())
        return turno


# ══════════════════════════════════════════════════════════════
# REPOSITORY — Turnos
# ══════════════════════════════════════════════════════════════

class TurnoRepository:
    def __init__(self):
        self._turnos = []

    def agregar(self, turno):
        self._turnos.append(turno)

    def todos(self):
        return list(self._turnos)

    def buscar_por_id(self, id):
        return next((t for t in self._turnos if t.id == id), None)

    def buscar_por_paciente(self, dni):
        return [t for t in self._turnos if t.paciente.dni == dni]

    def buscar_por_medico_y_fecha(self, medico_nombre, fecha):
        return [t for t in self._turnos
                if t.medico.nombre == medico_nombre and t.fecha == fecha]

    def horarios_ocupados(self, medico_nombre, fecha):
        return [
            t.hora for t in self._turnos
            if t.medico.nombre == medico_nombre
            and t.fecha == fecha
            and t.estado != 'CANCELADO'
        ]

    def horarios_disponibles(self, medico, fecha):
        todos    = medico.generar_horarios()
        ocupados = self.horarios_ocupados(medico.nombre, fecha)
        hoy      = date.today().strftime("%Y-%m-%d")
        ahora    = datetime.now().strftime("%H:%M")
        result   = []
        for h in todos:
            if h in ocupados:
                result.append({'hora': h, 'disponible': False})
            elif fecha == hoy and h <= ahora:
                result.append({'hora': h, 'disponible': False})
            else:
                result.append({'hora': h, 'disponible': True})
        return result


# ══════════════════════════════════════════════════════════════
# REPOSITORY — Médicos
# ══════════════════════════════════════════════════════════════

class MedicoRepository:
    ESPECIALIDADES_VALIDAS = [e.value for e in Especialidad]

    def __init__(self):
        self._medicos = {}

    def agregar(self, nombre, especialidad_str, matricula,
                hora_inicio="08:00", hora_fin="12:00", duracion_min=30):
        esp    = self._resolver_especialidad(especialidad_str)
        medico = Medico(nombre, esp, matricula, hora_inicio, hora_fin, duracion_min)
        self._medicos[matricula] = medico
        return medico

    def eliminar(self, matricula):
        self._medicos.pop(matricula, None)

    def todos(self):
        return list(self._medicos.values())

    def buscar_por_matricula(self, matricula):
        return self._medicos.get(matricula)

    def buscar_por_indice(self, idx):
        lista = self.todos()
        if 0 <= idx < len(lista):
            return lista[idx]
        return None

    def _resolver_especialidad(self, texto):
        for e in Especialidad:
            if e.value.lower() == texto.lower() or e.name.lower() == texto.lower():
                return e
        return Especialidad.CLINICA_MEDICA


# ══════════════════════════════════════════════════════════════
# AUDITORÍA
# ══════════════════════════════════════════════════════════════

class AuditoriaEntry:
    _contador = 0

    def __init__(self, usuario, rol, accion, detalle):
        AuditoriaEntry._contador += 1
        self.id        = AuditoriaEntry._contador
        self.usuario   = usuario
        self.rol       = rol
        self.accion    = accion
        self.detalle   = detalle
        self.timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    def to_dict(self):
        return {
            'id':        self.id,
            'usuario':   self.usuario,
            'rol':       self.rol,
            'accion':    self.accion,
            'detalle':   self.detalle,
            'timestamp': self.timestamp,
        }


class AuditoriaRepository:
    def __init__(self):
        self._logs = []

    def registrar(self, usuario, rol, accion, detalle=""):
        entry = AuditoriaEntry(usuario, rol, accion, detalle)
        self._logs.append(entry)
        return entry

    def todos(self):
        return list(reversed(self._logs))

    def filtrar_por_rol(self, rol):
        return [e for e in reversed(self._logs) if e.rol == rol]


# ══════════════════════════════════════════════════════════════
# INSTANCIAS GLOBALES
# ══════════════════════════════════════════════════════════════

obra_social_repo = ObraSocialRepository()   # debe ir antes que validador
repositorio      = TurnoRepository()
validador        = ValidadorCobertura()
medico_repo      = MedicoRepository()
auditoria        = AuditoriaRepository()

# Médicos iniciales
medico_repo.agregar("Ana Garcia",       "Clinica Medica",  "MP-1001")
medico_repo.agregar("Luis Martinez",    "Pediatria",       "MP-1002")
medico_repo.agregar("Maria Lopez",      "Cardiologia",     "MP-1003")
medico_repo.agregar("Carlos Rodriguez", "Ginecologia",     "MP-1004")
medico_repo.agregar("Juan Perez",       "Traumatologia",   "MP-1005")
medico_repo.agregar("Laura Sanchez",    "Dermatologia",    "MP-1006")
