# TP2 — Pruebas Unitarias
## Sistema de Turnos Médicos — Clínica LAAB

---

## B0. Investigación Previa

### ¿Qué es una clase de equivalencia?

Una **clase de equivalencia** es una técnica de diseño de casos de prueba que consiste en dividir el dominio de entrada de una función en grupos (clases) donde todos los valores del grupo se comportan de la misma manera. El principio es que si un valor de la clase produce un resultado correcto, todos los demás valores de esa clase también lo harán. Si un valor produce un error, todos los demás también lo producirán.

Esto permite reducir la cantidad de casos de prueba necesarios sin perder cobertura, ya que en lugar de probar todos los valores posibles, se elige uno representativo de cada clase.

Se dividen en:
- **Clases válidas**: valores que el sistema debe aceptar y procesar correctamente.
- **Clases inválidas**: valores que el sistema debe rechazar con un error.

**Cómo se aplica:**
1. Se identifica la función o método a probar.
2. Se analizan las condiciones de entrada.
3. Se agrupan los valores en clases válidas e inválidas.
4. Se elige un valor representativo de cada clase.
5. Se escribe un caso de prueba por cada clase.

---

### ¿Qué es un valor límite?

El **análisis de valores límite** es una técnica complementaria a la partición de equivalencia. Se basa en la observación de que los defectos de software tienden a concentrarse en los bordes de las clases de equivalencia, no en el centro.

Por ejemplo, si una función acepta valores entre 1 y 100, los valores más propensos a fallar son 0, 1, 100 y 101 — no el valor 50.

Se analizan:
- El **límite inferior**: el valor mínimo aceptable y el valor justo por debajo.
- El **límite superior**: el valor máximo aceptable y el valor justo por encima.

**Cómo se aplica:**
1. Se identifica el rango válido de entrada.
2. Se prueban los valores en los bordes: justo dentro del límite y justo fuera.
3. Se verifica que el sistema acepte los valores límite válidos y rechace los inválidos.

---

### Ejemplos concretos del proyecto

#### Ejemplo 1 — Partición de Equivalencia aplicada a ObraSocial

La función `ObraSocial.__init__()` acepta solo tres obras sociales válidas. El dominio de entrada se divide en:

| Clase | Ejemplo | Resultado esperado |
|-------|---------|-------------------|
| Válida | "OSDE" | Se crea el objeto correctamente |
| Inválida | "Swiss Medical" | Se lanza ValueError |

#### Ejemplo 2 — Valor Límite aplicado a TurnoFactory (horario)

La función `TurnoFactory.crear()` acepta horarios entre 08:00 y 20:00. Los valores límite son:

| Valor | Tipo | Resultado esperado |
|-------|------|-------------------|
| "07:59" | Límite inferior inválido | ValueError |
| "08:00" | Límite inferior válido | Turno creado |
| "20:00" | Límite superior válido | Turno creado |
| "20:01" | Límite superior inválido | ValueError |

---

## B1. Casos de Prueba Unitaria

Archivo: `tests/unit/test_logica.py`

---

### Grupo 1 — TurnoFactory: validación de fecha

| # | Método | Técnica | Entrada | Resultado esperado |
|---|--------|---------|---------|-------------------|
| 1 | `TurnoFactory.crear()` | Valor límite inferior | fecha = ayer | ValueError: "fecha pasada" |
| 2 | `TurnoFactory.crear()` | Valor límite exacto | fecha = hoy | Turno creado correctamente |
| 3 | `TurnoFactory.crear()` | Clase válida | fecha = hoy + 7 días | Turno creado correctamente |

---

### Grupo 2 — TurnoFactory: validación de horario

| # | Método | Técnica | Entrada | Resultado esperado |
|---|--------|---------|---------|-------------------|
| 4 | `TurnoFactory.crear()` | Valor límite inferior inválido | hora = "07:59" | ValueError: horario inválido |
| 5 | `TurnoFactory.crear()` | Valor límite inferior válido | hora = "08:00" | Turno creado correctamente |
| 6 | `TurnoFactory.crear()` | Valor límite superior válido | hora = "20:00" | Turno creado correctamente |
| 7 | `TurnoFactory.crear()` | Valor límite superior inválido | hora = "20:01" | ValueError: horario inválido |

---

### Grupo 3 — ObraSocial: partición de equivalencia

| # | Método | Técnica | Entrada | Resultado esperado |
|---|--------|---------|---------|-------------------|
| 8 | `ObraSocial.__init__()` | Clase válida | "OSDE" | cobertura = 90% |
| 9 | `ObraSocial.__init__()` | Clase inválida | "Swiss Medical" | ValueError |
| 10 | `ObraSocial.__init__()` | Clase válida | "IPS Misiones" | cobertura = 80% |

