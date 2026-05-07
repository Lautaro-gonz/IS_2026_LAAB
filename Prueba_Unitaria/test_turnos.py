# ══════════════════════════════════════════════
# PRUEBAS UNITARIAS — Sistema de Turnos
# Dev Lead: Angelina Alonso + Guty
# ══════════════════════════════════════════════
import pytest
import sys
import os
from datetime import date, timedelta

# Apuntamos al logica.py actual
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from turnos.logica import (
    Paciente, CalculoCosto, TurnoFactory,
    EstadoPendiente, EstadoConfirmado, EstadoCancelado,
    Especialidad, Turno
)


# ══════════════════════════════════════════════
# FUNCIÓN 1: CalculoCosto.calcular()
# Verifica que el cálculo de costos sea correcto
# según la obra social del paciente
# ══════════════════════════════════════════════

def test_costo_sin_obra_social():
    """Sin obra social el paciente paga $10.000 completos"""
    paciente = Paciente("Ana Lopez", "12345678")
    resultado = CalculoCosto.calcular(paciente)
    assert resultado["paga_paciente"] == 10000.0
    assert resultado["cubre_os"] == 0.0

def test_costo_con_cobertura_90():
    """Con 90% de cobertura el paciente paga $1.000"""
    class ObraSocialMock:
        nombre = "OSDE"
        cobertura = 90
    paciente = Paciente("Juan Perez", "87654321", obra_social=ObraSocialMock())
    resultado = CalculoCosto.calcular(paciente)
    assert resultado["paga_paciente"] == 1000.0
    assert resultado["cubre_os"] == 9000.0

def test_costo_con_cobertura_80():
    """Con 80% de cobertura el paciente paga $2.000"""
    class ObraSocialMock:
        nombre = "IPS Misiones"
        cobertura = 80
    paciente = Paciente("Maria Garcia", "11223344", obra_social=ObraSocialMock())
    resultado = CalculoCosto.calcular(paciente)
    assert resultado["paga_paciente"] == 2000.0
    assert resultado["cubre_os"] == 8000.0


# ══════════════════════════════════════════════
# FUNCIÓN 2: TurnoFactory.crear()
# Verifica validaciones de fecha y hora
# ══════════════════════════════════════════════

class MedicoMock:
    """Médico de prueba sin necesidad de base de datos"""
    nombre_completo = "Dr. Garcia"
    especialidad = Especialidad.CARDIOLOGIA
    matricula = "MP-1001"


def test_turno_fecha_pasada_lanza_error():
    """No se puede crear un turno con fecha anterior a hoy"""
    paciente = Paciente("Ana Lopez", "12345678")
    medico = MedicoMock()
    fecha_pasada = (date.today() - timedelta(days=1)).isoformat()
    with pytest.raises(ValueError, match="fecha pasada"):
        TurnoFactory.crear(paciente, medico, fecha_pasada, "10:00")

def test_turno_hora_fuera_de_rango_lanza_error():
    """No se puede crear un turno fuera del horario 08:00-20:00"""
    paciente = Paciente("Ana Lopez", "12345678")
    medico = MedicoMock()
    fecha_futura = (date.today() + timedelta(days=5)).isoformat()
    with pytest.raises(ValueError, match="no es valido"):
        TurnoFactory.crear(paciente, medico, fecha_futura, "07:00")

def test_turno_valido_se_crea_correctamente():
    """Un turno con fecha futura y hora válida se crea en estado PENDIENTE"""
    paciente = Paciente("Ana Lopez", "12345678")
    medico = MedicoMock()
    fecha_futura = (date.today() + timedelta(days=5)).isoformat()
    turno = TurnoFactory.crear(paciente, medico, fecha_futura, "10:00")
    assert turno is not None
    assert turno.estado == "PENDIENTE"
    assert turno.paciente.dni == "12345678"
