import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'turnos_v2 (6)', 'turnos_v2'))

from turnos.logica import (
    Paciente, Medico, ObraSocial, CalculoCosto,
    TurnoFactory, TurnoRepository, Especialidad
)

# PRUEBA 1 — Sin obra social paga $10.000
def test_costo_sin_obra_social():
    paciente = Paciente("Ana Lopez", "12345678")
    resultado = CalculoCosto.calcular(paciente)
    assert resultado["paga_paciente"] == 10000.0

# PRUEBA 2 — Con OSDE paga $1.000
def test_costo_con_osde():
    os = ObraSocial("OSDE")
    paciente = Paciente("Juan Perez", "87654321", obra_social=os)
    resultado = CalculoCosto.calcular(paciente)
    assert resultado["paga_paciente"] == 1000.0
    assert resultado["cubre_os"] == 9000.0

# PRUEBA 3 — Con IPS Misiones paga $2.000
def test_costo_con_ips_misiones():
    os = ObraSocial("IPS Misiones")
    paciente = Paciente("Maria Garcia", "11223344", obra_social=os)
    resultado = CalculoCosto.calcular(paciente)
    assert resultado["paga_paciente"] == 2000.0
    assert resultado["cubre_os"] == 8000.0

# PRUEBA 4 — Agregar y buscar turno por ID
def test_agregar_y_buscar_turno():
    repo = TurnoRepository()
    paciente = Paciente("Ana Lopez", "12345678")
    medico = Medico("Garcia", Especialidad.CARDIOLOGIA, "MP-1001")
    turno = TurnoFactory.crear(paciente, medico, "2026-05-10", "09:00")
    repo.agregar(turno)
    resultado = repo.buscar_por_id(turno.id)
    assert resultado is not None
    assert resultado.paciente.dni == "12345678"

# PRUEBA 5 — Buscar turno que no existe devuelve None
def test_buscar_turno_inexistente():
    repo = TurnoRepository()
    resultado = repo.buscar_por_id(9999)
    assert resultado is None

# PRUEBA 6 — Buscar todos los turnos de un paciente por DNI
def test_buscar_turnos_por_paciente():
    repo = TurnoRepository()
    paciente = Paciente("Ana Lopez", "12345678")
    medico = Medico("Garcia", Especialidad.CARDIOLOGIA, "MP-1001")
    turno1 = TurnoFactory.crear(paciente, medico, "2026-05-10", "09:00")
    turno2 = TurnoFactory.crear(paciente, medico, "2026-05-11", "10:00")
    repo.agregar(turno1)
    repo.agregar(turno2)
    resultados = repo.buscar_por_paciente("12345678")
    assert len(resultados) == 2