---

### Grupo 4 — CalculoCosto: con y sin obra social

| # | Método | Técnica | Entrada | Resultado esperado |
|---|--------|---------|---------|-------------------|
| 11 | `CalculoCosto.calcular()` | Clase válida | Paciente sin OS | paga_paciente = $10.000 |
| 12 | `CalculoCosto.calcular()` | Clase válida | Paciente con OSDE | paga_paciente = $1.000 |
| 13 | `CalculoCosto.calcular()` | Clase válida | Paciente con OSECAC | paga_paciente = $2.500 |

---

### Grupo 5 — State: transiciones del turno

| # | Método | Técnica | Entrada | Resultado esperado |
|---|--------|---------|---------|-------------------|
| 14 | `EstadoPendiente.confirmar()` | Clase válida | Turno PENDIENTE | Estado → CONFIRMADO |
| 15 | `EstadoPendiente.atender()` | Clase inválida | Turno PENDIENTE | ValueError |
| 16 | `EstadoConfirmado.atender()` | Clase válida | Turno CONFIRMADO | Estado → EN ATENCION |
| 17 | `EstadoCompletado.cancelar()` | Clase inválida | Turno COMPLETADO | ValueError |

---

### Grupo 6 — ValidadorCobertura: Singleton

| # | Método | Técnica | Entrada | Resultado esperado |
|---|--------|---------|---------|-------------------|
| 18 | `ValidadorCobertura.__new__()` | Clase válida | Dos instancias | Son el mismo objeto (is) |
| 19 | `ValidadorCobertura.validar()` | Clase válida | Paciente sin OS | válido = True |
| 20 | `ValidadorCobertura.validar()` | Clase válida | Paciente con IPS Misiones | válido = True |

---

## Cómo ejecutar las pruebas

Desde la carpeta raíz del proyecto:

```bash
python -m pytest tests/unit/test_logica.py -v
```

O con unittest:

```bash
python -m unittest tests/unit/test_logica.py -v
```

---

## Resultado esperado al correr las pruebas

```
test_caso1_fecha_pasada_levanta_error ... ok
test_caso2_fecha_hoy_es_valida ... ok
test_caso3_fecha_futura_es_valida ... ok
test_caso4_horario_antes_de_apertura ... ok
test_caso5_horario_limite_apertura_valido ... ok
test_caso6_horario_limite_cierre_valido ... ok
test_caso7_horario_despues_cierre ... ok
test_caso8_obra_social_valida ... ok
test_caso9_obra_social_invalida ... ok
test_caso10_ips_misiones ... ok
test_caso11_sin_obra_social_paga_total ... ok
test_caso12_con_osde_paga_10_porciento ... ok
test_caso13_con_osecac_paga_25_porciento ... ok
test_caso14_pendiente_puede_confirmar ... ok
test_caso15_pendiente_no_puede_atender ... ok
test_caso16_confirmado_puede_atender ... ok
test_caso17_completado_no_puede_cancelar ... ok
test_caso18_singleton_misma_instancia ... ok
test_caso19_validar_sin_obra_social ... ok
test_caso20_validar_con_obra_social_valida ... ok

Ran 20 tests in 0.XXXs
OK
```

---

## B3 — Diseño conceptual de pruebas de integración

> ⚠️ Esta sección es **conceptual**. Las pruebas de integración no se implementan en esta entrega — se diseñan para la siguiente iteración del proyecto cuando el sistema migre a persistencia real.

---

### Dependencias externas identificadas

El sistema actualmente opera con almacenamiento en memoria (listas Python en `logica.py`). En su evolución hacia producción, tendrá dos dependencias externas que hoy no existen pero que son inevitables: la base de datos SQLite gestionada por Django ORM y el sistema de autenticación de Django.

---

### Dependencia 1 — Base de datos SQLite con Django ORM

**Descripción en el sistema actual:**

Hoy el sistema guarda turnos, médicos y pacientes en objetos Python en memoria a través de clases como `TurnoRepositorio`, `MedicoRepositorio` y similares definidas en `logica.py`. Cuando el sistema migre a Django ORM con SQLite, todas las operaciones de `repositorio.agregar(turno)`, `repositorio.buscar(id)` y `repositorio.listar()` pasarán a ser queries SQL reales ejecutadas sobre el archivo `db.sqlite3`.

**Por qué es crítica para las pruebas:**

Una prueba que toca la base de datos real es lenta, deja datos sucios entre tests y puede fallar por razones ajenas al código (permisos de archivo, BD bloqueada, datos de otro test). Si se prueba `TurnoFactory.crear()` con persistencia real, el test deja un turno en la BD que puede romper el test siguiente si este asume que la BD está vacía.

