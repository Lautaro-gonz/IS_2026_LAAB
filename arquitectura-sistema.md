# Arquitectura del Sistema — Sistema de Gestión de Turnos

> Ingeniería de Software II · UCP · 2026  
> Trabajo Práctico 1 · Python puro + Django

---

## Descripción general

El sistema está construido en dos capas completamente independientes entre sí. La primera es la **lógica de dominio**, escrita en Python puro y contenida en un único archivo (`sistemadeturno.py`). La segunda es la **interfaz web**, construida con Django, que consume la lógica anterior sin modificarla.

Esta separación es intencional: los patrones de diseño y las reglas de negocio funcionan por sí solos sin necesidad de un servidor web. Django únicamente agrega la capa de presentación y autenticación.

```
sistemadeturno.py     ←  Lógica de dominio (Python puro, sin dependencias externas)
django_app/           ←  Interfaz web con login y paneles por rol
```

---

## Clases del dominio

### ObraSocial

Representa una obra social válida en el sistema. Las tres obras sociales soportadas son IPS Misiones, OSECAC y OSDE, cada una con su porcentaje de cobertura definido como constante de clase. Si se intenta instanciar una obra social con un nombre no reconocido, el constructor lanza `ValueError` inmediatamente, evitando que el error aparezca más adelante en el cálculo de costos.

```python
class ObraSocial:
    COBERTURAS = {
        "IPS Misiones": 80.0,
        "OSECAC":       75.0,
        "OSDE":         90.0,
    }
    def __init__(self, nombre: str):
        if nombre not in self.COBERTURAS:
            raise ValueError(f"Obra social '{nombre}' no valida.")
        self.cobertura = self.COBERTURAS[nombre]
```

---

### Paciente

Almacena los datos del paciente. El teléfono, el email y la obra social son opcionales: un paciente puede no tener ninguno de los tres. El Observer usa la presencia o ausencia de teléfono y email para decidir qué notificadores suscribir al crear el turno. Un paciente sin obra social puede atenderse y paga el costo completo de la consulta.

```python
class Paciente:
    def __init__(self, nombre: str, dni: str,
                 telefono: str = '', email: str = '',
                 obra_social: ObraSocial = None):
        self.nombre      = nombre
        self.dni         = dni
        self.telefono    = telefono
        self.email       = email
        self.obra_social = obra_social
```

---

### Especialidad y Medico

`Especialidad` es un `Enum` con seis valores que representa las especialidades médicas disponibles en el sistema. `Medico` la usa como tipo del atributo `especialidad`, garantizando que no se pueda crear un médico con una especialidad inválida.

```python
class Especialidad(Enum):
    CLINICA_MEDICA = "Clinica Medica"
    PEDIATRIA      = "Pediatria"
    CARDIOLOGIA    = "Cardiologia"
    GINECOLOGIA    = "Ginecologia"
    TRAUMATOLOGIA  = "Traumatologia"
    DERMATOLOGIA   = "Dermatologia"

class Medico:
    def __init__(self, nombre: str, especialidad: Especialidad, matricula: str):
        self.nombre       = nombre
        self.especialidad = especialidad
        self.matricula    = matricula
```

---

### CalculoCosto

Calcula cuánto paga el paciente por la consulta según su obra social. Se implementó como método estático porque el cálculo no necesita estado propio: recibe un paciente y devuelve un diccionario con el monto que cubre la obra social y el monto que paga el paciente. Si el paciente no tiene obra social, el costo completo recae sobre él.

| Obra social    | Cobertura | Paga el paciente |
|----------------|-----------|------------------|
| Sin obra social | 0%       | $10.000          |
| IPS Misiones   | 80%       | $2.000           |
| OSECAC         | 75%       | $2.500           |
| OSDE           | 90%       | $1.000           |

