import threading
from datetime import datetime, date, timedelta
from django.db.utils import OperationalError, ProgrammingError
from turnos.models import ObraSocial as ObraSocialModel, Medico as MedicoModel, Paciente as PacienteModel, Turno as TurnoModel, AuditoriaLog

# ══════════════════════════════════════════════════════════════
# OBRAS SOCIALES — REPOSITORIO DINÁMICO
# ══════════════════════════════════════════════════════════════

class ObraSocialRepository:
    def __init__(self):
        self._cargar_defaults()

    def _cargar_defaults(self):
        try:
            if not ObraSocialModel.objects.exists():
                defaults = [
                    ("IPS Misiones", 80.0),
                    ("OSECAC",       75.0),
                    ("OSDE",         90.0),
                ]
                for o in defaults:
                    ObraSocialModel.objects.create(
                        nombre=o[0], cobertura=o[1], activa=True,
                        creada_en=datetime.now().strftime("%d/%m/%Y %H:%M")
                    )
        except (OperationalError, ProgrammingError):
            pass

    def todas(self):
        return list(ObraSocialModel.objects.all())

    def activas(self):
        return list(ObraSocialModel.objects.filter(activa=True))

    def buscar(self, nombre):
        return ObraSocialModel.objects.filter(nombre=nombre).first()

    def agregar(self, nombre, cobertura):
        if self.existe(nombre):
            raise ValueError(f"La obra social '{nombre}' ya existe.")
        if not (0 < float(cobertura) <= 100):
            raise ValueError("El porcentaje debe estar entre 1 y 100.")
        ObraSocialModel.objects.create(
            nombre=nombre, cobertura=float(cobertura), activa=True,
            creada_en=datetime.now().strftime("%d/%m/%Y %H:%M")
        )

    def modificar_cobertura(self, nombre, nueva_cobertura):
        obra = self.buscar(nombre)
        if not obra:
            raise ValueError(f"Obra social '{nombre}' no encontrada.")
        if not (0 < float(nueva_cobertura) <= 100):
            raise ValueError("El porcentaje debe estar entre 1 y 100.")
        obra.cobertura = float(nueva_cobertura)
        obra.save()

    def desactivar(self, nombre, motivo=""):
        obra = self.buscar(nombre)
        if not obra:
            raise ValueError(f"Obra social '{nombre}' no encontrada.")
        obra.activa = False
        obra.motivo_baja = motivo
        obra.save()

    def activar(self, nombre):
        obra = self.buscar(nombre)
        if not obra:
            raise ValueError(f"Obra social '{nombre}' no encontrada.")
        obra.activa = True
        obra.motivo_baja = ""
        obra.save()

    def eliminar(self, nombre):
        ObraSocialModel.objects.filter(nombre=nombre).delete()

    def existe(self, nombre):
        return ObraSocialModel.objects.filter(nombre=nombre).exists()


# ══════════════════════════════════════════════════════════════
# MODELOS WRAPPERS PARA MANTENER LA API
# ══════════════════════════════════════════════════════════════

from enum import Enum
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
        self.obra_model = obra # Guardar referencia al modelo

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
        costos = CalculoCosto.calcular(paciente)
        
        # Buscar o crear paciente en DB
        paciente_model, _ = PacienteModel.objects.get_or_create(
            dni=paciente.dni,
            defaults={
                'nombre': paciente.nombre,
                'telefono': paciente.telefono,
                'email': paciente.email,
                'obra_social': paciente.obra_social.obra_model if paciente.obra_social else None
            }
        )
        # Update paciente just in case
        paciente_model.nombre = paciente.nombre
        paciente_model.obra_social = paciente.obra_social.obra_model if paciente.obra_social else None
        paciente_model.save()
        
        turno = TurnoModel.objects.create(
            paciente=paciente_model,
            medico=medico,
            fecha=fecha,
            hora=hora,
            estado="PENDIENTE",
            costo_total=costos['costo_total'],
            cubre_os=costos['cubre_os'],
            paga_paciente=costos['paga_paciente'],
            detalle_costo=costos['detalle']
        )
        return turno


# ══════════════════════════════════════════════════════════════
# REPOSITORY — Turnos
# ══════════════════════════════════════════════════════════════

class TurnoRepository:
    def agregar(self, turno):
        # El Factory ya lo guarda en la DB
        pass

    def todos(self):
        return list(TurnoModel.objects.all())

    def buscar_por_id(self, id):
        return TurnoModel.objects.filter(id=id).first()

    def buscar_por_paciente(self, dni):
        return list(TurnoModel.objects.filter(paciente__dni=dni))

    def buscar_por_medico_y_fecha(self, medico_nombre, fecha):
        return list(TurnoModel.objects.filter(medico__nombre=medico_nombre, fecha=fecha))

    def horarios_ocupados(self, medico_nombre, fecha):
        turnos = TurnoModel.objects.filter(
            medico__nombre=medico_nombre, fecha=fecha
        ).exclude(estado='CANCELADO')
        return [t.hora for t in turnos]

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

    def _cargar_defaults(self):
        try:
            if not MedicoModel.objects.exists():
                self.agregar("Ana Garcia",       "Clinica Medica",  "MP-1001")
                self.agregar("Luis Martinez",    "Pediatria",       "MP-1002")
                self.agregar("Maria Lopez",      "Cardiologia",     "MP-1003")
                self.agregar("Carlos Rodriguez", "Ginecologia",     "MP-1004")
                self.agregar("Juan Perez",       "Traumatologia",   "MP-1005")
                self.agregar("Laura Sanchez",    "Dermatologia",    "MP-1006")
        except (OperationalError, ProgrammingError):
            pass

    def agregar(self, nombre, especialidad_str, matricula,
                hora_inicio="08:00", hora_fin="12:00", duracion_min=30):
        esp = self._resolver_especialidad(especialidad_str).value
        medico, created = MedicoModel.objects.get_or_create(
            matricula=matricula,
            defaults={
                'nombre': nombre,
                'especialidad': esp,
                'hora_inicio': hora_inicio,
                'hora_fin': hora_fin,
                'duracion_min': duracion_min
            }
        )
        return medico

    def eliminar(self, matricula):
        MedicoModel.objects.filter(matricula=matricula).delete()

    def todos(self):
        return list(MedicoModel.objects.all())

    def buscar_por_matricula(self, matricula):
        return MedicoModel.objects.filter(matricula=matricula).first()

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

class AuditoriaRepository:
    def registrar(self, usuario, rol, accion, detalle=""):
        return AuditoriaLog.objects.create(
            usuario=usuario,
            rol=rol,
            accion=accion,
            detalle=detalle,
            timestamp=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        )

    def todos(self):
        return list(AuditoriaLog.objects.all().order_by('-id'))

    def filtrar_por_rol(self, rol):
        return list(AuditoriaLog.objects.filter(rol=rol).order_by('-id'))


# ══════════════════════════════════════════════════════════════
# INSTANCIAS GLOBALES
# ══════════════════════════════════════════════════════════════

obra_social_repo = ObraSocialRepository()   # debe ir antes que validador
repositorio      = TurnoRepository()
validador        = ValidadorCobertura()
medico_repo      = MedicoRepository()
auditoria        = AuditoriaRepository()

# Cargar default medicos
medico_repo._cargar_defaults()

OBRAS_SOCIALES = []
try:
    OBRAS_SOCIALES = [o.nombre for o in obra_social_repo.activas()]
except (OperationalError, ProgrammingError):
    pass