**Cómo se mockearía:**

Se reemplaza el repositorio real por un objeto falso usando `unittest.mock.patch`, configurado para devolver datos controlados sin ejecutar ninguna query. El test verifica que el código llamó al repositorio correctamente, no que la BD tenga los datos.

```python
# Cómo se mockearía la dependencia de SQLite/Django ORM

from unittest.mock import patch, MagicMock
from datetime import date, timedelta
from logica import TurnoFactory, Paciente, ObraSocial, medico_repo

@patch('logica.TurnoRepositorio.agregar')
@patch('logica.TurnoRepositorio.buscar')
def test_crear_turno_se_persiste_correctamente(mock_buscar, mock_agregar):
    # Arrange — configurar el stub del repositorio
    paciente     = Paciente("Juan Pérez", "12345678", "3764000001", "juan@mail.com")
    medico       = medico_repo.buscar_por_matricula("MP-1001")
    fecha_futura = (date.today() + timedelta(days=5)).isoformat()

    turno_mock        = MagicMock()
    turno_mock.id     = 1
    turno_mock.estado = "PENDIENTE"
    mock_buscar.return_value = turno_mock

    # Act
    turno = TurnoFactory.crear(paciente, medico, fecha_futura, "10:00")
    repositorio.agregar(turno)
    resultado = repositorio.buscar(1)

    # Assert
    assert resultado.estado == "PENDIENTE"
    mock_agregar.assert_called_once()        # se llamó al guardar exactamente una vez
    mock_buscar.assert_called_once_with(1)   # se buscó por el ID correcto
```

**Alternativa con BD de prueba en memoria:**

Django también permite configurar una base de datos SQLite en memoria solo para tests, que se crea y destruye en cada ejecución sin afectar la BD real:

```python
# settings_test.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',   # BD en memoria, se destruye al terminar el test
    }
}
```

---

### Dependencia 2 — Sistema de autenticación Django (`django.contrib.auth`)

**Descripción en el sistema actual:**

El sistema distingue cuatro roles: Administrador, Recepcionista, Médico y Paciente. El acceso a cada vista en `views.py` depende del usuario autenticado en la sesión activa de Django. Por ejemplo, solo una Recepcionista puede acceder a la vista de creación de turnos; un Paciente que intente acceder debe ser redirigido.

Esta lógica de control de acceso está acoplada al sistema de autenticación de Django, que a su vez depende de la tabla de usuarios en la BD. En una prueba de integración de las vistas, habría que simular ese usuario autenticado sin crear registros reales en la BD ni pasar por el flujo real de login.

**Por qué es crítica para las pruebas:**

Sin mockear la autenticación, cada test de vista necesitaría: (1) crear un usuario en la BD de prueba, (2) hacer POST al endpoint de login con credenciales, (3) manejar la cookie de sesión en cada request. Eso acopla el test al sistema de autenticación completo y lo hace frágil ante cambios en el modelo de usuario.

**Cómo se mockearía:**

Django provee `Client.force_login()` que inyecta un usuario autenticado en la sesión sin pasar por el flujo real de login. Combinado con `MagicMock`, permite simular cualquier rol sin tocar la BD de usuarios.

```python
# Cómo se mockearía la autenticación por rol

from django.test import TestCase, Client
from unittest.mock import MagicMock, patch

class TestVistaCrearTurno(TestCase):

    def setUp(self):
        self.client = Client()

    def test_recepcionista_puede_ver_formulario_de_turno(self):
        # Stub: simular usuario con rol RECEPCIONISTA sin crear registro en BD
        usuario_mock          = MagicMock()
        usuario_mock.rol      = "RECEPCIONISTA"
        usuario_mock.username = "secretaria"
        usuario_mock.is_authenticated = True

        # Inyectar usuario sin pasar por login real
        self.client.force_login(usuario_mock)

        response = self.client.get('/turnos/crear/')

        # La recepcionista debe ver el formulario (200 OK)
        self.assertEqual(response.status_code, 200)

    def test_usuario_no_autenticado_es_redirigido(self):
        # Sin login → debe redirigir al login (302)
        response = self.client.get('/turnos/crear/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response['Location'])

    def test_paciente_no_puede_crear_turno(self):
        # Stub: usuario con rol PACIENTE
        usuario_mock          = MagicMock()
        usuario_mock.rol      = "PACIENTE"
        usuario_mock.is_authenticated = True

        self.client.force_login(usuario_mock)
        response = self.client.get('/turnos/crear/')

        # El paciente no tiene acceso → 403 Forbidden o redirect
        self.assertIn(response.status_code, [302, 403])
```

---

### Flujo de prueba de integración — ejemplo completo