```python
class CalculoCosto:
    COSTO_CONSULTA = 10000.0

    @staticmethod
    def calcular(paciente: Paciente) -> dict:
        if paciente.obra_social is None:
            return {"paga_paciente": 10000.0, "cubre_os": 0.0}
        cob = paciente.obra_social.cobertura
        monto_os = round(10000 * cob / 100, 2)
        return {"cubre_os": monto_os, "paga_paciente": 10000 - monto_os}
```

---

### Turno

Clase central del sistema. Al instanciarse, genera un ID único automático mediante un contador de clase, calcula el costo llamando a `CalculoCosto`, inicializa su estado en `EstadoPendiente` (patrón State) y prepara la lista de observadores vacía (patrón Observer).

```python
class Turno:
    _contador = 0

    def __init__(self, paciente, medico, fecha, hora):
        Turno._contador   += 1
        self.id            = Turno._contador
        self.paciente      = paciente
        self.medico        = medico
        self.fecha         = fecha
        self.hora          = hora
        self._estado       = EstadoPendiente()   # State
        self._observadores = []                   # Observer
        self.costo         = CalculoCosto.calcular(paciente)
```

---

### SistemaTurnos

Registro global de todos los turnos activos en memoria. Expone cuatro métodos: agregar un turno, buscar todos los turnos de un paciente por DNI, buscar un objeto paciente por DNI, y obtener la agenda del día de un médico filtrando por fecha.

```python
class SistemaTurnos:
    def agregar(self, turno): ...
    def buscar_por_paciente(self, dni): ...
    def buscar_paciente_por_dni(self, dni): ...
    def agenda_del_dia(self, medico, fecha): ...
```

---

## Patrones de diseño

### State — estados del turno

**Problema que resuelve:** el comportamiento de un turno varía completamente según su estado. Sin el patrón State, la clase `Turno` necesitaría una cadena de `if/elif` para cada operación, lo que hace el código frágil y difícil de extender.

**Solución aplicada:** se define una clase abstracta `EstadoTurno` y cinco clases concretas, una por cada estado posible. La clase `Turno` delega todas las operaciones al objeto de estado actual. Si una operación no es válida en el estado actual, el estado concreto lanza `ValueError` con un mensaje descriptivo.

**Diagrama de transiciones:**

```
                  ┌─────────────┐
                  │   PENDIENTE  │
                  └──────┬───── ┘
          confirmar()    │    cancelar()
              ┌──────────┴──────────┐
              ▼                     ▼
      ┌─────────────┐        ┌─────────────┐
      │  CONFIRMADO  │        │  CANCELADO  │
      └──────┬───── ┘        └─────────────┘
    atender() │    cancelar()       ▲
              │    ─────────────────┘
              ▼
      ┌─────────────┐
      │ EN ATENCIÓN │
      └──────┬───── ┘
  completar()│
             ▼
      ┌─────────────┐
      │  COMPLETADO  │
      └─────────────┘
```

**Tabla de transiciones válidas:**

| Estado        | Puede hacer                          | No puede hacer                  |
|---------------|--------------------------------------|---------------------------------|
| `PENDIENTE`   | confirmar, cancelar, reprogramar     | atender, completar              |
| `CONFIRMADO`  | atender, cancelar, reprogramar*      | confirmar, completar            |
| `EN ATENCIÓN` | completar                            | todo lo demás                   |
| `COMPLETADO`  | —                                    | todo — lanza `ValueError`       |
| `CANCELADO`   | —                                    | todo — lanza `ValueError`       |

> \* Al reprogramar desde `CONFIRMADO`, el turno vuelve a `PENDIENTE` porque la nueva fecha requiere nueva confirmación.

---

### Observer — notificaciones automáticas

**Problema que resuelve:** cada vez que un turno cambia de estado, el sistema debe notificar al paciente. Sin el patrón Observer, la clase `Turno` tendría que conocer todos los canales de notificación posibles y decidir cuáles usar, acoplando la lógica de negocio con la lógica de comunicación.

