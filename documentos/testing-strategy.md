# 🧪 Testing Strategy — Sistema de Turnos Médicos

**Proyecto:** Sistema de Gestión de Turnos — Clínica Médica  
**Equipo:** LAAB  
**Última actualización:** TP2

---

## Índice

- [Herramientas de testing](#herramientas-de-testing)
- [Estrategia por nivel de prueba](#estrategia-por-nivel-de-prueba)
- [Plan de mocks y dobles de prueba](#plan-de-mocks-y-dobles-de-prueba)
- [Flujo E2E básico](#flujo-e2e-básico)
- [Estrategia de regresión](#estrategia-de-regresión)
- [Plan de estrés futuro](#plan-de-estrés-futuro)

---

## Herramientas de testing

| Herramienta | Tipo | Uso en el proyecto | Estado |
|---|---|---|---|
| `pytest` | Framework de pruebas unitarias | Correr los 20 casos de `test_logica.py` | ✅ Activo |
| `unittest` | Framework estándar Python | Alternativa compatible con pytest | ✅ Activo |
| `unittest.mock` | Dobles de prueba (mocks/stubs) | Mockear SQLite, autenticación y Observer | 📋 Diseñado |
| `pytest-django` | Plugin Django para pytest | Tests de vistas y autenticación | 📋 Próxima etapa |
| GitHub Actions | CI/CD | Pipeline automático en cada push/PR | ✅ Activo |
| Locust / k6 | Pruebas de estrés | Carga concurrente en endpoints críticos | 🔮 Futuro |

---

## Estrategia por nivel de prueba

### Nivel 1 — Pruebas unitarias ✅ (implementadas en TP2)

**Objetivo:** verificar que cada clase y método del dominio funciona de forma aislada, sin depender de la BD ni de otros módulos.

**Qué se prueba:** `TurnoFactory`, `ObraSocial`, `CalculoCosto`, `EstadoTurno` (y subclases), `ValidadorCobertura`.

**Técnicas aplicadas:** partición de equivalencia y análisis de valores límite.

**Cobertura actual:** 20 casos de prueba sobre 6 funciones/métodos distintos.

**Archivo:** `tests/unit/test_logica.py`

```
TurnoFactory.crear()     → 7 casos (fecha y horario: límites válidos e inválidos)
ObraSocial.__init__()    → 3 casos (obras válidas e inválidas)
CalculoCosto.calcular()  → 3 casos (sin OS, OSDE, OSECAC)
EstadoTurno.*            → 4 casos (transiciones válidas e inválidas)
ValidadorCobertura.*     → 3 casos (Singleton + validación de cobertura)
```

---

### Nivel 2 — Pruebas de integración 📋 (diseñadas, no implementadas)

**Objetivo:** verificar que los módulos del sistema funcionan correctamente cuando interactúan entre sí y con dependencias externas (SQLite, autenticación Django).

**Cuándo se implementan:** cuando el sistema migre de almacenamiento en memoria a Django ORM con SQLite persistente.

**Dependencias a mockear:**

| Dependencia | Mock utilizado | Qué simula |
|---|---|---|
| SQLite / Django ORM | `unittest.mock.patch` sobre `TurnoRepositorio` | Guardar y recuperar turnos sin query real |
| Autenticación Django | `Client.force_login()` + `MagicMock` | Usuario con rol específico sin login real |

**Escenario principal diseñado:**

```
Recepcionista autenticada → POST formulario → ValidadorCobertura valida
→ TurnoFactory crea turno → repositorio.agregar() → Observer notifica
→ redirect con mensaje de éxito
```

**Archivo futuro:** `tests/integration/test_flujo_turno.py`

---

### Nivel 3 — Pruebas de sistema 🔮 (futuro — trabajo integrador)

**Objetivo:** verificar el sistema completo end-to-end desde la interfaz web hasta la base de datos, simulando el comportamiento real de un usuario.

**Herramienta candidata:** Selenium o Playwright para automatizar el navegador.

**Escenarios prioritarios:**
- Recepcionista crea turno completo desde el formulario web
- Médico ve su agenda del día con los turnos asignados
- Paciente consulta su turno ingresando su DNI
- Administrador crea un nuevo usuario médico

---

## Plan de mocks y dobles de prueba

### ¿Qué mockear y por qué?

| Componente | Tipo de doble | Justificación |
|---|---|---|
| `TurnoRepositorio.agregar()` | Mock con `patch` | Evita escribir en SQLite durante los tests |
| `TurnoRepositorio.buscar()` | Stub con `return_value` | Devuelve turno controlado sin query |
| `ValidadorCobertura.validar()` | Stub con `return_value` | Controla el resultado sin lógica real |
| `EmailObservador.actualizar()` | Mock con `assert_called` | Verifica que la notificación se disparó |
| Usuario autenticado | `MagicMock` + `force_login` | Simula rol sin crear registro en BD |

### Herramienta elegida: `unittest.mock`

Incluida en Python estándar desde 3.3. No requiere instalación. Compatible con pytest y Django. Provee `MagicMock`, `patch` y verificaciones de llamadas. Ver justificación completa en `docs/tp2-pruebas-unitarias.md`.

---

## Flujo E2E básico

El flujo end-to-end principal del sistema es la creación de un turno. Este es el camino crítico que debe mantenerse funcional en todo momento:

```
[1] Recepcionista accede al formulario de nuevo turno
        ↓
[2] Sistema muestra médicos disponibles por especialidad
        ↓
[3] Recepcionista completa: paciente, médico, fecha, hora, obra social
        ↓
[4] Sistema llama a ValidadorCobertura.validar(paciente)
    ├── [NO VÁLIDA] → muestra error en formulario, no crea turno
    └── [VÁLIDA] → continúa al paso 5
        ↓
[5] TurnoFactory.crear(paciente, medico, fecha, hora)
    ├── valida que fecha >= hoy
    ├── valida que hora esté entre 08:00 y 20:00
    ├── crea Turno con estado PENDIENTE  (State)
    └── suscribe observers según datos del paciente  (Observer)
        ↓
[6] repositorio.agregar(turno)  → persiste en SQLite
        ↓
[7] Observer notifica al paciente
    ├── EmailObservador → [EMAIL] Turno creado
    ├── SMSObservador   → [SMS] Turno creado
    └── ConsoleObservador → [LOG] evento registrado
        ↓
[8] Sistema redirige al panel con mensaje de confirmación
    "Turno #N creado para [nombre paciente]"
```

**Caminos alternativos críticos:**

```
Fecha pasada         → ValueError en TurnoFactory → error visible en formulario
Hora fuera de rango  → ValueError en TurnoFactory → error visible en formulario
Obra social inválida → (False, msg) en ValidadorCobertura → error en formulario
Turno ya cancelado   → ValueError en State al intentar acción → error controlado
```

---

## Estrategia de regresión

**Objetivo:** garantizar que las correcciones o nuevas funcionalidades no rompan lo que ya funciona.

### Qué se ejecuta automáticamente en cada push

El pipeline de GitHub Actions (`.github/workflows/test.yml`) corre automáticamente los 20 casos de prueba unitaria en cada `push` y `pull request`. Si algún test falla, el push queda marcado en rojo y el equipo recibe la notificación antes de hacer merge.

```yaml
# .github/workflows/test.yml
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with: { python-version: '3.11' }
      - run: pip install pytest
      - run: pytest tests/unit/ -v
```

### Reglas del equipo para evitar regresiones

- **Nunca hacer merge a `main` con tests en rojo.** El pipeline es la puerta de entrada.
- **Ante cualquier cambio en `logica.py`**, correr los tests localmente antes de hacer push.
- **Ante cualquier nuevo método o clase**, agregar al menos un caso de prueba antes de considerar la tarea terminada.
- **Ante un bug encontrado en producción**, escribir primero el test que lo reproduce y luego corregirlo (TDD).

### Prioridad de cobertura futura

Cuando se agreguen nuevas funcionalidades, los tests de regresión deben cubrir en este orden:

```
1. TurnoFactory (punto de entrada — mayor impacto si falla)
2. Estado del turno (ciclo de vida — reglas de negocio críticas)
3. ValidadorCobertura (afecta directamente al paciente)
4. CalculoCosto (impacto económico directo)
5. Vistas Django (integración — segunda etapa)
```

---

## Plan de estrés futuro

> 🔮 Esta sección se ejecutará en el trabajo integrador final, cuando el sistema tenga persistencia real en SQLite y esté desplegado en un servidor.

**Objetivo:** verificar que el sistema mantiene tiempos de respuesta aceptables bajo carga concurrente, especialmente en los endpoints más usados por la recepcionista.

### Herramienta candidata: Locust

```bash
pip install locust
```

Locust permite simular múltiples usuarios concurrentes haciendo requests HTTP al sistema, con métricas de tiempo de respuesta, tasa de errores y throughput en una interfaz web en tiempo real.

### Escenarios de estrés planificados

| Escenario | Usuarios simulados | Endpoint crítico | Métrica objetivo |
|---|---|---|---|
| Carga normal | 10 usuarios | `POST /turnos/crear/` | < 500ms respuesta |
| Carga media | 50 usuarios | `GET /turnos/agenda/` | < 1s respuesta |
| Pico de demanda | 100 usuarios | `POST /turnos/crear/` | Sin errores 500 |
| Concurrencia en Singleton | 50 threads | `ValidadorCobertura` | Sin condición de carrera |

### Criterios de aceptación

- El sistema no debe devolver errores `500` bajo ninguno de los escenarios de carga definidos.
- El tiempo de respuesta del formulario de creación de turno no debe superar **1 segundo** con 50 usuarios concurrentes.
- El `ValidadorCobertura` (Singleton con `threading.Lock()`) no debe presentar condiciones de carrera bajo 50 threads simultáneos — ya está implementado con doble verificación para este escenario.
- La BD SQLite debe manejar escrituras concurrentes sin bloqueos permanentes (considerar migración a PostgreSQL si se detectan problemas).