**Escenario:** una recepcionista crea un turno para un paciente con OSDE. El sistema valida la cobertura, crea el turno en PENDIENTE, lo persiste en SQLite y dispara las notificaciones Observer.

```
DADO que:
  - Existe un médico "Dr. García" con matrícula "MP-1001" y especialidad "Cardiología"
  - Existe un paciente "Juan Pérez" con DNI "12345678" y obra social "OSDE"
  - La recepcionista está autenticada en el sistema (simulada con force_login)
  - El repositorio de turnos está mockeado (no toca SQLite real)
  - El ValidadorCobertura devuelve (True, "Cobertura válida: OSDE")

CUANDO la recepcionista envía el formulario POST con:
  - medico_id    = "MP-1001"
  - especialidad = "Cardiología"
  - fecha        = "2025-06-15"   ← fecha futura válida
  - hora         = "10:00"        ← dentro del rango 08:00-20:00
  - paciente_dni = "12345678"

ENTONCES el sistema debe ejecutar en orden:
  1. Autenticar a la recepcionista → verificar rol = RECEPCIONISTA
  2. Llamar a ValidadorCobertura.validar(paciente) → recibir (True, msg)
  3. Llamar a TurnoFactory.crear(paciente, medico, "2025-06-15", "10:00")
     → el turno nace con estado = "PENDIENTE"  (patrón State)
     → se suscriben EmailObservador y ConsoleObservador  (patrón Observer)
  4. Llamar a repositorio.agregar(turno) exactamente una vez
  5. Observer dispara: EmailObservador.actualizar(turno, "Tu turno fue creado")
  6. La vista redirige a /turnos/panel/ con código 302
  7. El mensaje flash contiene "Turno #1 creado para Juan Pérez"

VERIFICACIONES de los mocks:
  mock_validador.validar.assert_called_once_with(paciente)
  mock_repositorio.agregar.assert_called_once()
  mock_email_observer.actualizar.assert_called_once()
  assert response.status_code == 302
  assert "Turno #1 creado" in [str(m) for m in get_messages(response.wsgi_request)]

ESCENARIO ALTERNATIVO — obra social inválida:
  DADO que el paciente tiene obra social "Swiss Medical" (no registrada)
  CUANDO la recepcionista envía el formulario
  ENTONCES:
    - ValidadorCobertura.validar() retorna (False, "'Swiss Medical' no es válida.")
    - TurnoFactory.crear() NO se llama
    - repositorio.agregar() NO se llama
    - La vista devuelve 200 con mensaje de error visible en el formulario
    - No se genera ninguna notificación Observer
```

---

### Herramienta recomendada: `unittest.mock`

| Criterio | Detalle |
|---|---|
| **Nombre** | `unittest.mock` |
| **Incluida en** | Python estándar desde 3.3 — sin instalación |
| **Compatibilidad** | 100% con pytest, unittest y Django Test Client |
| **Licencia** | Gratuita y open source |
| **Complemento** | `pytest-mock` como wrapper opcional |

**Justificación:**

Se eligió `unittest.mock` porque viene incluida en la biblioteca estándar de Python, sin requerir ninguna dependencia adicional. El proyecto usa Python con Django y pytest, por lo que la integración es inmediata.

Cubre los tres tipos de dobles de prueba que el sistema necesitará al integrar SQLite y autenticación:

- **`MagicMock`** — crea objetos falsos que simulan el repositorio, el usuario autenticado o cualquier clase del sistema sin instanciar nada real ni tocar la BD.
- **`patch`** — reemplaza temporalmente cualquier función o método durante el test (por ejemplo, `TurnoRepositorio.agregar`) y lo restaura automáticamente al terminar, sin afectar otros tests.
- **`assert_called_once` / `assert_called_with`** — verifican que el código llamó exactamente a los métodos que debía, con los parámetros correctos. Fundamental para verificar que el Observer se disparó y que el repositorio fue llamado.

```python
# Resumen de los tres usos en el proyecto

from unittest.mock import patch, MagicMock

# 1. Mockear el repositorio SQLite
with patch('logica.TurnoRepositorio.agregar') as mock_repo:
    mock_repo.return_value = None
    # ... ejecutar acción
    mock_repo.assert_called_once()

# 2. Mockear el validador de cobertura
with patch('logica.ValidadorCobertura.validar') as mock_validar:
    mock_validar.return_value = (True, "Cobertura válida: OSDE")
    # ... ejecutar acción
    mock_validar.assert_called_once()

# 3. Mockear el Observer para verificar notificaciones
with patch('logica.EmailObservador.actualizar') as mock_email:
    # ... ejecutar acción que cambia estado del turno
    mock_email.assert_called_once()
```
