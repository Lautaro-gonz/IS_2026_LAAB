import threading
from abc import ABC, abstractmethod
from enum import Enum


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
        turno.hora = nueva_hora
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
        turno.hora = nueva_hora
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
    def confirmar(self, turno):           raise ValueError("Turno ya completado.")
    def atender(self, turno):             raise ValueError("Turno ya completado.")
    def completar(self, turno):           raise ValueError("Turno ya completado.")
    def cancelar(self, turno, motivo=""): raise ValueError("No se puede cancelar un turno completado.")
    def reprogramar(self, turno, nf, nh): raise ValueError("Turno ya completado.")
    def nombre(self): return "COMPLETADO"


class EstadoCancelado(EstadoTurno):
    def confirmar(self, turno):           raise ValueError("Turno cancelado.")
    def atender(self, turno):             raise ValueError("Turno cancelado.")
    def completar(self, turno):           raise ValueError("Turno cancelado.")
    def cancelar(self, turno, motivo=""): raise ValueError("El turno ya está cancelado.")
    def reprogramar(self, turno, nf, nh): raise ValueError("Turno cancelado.")
    def nombre(self): return "CANCELADO"


# ══════════════════════════════════════════════════════════════
# MODELOS
# ══════════════════════════════════════════════════════════════

class Especialidad(Enum):
    CLINICA_MEDICA = "Clínica Médica"
    PEDIATRIA      = "Pediatría"
    CARDIOLOGIA    = "Cardiología"
    GINECOLOGIA    = "Ginecología"
    TRAUMATOLOGIA  = "Traumatología"
    DERMATOLOGIA   = "Dermatología"


class ObraSocial:
    COBERTURAS = {
        "IPS Misiones": 80.0,
        "OSECAC":       75.0,
        "OSDE":         90.0,
    }

    def __init__(self, nombre):
        if nombre not in self.COBERTURAS:
            raise ValueError(f"Obra social '{nombre}' no válida.")
        self.nombre    = nombre
        self.cobertura = self.COBERTURAS[nombre]

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
    def __init__(self, nombre, especialidad, matricula):
        self.nombre       = nombre
        self.especialidad = especialidad
        self.matricula    = matricula

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
        Turno._contador      += 1
        self.id               = Turno._contador
        self.paciente         = paciente
        self.medico           = medico
        self.fecha            = fecha
        self.hora             = hora
        self._estado          = EstadoPendiente()
        self._observadores    = []
        self.costo            = CalculoCosto.calcular(paciente)
        self.motivo_cancelacion = ""

    @property
    def estado(self):
        return self._estado.nombre()

    def set_estado(self, nuevo_estado):
        self._estado = nuevo_estado

    def suscribir(self, observador):
        self._observadores.append(observador)

    def notificar(self, mensaje):
        for obs in self._observadores:
            obs.actualizar(self, mensaje)

    def confirmar(self):   self._estado.confirmar(self)
    def atender(self):     self._estado.atender(self)
    def completar(self):   self._estado.completar(self)
    def cancelar(self, motivo=""):      self._estado.cancelar(self, motivo)
    def reprogramar(self, nf, nh):     self._estado.reprogramar(self, nf, nh)

    def to_dict(self):
        return {
            'id':       self.id,
            'paciente': self.paciente.nombre,
            'dni':      self.paciente.dni,
            'medico':   self.medico.nombre,
            'especialidad': self.medico.especialidad.value,
            'fecha':    self.fecha,
            'hora':     self.hora,
            'estado':   self.estado,
            'costo':    self.costo,
            'motivo_cancelacion': self.motivo_cancelacion,
        }


# ══════════════════════════════════════════════════════════════
# SINGLETON — Validador de cobertura
# ══════════════════════════════════════════════════════════════

class ValidadorCobertura:
    _instance = None
    _lock = threading.Lock()
    OBRAS_VALIDAS = set(ObraSocial.COBERTURAS.keys())

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def validar(self, paciente):
        if paciente.obra_social is None:
            return True, "Sin obra social — pagará el 100% ($10.000)"
        if paciente.obra_social.nombre not in self.OBRAS_VALIDAS:
            return False, f"'{paciente.obra_social.nombre}' no es válida."
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
# REPOSITORY
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


# ══════════════════════════════════════════════════════════════
# REGISTRO DINÁMICO DE MÉDICOS
# Se sincroniza con los usuarios de rol 'doctor'
# ══════════════════════════════════════════════════════════════

class MedicoRepository:
    """Mantiene la lista de médicos sincronizada con los usuarios."""

    ESPECIALIDADES_VALIDAS = [e.value for e in Especialidad]

    def __init__(self):
        self._medicos = {}

    def agregar(self, nombre, especialidad_str, matricula):
        """Agrega un médico. especialidad_str es el valor del Enum (ej: 'Pediatría')."""
        esp = self._resolver_especialidad(especialidad_str)
        medico = Medico(nombre, esp, matricula)
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
        return Especialidad.CLINICA_MEDICA  # fallback


OBRAS_SOCIALES = list(ObraSocial.COBERTURAS.keys())

# Instancias globales
repositorio      = TurnoRepository()
validador        = ValidadorCobertura()
medico_repo      = MedicoRepository()

# Médicos iniciales de ejemplo
medico_repo.agregar("Ana Garcia",       "Clinica Medica",  "MP-1001")
medico_repo.agregar("Luis Martinez",    "Pediatria",       "MP-1002")
medico_repo.agregar("Maria Lopez",      "Cardiologia",     "MP-1003")
medico_repo.agregar("Carlos Rodriguez", "Ginecologia",     "MP-1004")
medico_repo.agregar("Juan Perez",       "Traumatologia",   "MP-1005")
medico_repo.agregar("Laura Sanchez",    "Dermatologia",    "MP-1006")
