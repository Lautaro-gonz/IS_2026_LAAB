# 🧪 Pruebas Unitarias — TP2

<div align="center">

**Proyecto:** Sistema de Gestión de Turnos — Clínica Médica  
**Módulo testeado:** `ValidadorCobertura.validar()`  
**Técnicas aplicadas:** Clases de Equivalencia · Valores Límite  
**Framework:** `pytest`

</div>

---

## 📌 ¿Por qué este módulo?

`ValidadorCobertura.validar()` es el **punto de entrada crítico** antes de crear cualquier turno en el sistema. Si el validador falla, el turno no se crea. Fue elegido porque:

- Tiene **parámetros de entrada claros** (paciente con o sin obra social)
- Devuelve resultados **binarios y verificables** (`True/False` + mensaje)
- Tiene **costo calculable** según la cobertura, ideal para valores límite
- Es el componente que **más impacto tiene** si falla silenciosamente

---

## 🗂️ Clases de Equivalencia

Las clases se definieron sobre el atributo `obra_social` del paciente:

| ID | Clase | Descripción | ¿Válida? |
|:---:|---|---|:---:|
| CE1 | Obra social reconocida | IPS Misiones, OSECAC u OSDE | ✅ |
| CE2 | Sin obra social | `obra_social = None` | ✅ |
| CE3 | Obra social no reconocida | Nombre fuera del conjunto válido | ❌ |
| CE4 | Obra social vacía | `obra_social = ""` | ❌ |
| CE5 | Paciente nulo | `paciente = None` | ❌ |

---

## 📏 Valores Límite

El costo base de la consulta es **$10.000**. El sistema descuenta según la cobertura registrada:

| Obra Social | Cobertura | Costo al Paciente | Posición |
|---|:---:|:---:|---|
| OSDE | 90% | **$1.000** | 🔽 Mínimo posible |
| IPS Misiones | 80% | $2.000 | Cobertura alta |
| OSECAC | 75% | $2.500 | Cobertura media-alta |
| Sin obra social | 0% | **$10.000** | 🔼 Máximo posible |
| Obra inválida | — | **Rechazado** | 🚫 Frontera del sistema |

---

## ✅ Casos de Prueba

### Caso 1 — Cobertura válida con costo mínimo

> **Técnica:** CE1 (clase válida) + Valor límite inferior

| Campo | Detalle |
|---|---|
| **Entrada** | Paciente con obra social `OSDE` (90% de cobertura) |
| **Acción** | `validador.validar(paciente)` |
| **Resultado esperado** | `puede = True` · `costo = $1.000` · mensaje confirma cobertura |
| **Qué verifica** | Que la cobertura más alta calcule el costo mínimo correctamente |

```python
def test_osde_costo_minimo(validador, paciente_con_osde):
    puede, mensaje = validador.validar(paciente_con_osde)

    assert puede == True
    assert "OSDE" in mensaje
    assert paciente_con_osde.costo_consulta() == 1000
```

---

### Caso 2 — Sin obra social, costo máximo

> **Técnica:** CE2 (clase válida especial) + Valor límite superior

| Campo | Detalle |
|---|---|
| **Entrada** | Paciente con `obra_social = None` |
| **Acción** | `validador.validar(paciente)` |
| **Resultado esperado** | `puede = True` · `costo = $10.000` · mensaje indica pago completo |
| **Qué verifica** | Que un paciente sin cobertura sea aceptado y pague el precio base completo |

```python
def test_sin_obra_social_paga_completo(validador, paciente_sin_obra_social):
    puede, mensaje = validador.validar(paciente_sin_obra_social)

    assert puede == True
    assert "$10.000" in mensaje
    assert paciente_sin_obra_social.costo_consulta() == 10000
```

---

### Caso 3 — Obra social en la frontera del rechazo

> **Técnica:** CE3 (clase inválida) + Frontera del conjunto válido

| Campo | Detalle |
|---|---|
| **Entrada** | Paciente con `obra_social = "Swiss Medical"` (no registrada) |
| **Acción** | `validador.validar(paciente)` |
| **Resultado esperado** | `puede = False` · mensaje indica que la obra social no es válida |
| **Qué verifica** | Que cualquier obra social fuera del conjunto sea rechazada sin lanzar excepción |

```python
def test_obra_social_no_reconocida_es_rechazada(validador, paciente_obra_invalida):
    puede, mensaje = validador.validar(paciente_obra_invalida)

    assert puede == False
    assert "Swiss Medical" in mensaje
    assert "no es válida" in mensaje
```

---

## 🛠️ Estructura de fixtures

Los tres casos comparten fixtures reutilizables definidas una sola vez:

```python
# tests/conftest.py

import pytest
from turnos.logica import ValidadorCobertura, ObraSocial, Paciente

@pytest.fixture
def validador():
    return ValidadorCobertura()

@pytest.fixture
def paciente_con_osde():
    p = Paciente("María", "López", "30111222")
    p.obra_social = ObraSocial("OSDE")
    return p

@pytest.fixture
def paciente_sin_obra_social():
    return Paciente("Carlos", "Díaz", "25999888")   # obra_social = None por defecto

@pytest.fixture
def paciente_obra_invalida():
    p = Paciente("Juan", "Pérez", "12345678")
    p.obra_social = ObraSocial("Swiss Medical")
    return p
```

---

## ⚙️ Framework elegido: `pytest`

### ¿Por qué pytest y no unittest?

| Criterio | `unittest` | `pytest` ✅ |
|---|---|---|
| Sintaxis | Requiere heredar clases y métodos especiales | Funciones simples con `assert` |
| Compatibilidad Django | Manual | Nativa con `pytest-django` |
| Fixtures | Básicas con `setUp/tearDown` | Modulares, reutilizables y con scope |
| Salida al fallar | Poco descriptiva | Muestra valor obtenido vs esperado |
| Plugins disponibles | Pocos | Ecosistema amplio (`coverage`, `mock`, etc.) |
| Curva de aprendizaje | Media | Baja |

### Justificación

La pila tecnológica del proyecto es **Python + Django**. `pytest` es la elección natural porque:

- El plugin **`pytest-django`** integra la configuración del proyecto automáticamente sin configuración extra
- La sintaxis de **`assert` puro** hace los tests más legibles y fáciles de escribir
- Las **fixtures con `@pytest.fixture`** permiten reutilizar pacientes y validadores de prueba en todos los casos sin repetir código
- La **salida al fallar** muestra exactamente qué valor se obtuvo versus qué se esperaba, acortando el tiempo de debugging
- Es **gratuito, open source** y mantenido activamente por la comunidad Python

### Cómo ejecutar los tests

```bash
# Instalar pytest y el plugin de Django
pip install pytest pytest-django

# Ejecutar todos los tests
pytest

# Ejecutar con detalle
pytest -v

# Ver cobertura de código
pytest --cov=turnos
```

---

<div align="center">

*Pruebas diseñadas con técnicas de caja negra: Clases de Equivalencia y Valores Límite*  
*Ningún test requiere conocer la implementación interna del validador*

</div>
