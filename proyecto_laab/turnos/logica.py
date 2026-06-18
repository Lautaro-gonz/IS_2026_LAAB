import threading
from abc import ABC, abstractmethod
from enum import Enum
from datetime import date, time, datetime, timedelta


# ══════════════════════════════════════════════════════════════
# DURACIONES POR ESPECIALIDAD (minutos)
# MEJORA 4: cada especialidad tiene su duración real
# ══════════════════════════════════════════════════════════════

DURACIONES = {
    "Clínica Médica":  20,
    "Pediatría":       20,
    "Cardiología":     30,
    "Ginecología":     30,
    "Traumatología":   40,
    "Dermatología":    20,
}


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


def _validar_anticipacion_cancelacion(turno):
    """
    MEJORA 3: Verifica que falten mas de 24hs para cancelar.
    Se usa en EstadoPendiente y EstadoConfirmado.
    """
    fecha_hora_turno = datetime.fromisoformat(f"{turno.fecha} {turno.hora}")
    if datetime.now() + timedelta(hours=24) > fecha_hora_turno:
        raise ValueError(
            "No se puede cancelar con menos de 24 horas de anticipacion. "
            f"El turno es el {turno.fecha} a las {turno.hora}."
        )


class EstadoPendiente(EstadoTurno):
    def confirmar(self, turno):
        turno.set_estado(EstadoConfirmado())
        turno.notificar("Tu turno fue CONFIRMADO")

    def atender(self, turno):
        raise ValueError("El turno debe confirmarse antes de atender.")

    def completar(self, turno):
        raise ValueError("El turno debe confirmarse antes de completar.")

    def cancelar(self, turno, motivo=""):
        # MEJORA 3: validar anticipacion
        _validar_anticipacion_cancelacion(turno)
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
        raise ValueError("El turno ya esta confirmado.")

    def atender(self, turno):
        turno.set_estado(EstadoEnAtencion())
        turno.notificar("El paciente esta siendo ATENDIDO")

    def completar(self, turno):
        raise ValueError("El turno debe pasar por atencion primero.")

    def cancelar(self, turno, motivo=""):
        # MEJORA 3: validar anticipacion
        _validar_anticipacion_cancelacion(turno)
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
    def confirmar(self, turno): raise ValueError("El turno ya esta en atencion.")
    def atender(self, turno):   raise ValueError("El turno ya esta en atencion.")
    def completar(self, turno):
        turno.set_estado(EstadoCompletado())
        turno.notificar("Consulta COMPLETADA. Hasta pronto!")
    def cancelar(self, turno, motivo=""):
        raise ValueError("No se puede cancelar un turno en atencion.")
    def reprogramar(self, turno, nf, nh):
        raise ValueError("No se puede reprogramar un turno en atencion.")
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
    def cancelar(self, turno, motivo=""):  raise ValueError("El turno ya esta cancelado.")
    def reprogramar(self, turno, nf, nh):  raise ValueError("Turno cancelado.")
    def nombre(self): return "CANCELADO"


# ══════════════════════════════════════════════════════════════
# MODELOS DEL DOMINIO
# ══════════════════════════════════════════════════════════════

class Especialidad(Enum):
    CLINICA_MEDICA = "Clínica Médica"
    PEDIATRIA      = "Pediatría"
    CARDIOLOGIA    = "Cardiología"
    GINECOLOGIA    = "Ginecología"
    TRAUMATOLOGIA  = "Traumatología"
    DERMATOLOGIA   = "Dermatología"





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
        Turno._contador        += 1
        self.id                 = Turno._contador
        self.paciente           = paciente
        self.medico             = medico
        self.fecha              = fecha
        self.hora               = hora
        self._estado            = EstadoPendiente()
        self._observadores      = []
        self.costo              = CalculoCosto.calcular(paciente)
        self.motivo_cancelacion = ""
        # MEJORA 4: duracion segun especialidad del medico
        esp = getattr(medico, 'especialidad', '')
        if hasattr(esp, 'value'):
            esp = esp.value
        self.duracion           = DURACIONES.get(esp, 20)

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

    def confirmar(self):              self._estado.confirmar(self)
    def atender(self):                self._estado.atender(self)
    def completar(self):              self._estado.completar(self)
    def cancelar(self, motivo=""):    self._estado.cancelar(self, motivo)
    def reprogramar(self, nf, nh):    self._estado.reprogramar(self, nf, nh)

    def to_dict(self):
        return {
            'id':                   self.id,
            'paciente':             self.paciente.nombre,
            'dni':                  self.paciente.dni,
            'medico':               getattr(self.medico, 'nombre_completo', getattr(self.medico, 'nombre', '')),
            'especialidad':         getattr(self.medico, 'especialidad', ''),
            'fecha':                self.fecha,
            'hora':                 self.hora,
            'estado':               self.estado,
            'costo':                self.costo,
            'duracion':             self.duracion,
            'motivo_cancelacion':   self.motivo_cancelacion,
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
            return True, "Sin obra social — pagara el 100% ($10.000)"
        # Si tiene obra social (instancia de ObraSocialDB), asumimos que es válida
        return True, f"Cobertura valida: {paciente.obra_social}"


# ══════════════════════════════════════════════════════════════
# FACTORY METHOD
# MEJORA 1: valida fecha no pasada
# MEJORA 2: valida horario entre 08:00 y 20:00
# ══════════════════════════════════════════════════════════════

class TurnoFactory:
    HORA_INICIO = time(8, 0)   # 08:00
    HORA_FIN    = time(20, 0)  # 20:00
    MAX_TURNOS_POR_DIA = 20

    @staticmethod
    def crear(paciente, medico, fecha, hora):
        # MEJORA 1: Validar que la fecha no sea pasada
        fecha_turno = date.fromisoformat(fecha)
        if fecha_turno < date.today():
            raise ValueError(
                f"No se puede crear un turno en una fecha pasada ({fecha})."
            )

        # MEJORA 2: Validar que el horario sea entre 08:00 y 20:00
        hora_turno = time.fromisoformat(hora)
        if not (TurnoFactory.HORA_INICIO <= hora_turno <= TurnoFactory.HORA_FIN):
            raise ValueError(
                f"El horario {hora} no es valido. "
                f"Los turnos son entre 08:00 y 20:00."
            )

        turno = Turno(paciente, medico, fecha, hora)
        if paciente.email:
            turno.suscribir(EmailObservador(paciente.email))
        if paciente.telefono:
            turno.suscribir(SMSObservador(paciente.telefono))
        turno.suscribir(ConsoleObservador())
        return turno





# Horarios de atención por matrícula: dias (0=Lun … 6=Dom), inicio y fin
HORARIOS = {
    "MP-1001": {"dias": [0,1,2,3,4], "inicio": "08:00", "fin": "14:00"},
    "MP-1002": {"dias": [0,1,2,3,4], "inicio": "10:00", "fin": "18:00"},
    "MP-1003": {"dias": [1,3,5],     "inicio": "09:00", "fin": "15:00"},
    "MP-1004": {"dias": [0,2,4],     "inicio": "14:00", "fin": "20:00"},
    "MP-1005": {"dias": [0,1,2,3,4], "inicio": "08:00", "fin": "16:00"},
    "MP-1006": {"dias": [1,2,3,4,5], "inicio": "09:00", "fin": "17:00"},
}



# Instancias globales
validador   = ValidadorCobertura()
