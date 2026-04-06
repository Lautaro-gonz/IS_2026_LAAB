# Patrones de Diseño — TP1

**Proyecto:** Sistema de Gestión de Turnos — Clínica Médica  
**Entrega:** TP1  
    EQUIPO: LAAB
---

## Índice

- [Observer (Comportamental)](#patrón-1-observer)
- [State (Comportamental)](#patrón-2-state)
- [Singleton (Creacional)](#patrón-3-singleton)
- [Factory Method (Creacional)](#patrón-4-factory-method)

---

## Resumen

| Patrón | Clase principal | Problema que resuelve |
|---|---|---|
| Observer | `ObservadorTurno` | Notificaciones desacopladas del turno |
| State | `EstadoTurno` | Estados sin if/elif en la clase Turno |
| Singleton | `ValidadorCobertura` | Un solo validador en todo el sistema |
| Factory Method | `TurnoFactory` | Creación de turnos con observadores automáticos |

---

# Patrón 1: Observer

### Intención

Definir una dependencia uno-a-muchos entre objetos, de modo que cuando uno cambia de estado todos sus dependientes sean notificados automáticamente, sin que el sujeto conozca a sus observadores concretos.

### Problema que resuelve en el sistema

Cuando un `Turno` cambia de estado, el sistema necesita reaccionar de múltiples formas simultáneas:

- Notificar al paciente por **email** que su turno fue creado o modificado
- Notificar al paciente por **SMS** con los datos del turno
- Registrar el evento en **consola** para auditoría interna

Sin Observer, la clase `Turno` tendría que conocer y llamar directamente a cada canal:

```python
# ❌ Sin patrón — acoplamiento fuerte
class Turno:
    def confirmar(self):
        self._estado = EstadoConfirmado()
        EmailObservador(self.paciente.email).actualizar(self, "Turno confirmado")
        SMSObservador(self.paciente.telefono).actualizar(self, "Turno confirmado")
        ConsoleObservador().actualizar(self, "Turno confirmado")
        # Si mañana se agrega un canal de WhatsApp
        # → hay que modificar la clase Turno ❌
```

Cada nuevo canal de notificación fuerza una modificación en `Turno`, violando el principio Open/Closed y aumentando el acoplamiento.

### Justificación de la elección

Se eligió Observer porque el problema es exactamente para el que fue diseñado: un objeto (`Turno`) genera eventos en cada transición de estado, y múltiples canales deben reaccionar a esos eventos sin que el turno los conozca.

**¿Por qué Observer y no llamadas directas?**  
Con llamadas directas, `Turno` queda acoplado a `EmailObservador`, `SMSObservador` y `ConsoleObservador`. Con Observer, `Turno` solo conoce la interfaz `ObservadorTurno`. Agregar un nuevo canal no requiere tocar `Turno` en absoluto.

**¿Por qué Observer y no Mediator?**  
Mediator centraliza comunicación bidireccional entre múltiples objetos. Observer es más simple y directo para este caso concreto de "un emisor, múltiples receptores pasivos". Agregar Mediator sería sobrediseño para este escenario.

### Clases involucradas

| Clase | Rol en el patrón | Archivo |
|---|---|---|
| `ObservadorTurno` | Observer abstracto (interfaz) | `turnos/logica.py` |
| `EmailObservador` | Observer concreto — canal email | `turnos/logica.py` |
| `SMSObservador` | Observer concreto — canal SMS | `turnos/logica.py` |
| `ConsoleObservador` | Observer concreto — log de consola | `turnos/logica.py` |
| `Turno` | Subject (sujeto observable) | `turnos/logica.py` |
| `TurnoFactory` | Inyecta los observers al crear el turno | `turnos/logica.py` |

### Relaciones entre clases

```
ObservadorTurno  (abstract)
    ├── EmailObservador
    ├── SMSObservador
    └── ConsoleObservador

Turno  (Subject)
    ├── suscribir(ObservadorTurno)
    └── notificar(mensaje)  →  obs.actualizar(self, mensaje)

TurnoFactory
    └── crea Turno e inyecta los observers según datos del paciente
```

### Funcionamiento general

1. `TurnoFactory.crear()` instancia el `Turno` y le inyecta los observers según los datos del paciente: si tiene email agrega `EmailObservador`, si tiene teléfono agrega `SMSObservador`, y siempre agrega `ConsoleObservador`.
2. Cada vez que el turno cambia de estado (confirmar, cancelar, reprogramar, atender, completar), el estado concreto llama a `turno.notificar(mensaje)`.
3. `notificar()` itera la lista `_observadores` y llama `obs.actualizar(self, mensaje)` en cada uno.
4. Cada observer decide qué hacer: `EmailObservador` imprime la notificación simulada al email, `SMSObservador` al teléfono, y `ConsoleObservador` registra el log interno.

### Código del proyecto

```python
# turnos/logica.py

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
```

```python
# Turno — Subject que suscribe y notifica sin conocer a los observers concretos

class Turno:
    def __init__(self, paciente, medico, fecha, hora):
        self._observadores = []
        ...

    def suscribir(self, observador):
        self._observadores.append(observador)

    def notificar(self, mensaje):
        for obs in self._observadores:
            obs.actualizar(self, mensaje)   # Turno NO sabe qué hace cada observer
```

```python
# TurnoFactory — inyecta los observers según los datos disponibles del paciente

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
```

```python
# views.py — la vista usa TurnoFactory, nunca instancia Turno directamente

turno = TurnoFactory.crear(paciente, medico, fecha, hora)
repositorio.agregar(turno)
```

### Mejora que aporta

| Aspecto | Sin Observer | Con Observer |
|---|---|---|
| Acoplamiento | `Turno` conoce todos los canales | `Turno` solo conoce `ObservadorTurno` |
| Agregar canal WhatsApp | Modificar `Turno` | Crear `WhatsAppObservador(ObservadorTurno)` |
| Responsabilidad única | Violada — `Turno` notifica | `Turno` no sabe nada de los canales |
| Testabilidad | Difícil — efectos mezclados | Fácil — se inyectan mocks en el test |

---

# Patrón 2: State

### Intención

Permitir que un objeto altere su comportamiento cuando su estado interno cambia, encapsulando cada estado en su propia clase y delegando las transiciones a esas clases, eliminando condicionales anidados.

### Problema que resuelve en el sistema

`Turno` tiene 5 estados con transiciones estrictas:

```
PENDIENTE → CONFIRMADO → EN ATENCION → COMPLETADO
         ↘            ↘
          CANCELADO    CANCELADO
```

Sin State, toda la lógica de transición viviría en `Turno` como una cadena de condicionales:

```python
# ❌ Sin patrón — condicionales anidados y frágiles
class Turno:
    def confirmar(self):
        if self.estado == "PENDIENTE":
            self.estado = "CONFIRMADO"
        else:
            raise ValueError("No se puede confirmar un turno en estado " + self.estado)

    def cancelar(self, motivo=""):
        if self.estado in ["PENDIENTE", "CONFIRMADO"]:
            self.estado = "CANCELADO"
            self.motivo_cancelacion = motivo
        elif self.estado == "EN ATENCION":
            raise ValueError("No se puede cancelar un turno en atención.")
        else:
            raise ValueError("El turno ya está " + self.estado)

    # Cada nuevo estado o regla → modificar todos los métodos de Turno ❌
```

A medida que crecen los estados y las reglas, `Turno` se vuelve una clase difícil de mantener y propensa a errores.

### Justificación de la elección

Se eligió State porque el ciclo de vida del turno tiene reglas de transición claras y cada estado tiene comportamiento diferente. Encapsular cada estado en su propia clase hace que las reglas sean explícitas y que agregar un nuevo estado no requiera modificar `Turno`.

**¿Por qué State y no un simple enum con ifs?**  
Un enum alcanza para guardar el valor del estado, pero no para encapsular las reglas de transición. Con State, si intentás cancelar un turno `EN ATENCION`, es el propio estado quien rechaza la operación. Con ifs, esa validación queda dispersa en múltiples métodos de `Turno`.

**¿Por qué State y no Strategy?**  
Strategy varía el *cómo* se ejecuta un algoritmo intercambiable. State varía el comportamiento completo del objeto según su situación actual e incluye las reglas de qué transiciones están permitidas. El problema aquí es de ciclo de vida con restricciones, no de algoritmos intercambiables.

### Clases involucradas

| Clase | Rol en el patrón | Archivo |
|---|---|---|
| `EstadoTurno` | State abstracto (interfaz) | `turnos/logica.py` |
| `EstadoPendiente` | State concreto | `turnos/logica.py` |
| `EstadoConfirmado` | State concreto | `turnos/logica.py` |
| `EstadoEnAtencion` | State concreto | `turnos/logica.py` |
| `EstadoCompletado` | State concreto | `turnos/logica.py` |
| `EstadoCancelado` | State concreto | `turnos/logica.py` |
| `Turno` | Context — delega comportamiento al estado actual | `turnos/logica.py` |

### Relaciones entre clases

```
EstadoTurno  (abstract)
    ├── EstadoPendiente    →  puede confirmar, cancelar, reprogramar
    ├── EstadoConfirmado   →  puede atender, cancelar, reprogramar
    ├── EstadoEnAtencion   →  solo puede completar
    ├── EstadoCompletado   →  estado final, no permite nada
    └── EstadoCancelado    →  estado final, no permite nada

Turno  (Context)
    ├── _estado: EstadoTurno   (nace como EstadoPendiente)
    ├── set_estado(nuevo)
    ├── confirmar()   → delega a _estado.confirmar(self)
    ├── cancelar()    → delega a _estado.cancelar(self)
    ├── atender()     → delega a _estado.atender(self)
    ├── completar()   → delega a _estado.completar(self)
    └── reprogramar() → delega a _estado.reprogramar(self)
```

### Funcionamiento general

1. Al crearse, `Turno` recibe `EstadoPendiente()` como estado inicial.
2. Cada operación (`confirmar`, `cancelar`, `atender`, `completar`, `reprogramar`) se delega al objeto de estado actual mediante `self._estado.metodo(self)`.
3. El estado decide si la transición es válida. Si lo es, llama `turno.set_estado(NuevoEstado())` y luego `turno.notificar(mensaje)` — activando también el patrón Observer.
4. Si la transición no está permitida, el estado lanza un `ValueError` descriptivo sin que `Turno` tenga que saberlo.
5. `turno.estado` es una `@property` que delega a `self._estado.nombre()`, devolviendo el nombre del estado actual como string.

### Código del proyecto

```python
# turnos/logica.py — State abstracto

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
```

```python
# Estados concretos — cada uno encapsula sus propias reglas de transición

class EstadoPendiente(EstadoTurno):
    def confirmar(self, turno):
        turno.set_estado(EstadoConfirmado())
        turno.notificar("Tu turno fue CONFIRMADO")       # dispara Observer
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
        turno.hora  = nueva_hora
        turno.notificar(f"Turno REPROGRAMADO al {nueva_fecha} a las {nueva_hora}")
    def nombre(self): return "PENDIENTE"


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


class EstadoCancelado(EstadoTurno):
    def confirmar(self, turno):            raise ValueError("Turno cancelado.")
    def atender(self, turno):              raise ValueError("Turno cancelado.")
    def completar(self, turno):            raise ValueError("Turno cancelado.")
    def cancelar(self, turno, motivo=""):  raise ValueError("El turno ya está cancelado.")
    def reprogramar(self, turno, nf, nh):  raise ValueError("Turno cancelado.")
    def nombre(self): return "CANCELADO"
```

```python
# Turno — Context que delega todo al estado actual

class Turno:
    def __init__(self, paciente, medico, fecha, hora):
        self._estado = EstadoPendiente()   # nace siempre en PENDIENTE
        ...

    @property
    def estado(self):
        return self._estado.nombre()       # string legible del estado actual

    def set_estado(self, nuevo_estado):
        self._estado = nuevo_estado

    def confirmar(self):              self._estado.confirmar(self)
    def atender(self):                self._estado.atender(self)
    def completar(self):              self._estado.completar(self)
    def cancelar(self, motivo=""):    self._estado.cancelar(self, motivo)
    def reprogramar(self, nf, nh):    self._estado.reprogramar(self, nf, nh)
```

```python
# views.py — la vista llama al método del turno, State decide si es válido

try:
    if accion == 'confirmar':
        turno.confirmar()
    elif accion == 'cancelar':
        turno.cancelar(motivo)
    elif accion == 'atender':
        turno.atender()
    elif accion == 'completar':
        turno.completar()
except ValueError as e:
    messages.error(request, str(e))   # el estado lanzó la excepción, no Turno
```

### Mejora que aporta

| Aspecto | Sin State | Con State |
|---|---|---|
| Reglas de transición | Ifs dispersos en cada método de `Turno` | Encapsuladas en cada clase de estado |
| Agregar nuevo estado | Modificar todos los métodos de `Turno` | Crear una nueva clase que extiende `EstadoTurno` |
| Transiciones inválidas | Condiciones mezcladas, propensas a olvidos | Cada estado lanza su propio `ValueError` descriptivo |
| Legibilidad | Difícil saber qué permite cada estado | Cada clase de estado es autoexplicativa |

### Interacción con Observer

State y Observer se complementan naturalmente en este proyecto. Cuando un estado concreto ejecuta una transición válida, llama `turno.notificar(mensaje)` como parte de la misma operación. Esto significa que cada cambio de estado dispara automáticamente las notificaciones a todos los observers suscritos, sin que ninguna de las dos capas sepa de la otra.

```
Secretaria llama turno.confirmar()
    → EstadoPendiente.confirmar(turno)
        → turno.set_estado(EstadoConfirmado())      ← State
        → turno.notificar("Tu turno fue CONFIRMADO")
            → EmailObservador.actualizar(...)        ← Observer
            → SMSObservador.actualizar(...)          ← Observer
            → ConsoleObservador.actualizar(...)      ← Observer
```

---

# Patrón 3: Singleton

### Intención

Garantizar que una clase tenga una única instancia en todo el sistema y proporcionar un punto de acceso global a ella.

### Problema que resuelve en el sistema

`ValidadorCobertura` es el componente que verifica si una obra social es válida antes de crear un turno. Este validador consulta el conjunto `OBRAS_VALIDAS` que es compartido y estático. Sin Singleton, cualquier parte del código podría crear su propio validador:

```python
# ❌ Sin patrón — instancias duplicadas e inconsistentes
def crear_turno(request):
    validador = ValidadorCobertura()   # nueva instancia en cada request
    puede, msg = validador.validar(paciente)

def otra_vista(request):
    v = ValidadorCobertura()           # otra instancia diferente ❌
    v.validar(...)
```

En un sistema web con requests concurrentes, podrían generarse condiciones de carrera al inicializar múltiples instancias simultáneamente.

### Justificación de la elección

Se eligió Singleton porque `ValidadorCobertura` no tiene estado mutable — solo consulta una lista fija de obras sociales válidas — y debe comportarse igual en todo el sistema sin importar desde dónde se invoque. Tener una única instancia garantiza consistencia y evita inicializaciones redundantes.

**¿Por qué Singleton y no una función estática?**  
Una función estática no permite inyección de dependencias ni herencia futura. Con Singleton, `ValidadorCobertura` puede extenderse para validar contra una base de datos real en el futuro, sin cambiar la interfaz que usa el resto del sistema.

**¿Por qué Singleton y no una variable global?**  
Una variable global no controla su propia creación ni garantiza thread-safety. El Singleton implementado usa `threading.Lock()` con doble verificación para ser seguro ante accesos concurrentes, lo que una variable global no puede garantizar.

### Clases involucradas

| Clase | Rol en el patrón | Archivo |
|---|---|---|
| `ValidadorCobertura` | Singleton — única instancia del validador | `turnos/logica.py` |
| `validador` | Instancia global accesible desde views | `turnos/logica.py` |

### Relaciones entre clases

```
ValidadorCobertura
    ├── _instance: ValidadorCobertura = None   (atributo de clase)
    ├── _lock: threading.Lock                  (thread-safety)
    ├── __new__(cls)  →  controla la creación, devuelve siempre _instance
    └── validar(paciente)  →  verifica la obra social del paciente

views.py
    └── usa la instancia global `validador` importada desde logica.py
```

### Funcionamiento general

1. La primera vez que cualquier parte del sistema accede a `ValidadorCobertura()`, `__new__` detecta que `_instance` es `None` y crea la instancia real.
2. El `threading.Lock()` con doble verificación garantiza que si dos threads llegan al mismo tiempo, solo uno crea la instancia y el otro reutiliza la ya creada.
3. Todas las llamadas posteriores a `ValidadorCobertura()` devuelven siempre la misma instancia almacenada en `_instance`.
4. En `views.py`, la instancia global `validador` es importada directamente desde `logica.py`, donde fue creada una sola vez al cargar el módulo.

### Código del proyecto

```python
# turnos/logica.py

class ValidadorCobertura:
    _instance = None
    _lock = threading.Lock()
    OBRAS_VALIDAS = set(ObraSocial.COBERTURAS.keys())

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:                      # thread-safety
                if cls._instance is None:        # doble verificación
                    cls._instance = super().__new__(cls)
        return cls._instance

    def validar(self, paciente):
        if paciente.obra_social is None:
            return True, "Sin obra social — pagará el 100% ($10.000)"
        if paciente.obra_social.nombre not in self.OBRAS_VALIDAS:
            return False, f"'{paciente.obra_social.nombre}' no es válida."
        return True, f"Cobertura válida: {paciente.obra_social}"


# Instancia global — se crea una sola vez al cargar el módulo
validador = ValidadorCobertura()
```

```python
# views.py — usa siempre la misma instancia, sin necesidad de instanciar

from .logica import repositorio, validador, TurnoFactory, medico_repo, ...

def crear_turno(request):
    ...
    puede, msg = validador.validar(paciente)   # misma instancia en todo el sistema
    if not puede:
        error = msg
    else:
        turno = TurnoFactory.crear(paciente, medico, fecha, hora)
        repositorio.agregar(turno)
```

### Mejora que aporta

| Aspecto | Sin Singleton | Con Singleton |
|---|---|---|
| Instancias | Una nueva por cada llamada | Exactamente una en todo el sistema |
| Consistencia | Cada instancia podría tener estado diferente | Comportamiento garantizado uniforme |
| Thread-safety | Sin control ante concurrencia | `threading.Lock()` con doble verificación |
| Punto de acceso | Disperso — cada módulo crea el suyo | Centralizado — instancia global `validador` |

---

# Patrón 4: Factory Method

### Intención

Definir una interfaz para crear un objeto, pero dejar que sea una clase especializada quien decida cómo instanciarlo, evitando el acoplamiento entre el cliente y la lógica de construcción concreta.

### Problema que resuelve en el sistema

Crear un `Turno` no es simplemente instanciar el objeto. Implica también decidir qué observers suscribir según los datos disponibles del paciente. Sin Factory Method, esa lógica quedaría dispersa en cada lugar que crea un turno:

```python
# ❌ Sin patrón — lógica de construcción duplicada en la vista
def crear_turno(request):
    turno = Turno(paciente, medico, fecha, hora)
    if paciente.email:
        turno.suscribir(EmailObservador(paciente.email))
    if paciente.telefono:
        turno.suscribir(SMSObservador(paciente.telefono))
    turno.suscribir(ConsoleObservador())
    repositorio.agregar(turno)
    # Si en otra vista también se crean turnos → copiar todo esto ❌
    # Si se agrega un nuevo observer → modificar todas las vistas ❌
```

La lógica de construcción quedaría acoplada a la capa de presentación (views), que no debería saber nada de eso.

### Justificación de la elección

Se eligió Factory Method porque la creación de un `Turno` requiere lógica condicional que no pertenece ni a la vista ni al constructor del turno. `TurnoFactory` centraliza esa responsabilidad y es el único lugar donde se define cómo se construye un turno correctamente.

**¿Por qué Factory Method y no instanciación directa en la vista?**  
Con instanciación directa, la vista conoce los detalles de construcción y la lógica de suscripción de observers. Con Factory Method, la vista solo llama `TurnoFactory.crear(...)` y recibe un turno listo y correctamente configurado.

**¿Por qué Factory Method y no Builder?**  
Builder es apropiado cuando la construcción requiere muchos pasos secuenciales y opcionales. Crear un turno es una operación directa — Factory Method es la elección más simple y correcta para este caso.

**¿Por qué Factory Method y no Abstract Factory?**  
Abstract Factory está pensado para familias de objetos relacionados. En este sistema hay un solo tipo de turno con variaciones en sus observers. Factory Method cubre exactamente esa necesidad sin agregar complejidad innecesaria.

### Clases involucradas

| Clase | Rol en el patrón | Archivo |
|---|---|---|
| `TurnoFactory` | Creator — encapsula la lógica de creación | `turnos/logica.py` |
| `Turno` | Producto — objeto que se construye | `turnos/logica.py` |
| `EmailObservador` | Componente inyectado condicionalmente | `turnos/logica.py` |
| `SMSObservador` | Componente inyectado condicionalmente | `turnos/logica.py` |
| `ConsoleObservador` | Componente siempre inyectado | `turnos/logica.py` |

### Relaciones entre clases

```
TurnoFactory
    └── crear(paciente, medico, fecha, hora) → Turno
            ├── instancia Turno(...)
            ├── si paciente.email    → suscribe EmailObservador
            ├── si paciente.telefono → suscribe SMSObservador
            └── siempre             → suscribe ConsoleObservador

views.py (cliente)
    └── TurnoFactory.crear(...)   ← no conoce Turno ni sus observers
```

### Funcionamiento general

1. La vista recibe los datos del formulario (nombre, DNI, médico, fecha, hora, obra social).
2. Construye el `Paciente` y valida su cobertura usando el `ValidadorCobertura` (Singleton).
3. Llama a `TurnoFactory.crear(paciente, medico, fecha, hora)` — punto único de construcción.
4. `TurnoFactory` instancia el `Turno` y decide qué observers inyectar según los datos del paciente.
5. Devuelve el turno ya configurado y listo para ser guardado en el repositorio.
6. La vista solo llama `repositorio.agregar(turno)` sin saber cómo fue construido internamente.

### Código del proyecto

```python
# turnos/logica.py

class TurnoFactory:
    @staticmethod
    def crear(paciente, medico, fecha, hora):
        turno = Turno(paciente, medico, fecha, hora)
        if paciente.email:
            turno.suscribir(EmailObservador(paciente.email))    # condicional
        if paciente.telefono:
            turno.suscribir(SMSObservador(paciente.telefono))   # condicional
        turno.suscribir(ConsoleObservador())                    # siempre
        return turno
```

```python
# views.py — el cliente no sabe nada de la construcción interna

def crear_turno(request):
    ...
    puede, msg = validador.validar(paciente)                         # Singleton valida
    if not puede:
        error = msg
    else:
        turno = TurnoFactory.crear(paciente, medico, fecha, hora)    # Factory construye
        repositorio.agregar(turno)                                   # Repository persiste
        messages.success(request, f'Turno #{turno.id} creado para {nombre}.')
        return redirect('turnos:panel_secretaria')
```

### Mejora que aporta

| Aspecto | Sin Factory Method | Con Factory Method |
|---|---|---|
| Responsabilidad | Vista conoce cómo construir el turno | Vista solo llama `TurnoFactory.crear()` |
| Agregar nuevo observer | Modificar todas las vistas que crean turnos | Modificar solo `TurnoFactory.crear()` |
| Encapsulamiento | Lógica de construcción dispersa | Centralizada en un único método |
| Consistencia | Cada vista podría construir diferente | Todos los turnos se construyen igual |

### Interacción con los otros patrones

`TurnoFactory` es el punto donde convergen los cuatro patrones del sistema:

```
views.py llama TurnoFactory.crear(paciente, medico, fecha, hora)
    │
    ├── validador.validar(paciente)          ← Singleton — valida antes de crear
    │
    ├── Turno(paciente, medico, fecha, hora) ← State — nace en EstadoPendiente
    │
    └── turno.suscribir(EmailObservador)     ← Observer — observers inyectados
        turno.suscribir(SMSObservador)
        turno.suscribir(ConsoleObservador)
```