**Solución aplicada:** se define una interfaz `ObservadorTurno` con un único método `notificar()`. Se implementan tres observadores concretos: `EmailObservador`, `SMSObservador` y `ConsoleObservador`. Al crear el turno, se suscriben automáticamente los observadores que corresponden según los datos del paciente. Cuando el estado cambia, el turno llama a `notificar()` en todos sus observadores sin saber qué hace cada uno.

```python
# Suscripción automática al crear el turno
if paciente.email:    turno.suscribir(EmailObservador(paciente.email))
if paciente.telefono: turno.suscribir(SMSObservador(paciente.telefono))
turno.suscribir(ConsoleObservador())  # siempre activo
```

**Ejemplo de salida al confirmar un turno:**

```
[EMAIL -> ana@mail.com]   Turno #1: Tu turno fue CONFIRMADO
[SMS -> +549376111111]    Turno #1: Tu turno fue CONFIRMADO
[LOG]                     Turno #1 | CONFIRMADO | Tu turno fue CONFIRMADO
```

---

## Interfaz web (Django)

La aplicación web está organizada en dos apps: `turnos` (lógica de vistas y formularios) y `accounts` (autenticación y gestión de sesiones). La lógica de dominio en `sistemadeturno.py` no se modificó al agregar Django; simplemente se importa desde las vistas.

### Roles y paneles

| Panel            | Rol                   | Funcionalidades                                         |
|------------------|-----------------------|---------------------------------------------------------|
| Login            | Todos                 | Autenticación con usuario y contraseña                  |
| Panel secretaria | `secretaria`, `admin` | Ver agenda, confirmar, cancelar y reprogramar turnos    |
| Nuevo turno      | `secretaria`, `admin` | Formulario con cálculo automático de costo              |
| Panel doctor     | `doctor`              | Ver agenda del día filtrada por su nombre               |
| Panel paciente   | `paciente`            | Buscar turnos propios por DNI                           |

---

## Menú interactivo (consola)

Además de la interfaz web, el sistema incluye un menú en consola para interactuar directamente con la lógica de dominio. Las funciones de validación están separadas de la lógica de negocio.

| Opción | Función              | Descripción                                               |
|--------|----------------------|-----------------------------------------------------------|
| 1      | `solicitar_turno()`  | Valida datos, calcula costo, crea turno y suscribe observadores |
| 2      | `confirmar_turno()`  | Transición PENDIENTE → CONFIRMADO, notifica               |
| 3      | `cancelar_turno()`   | Cancela con motivo, notifica                              |
| 4      | `reprogramar_turno()`| Cambia fecha y hora, notifica                             |
| 5      | `ver_agenda()`       | Filtra turnos por médico y fecha                          |
| 6      | `ver_mis_turnos()`   | Busca todos los turnos de un paciente por DNI             |

### Validaciones implementadas

- `pedir_texto()` — no acepta campos vacíos
- `pedir_dni()` — solo dígitos, mínimo 7 caracteres
- `pedir_fecha()` — valida formato `AAAA-MM-DD`
- `pedir_hora()` — valida formato `HH:MM`

---

## Decisiones de diseño relevantes

**Un solo archivo para el TP1.** Se eligió concentrar toda la lógica en `sistemadeturno.py` para simplificar la entrega y facilitar la revisión. En el TP2 se evaluará dividirlo en módulos.

**Paciente sin obra social puede atenderse.** La versión inicial del sistema rechazaba a pacientes sin obra social. Se corrigió porque en una clínica privada real cualquier paciente puede atenderse; la obra social solo determina cuánto paga.

**Estado como objeto, no como Enum.** El diagrama original usaba un Enum simple para representar el estado del turno. Se reemplazó por clases concretas con el patrón State para encapsular el comportamiento de cada estado y eliminar los condicionales de la clase `Turno`.

**Observadores suscritos automáticamente.** Los notificadores no se agregan manualmente: la lógica de suscripción al crear el turno evalúa si el paciente tiene email y/o teléfono y suscribe los observadores correspondientes. `ConsoleObservador` siempre se suscribe como registro de auditoría.

---

> *Ingeniería de Software II · Universidad de la Cuenca del Plata · 2026*
