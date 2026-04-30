# ══════════════════════════════════════════════
# PRUEBAS UNITARIAS — Sistema de Turnos
# Dev Lead: Angelina Alonso
# ══════════════════════════════════════════════

import pytest
import sys
import os

# Le decimos a Python dónde está el código del sistema
sys.path.insert(0, os.path.join(
    os.path.dirname(__file__), '..',
    'turnos_v2 (6)', 'turnos_v2'
))

# Importamos las clases que vamos a probar
from turnos.logica import (
    Paciente, Medico, ObraSocial, CalculoCosto,
    TurnoFactory, TurnoRepository, Especialidad
)

# ══════════════════════════════════════════════
# FUNCIÓN 1: CalculoCosto.calcular()
# Verifica que el cálculo de costos sea correcto
# según la obra social del paciente
# ══════════════════════════════════════════════

def test_costo_sin_obra_social():
    # Sin obra social el paciente paga $10.000 completos
    paciente = Paciente("Ana Lopez", "12345678")
    resultado = CalculoCosto.calcular(paciente)
    assert resultado["paga_paciente"] == 10000.0

def test_costo_con_osde():
    # Con OSDE (90%) el paciente paga $1.000
    os_obj = ObraSocial("OSDE")
    paciente = Paciente("Juan Perez", "87654321", obra_social=os_obj)
    resultado = CalculoCosto.calcular(paciente)
    assert resultado["paga_paciente"] == 1000.0
    assert resultado["cubre_os"] == 9000.0

def test_costo_con_ips_misiones():
    # Con IPS Misiones (80%) el paciente paga $2.000
    os_obj = ObraSocial("IPS Misiones")
    paciente = Paciente("Maria Garcia", "11223344", obra_social=os_obj)
    resultado = CalculoCosto.calcular(paciente)
    assert resultado["paga_paciente"] == 2000.0
    assert resultado["cubre_os"] == 8000.0

# ══════════════════════════════════════════════
# FUNCIÓN 2: TurnoRepository
# Verifica que los turnos se guarden
# y busquen correctamente
# ══════════════════════════════════════════════

def test_agregar_y_buscar_turno():
    # Un turno guardado se puede encontrar por su ID
    repo = TurnoRepository()
    paciente = Paciente("Ana Lopez", "12345678")
    medico = Medico("Garcia", Especialidad.CARDIOLOGIA, "MP-1001")
    turno = TurnoFactory.crear(paciente, medico, "2026-05-10", "09:00")
    repo.agregar(turno)
    resultado = repo.buscar_por_id(turno.id)
    assert resultado is not None
    assert resultado.paciente.dni == "12345678"

def test_buscar_turno_inexistente():
    # Buscar un ID que no existe devuelve None sin romperse
    repo = TurnoRepository()
    resultado = repo.buscar_por_id(9999)
    assert resultado is None

def test_buscar_turnos_por_paciente():
    # Se encuentran todos los turnos de un paciente por DNI
    repo = TurnoRepository()
    paciente = Paciente("Ana Lopez", "12345678")
    medico = Medico("Garcia", Especialidad.CARDIOLOGIA, "MP-1001")
    turno1 = TurnoFactory.crear(paciente, medico, "2026-05-10", "09:00")
    turno2 = TurnoFactory.crear(paciente, medico, "2026-05-11", "10:00")
    repo.agregar(turno1)
    repo.agregar(turno2)
    resultados = repo.buscar_por_paciente("12345678")
    assert len(resultados) == 2
