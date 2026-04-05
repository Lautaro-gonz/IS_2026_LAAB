# Sistema de Gestión de Turnos — Clínica Privada

> **Ingeniería de Software II · UCP · 2026**  
> Trabajo Práctico 1 · Python + Django · UCP Inc.

---

## Descripción del proyecto

Este repositorio contiene el desarrollo del **Sistema de Gestión de Turnos** para una clínica privada, construido en el marco de la materia Ingeniería de Software II de la Universidad de la Cuenca del Plata.

El sistema permite a recepcionistas y pacientes gestionar turnos médicos de forma digital, reemplazando el proceso manual por teléfono y planillas Excel. Está implementado en **Python puro** con lógica de dominio orientada a objetos, e incorpora una **interfaz web en Django** con autenticación por roles.

---

## Funcionalidades implementadas

| Funcionalidad | Estado | Descripción |
|---|---|---|
| Solicitar turno | Completo | Selección de médico, especialidad, fecha y hora |
| Confirmar turno | Completo | Transición de estado PENDIENTE → CONFIRMADO |
| Cancelar turno | Completo | Con motivo, notifica automáticamente |
| Reprogramar turno | Completo | Cambia fecha/hora, vuelve a PENDIENTE |
| Ver agenda del médico | Completo | Filtra por médico y fecha |
| Ver turnos por paciente | Completo | Búsqueda por DNI |
| Cálculo de costo automático | Completo | Según obra social del paciente |
| Notificaciones | Completo | Email, SMS y consola (simulados) |
| Interfaz web con login | Completo | 4 roles: admin, secretaria, doctor, paciente |

---

## Arquitectura del sistema

El proyecto está dividido en dos capas independientes:

```
sistemadeturno.py   ← Lógica de dominio completa (Python puro)
django_app/         ← Interfaz web que consume la lógica anterior
```

La lógica de negocio **no depende de Django**. Los patrones de diseño están implementados en `sistemadeturno.py` y Django únicamente agrega la capa de presentación web.

### Clases principales

```
ObraSocial          Obras sociales soportadas y porcentajes de cobertura
Paciente            Datos del paciente, obra social opcional
Medico              Nombre, matrícula y especialidad (Enum con 6 valores)
CalculoCosto        Cálculo del monto según cobertura (método estático)
Turno               Clase central. Integra State y Observer
SistemaTurnos       Registro global de turnos en memoria
```

---

## Patrones de diseño

### State — gestión de estados del turno

Cada turno pasa por estados bien definidos. La clase `Turno` **no tiene ningún `if/elif`** para manejar estados: delega completamente al objeto de estado actual.

```
PENDIENTE → CONFIRMADO → EN ATENCIÓN → COMPLETADO
    ↓              ↓
 CANCELADO      CANCELADO
```

| Estado | Puede hacer | No puede hacer |
|---|---|---|
| `PENDIENTE` | confirmar, cancelar, reprogramar | atender, completar |
| `CONFIRMADO` | atender, cancelar, reprogramar* | confirmar, completar |
| `EN ATENCIÓN` | completar | todo lo demás |
| `COMPLETADO` | — | todo (lanza `ValueError`) |
| `CANCELADO` | — | todo (lanza `ValueError`) |

> \* Al reprogramar desde `CONFIRMADO`, el turno vuelve a `PENDIENTE` porque la nueva fecha requiere nueva confirmación.

### Observer — notificaciones automáticas

Cada vez que un turno cambia de estado, notifica automáticamente a todos los observadores suscritos. Los observadores se registran al crear el turno según los datos del paciente:

```python
if paciente.email:    turno.suscribir(EmailObservador(paciente.email))
if paciente.telefono: turno.suscribir(SMSObservador(paciente.telefono))
turno.suscribir(ConsoleObservador())  # siempre activo
```

---

## Lógica de obras sociales

El sistema soporta tres obras sociales regionales. Un paciente **sin obra social puede atenderse** y paga el costo completo de la consulta.

| Obra social | Cobertura | Paga el paciente |
|---|---|---|
| Sin obra social | 0% | $10.000 |
| IPS Misiones | 80% | $2.000 |
| OSECAC | 75% | $2.500 |
| OSDE | 90% | $1.000 |

---

## Interfaz web (Django)

La aplicación web tiene login con cuatro roles diferenciados:

| Panel | Rol | Funcionalidades |
|---|---|---|
| Login | Todos | Autenticación con usuario y contraseña |
| Panel secretaria | `secretaria` / `admin` | Ver agenda, confirmar, cancelar, reprogramar turnos |
| Nuevo turno | `secretaria` / `admin` | Formulario con cálculo automático de costo |
| Panel doctor | `doctor` | Ver agenda del día filtrada por su nombre |
| Panel paciente | `paciente` | Buscar turnos propios por DNI |

---

## Menú interactivo (consola)

Además de la interfaz web, el sistema incluye un menú en consola con 6 opciones:

```
[1] Solicitar turno
[2] Confirmar turno
[3] Cancelar turno
[4] Reprogramar turno
[5] Ver agenda del médico
[6] Ver mis turnos (por DNI)
```

Todas las entradas tienen validación: DNI (solo dígitos, mín. 7 caracteres), fechas (formato `AAAA-MM-DD`), horas (formato `HH:MM`) y campos de texto (no acepta vacíos).

---

## Instalación y ejecución local

### Requisitos

- Python 3.10 o superior
- pip

### 1. Clonar el repositorio

```bash
git clone https://github.com/ucpinc/sistema-turnos.git
cd sistema-turnos
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### 3a. Ejecutar en consola (sin Django)

```bash
python src/sistemadeturno.py
```

### 3b. Ejecutar la interfaz web (Django)

```bash
cd django_app
python manage.py migrate
python manage.py runserver
```

Luego abrí `http://127.0.0.1:8000` en el navegador.

---

## Estructura del repositorio

```
/
├── src/
│   └── sistemadeturno.py       # Lógica de dominio completa
├── django_app/
│   ├── turnos/                 # App principal
│   ├── accounts/               # Login y autenticación
│   └── manage.py
├── tests/                      # Pruebas unitarias (TP2)
├── design/                     # Prototipos Figma y diagramas
├── docs/
│   ├── contrato-de-proyecto.md
│   ├── patrones-tp1.md         # Descripción técnica de los patrones
│   └── AI_LOG.md               # Registro de uso de IA
└── README.md
```

---

## Equipo — UCP Inc.

| Nombre | Rol | GitHub |
|---|---|---|
| Gonzalez Lautaro Sebastian | Scrum Master | [@Lautaro-gonz](https://github.com/Lautaro-gonz) |
| Alonso Angelina | Dev Lead | [@angelinaalonsoucp](https://github.com/angelinaalonsoucp) |
| Piedrafita José Augusto | QA Lead | [@Gu7y](https://github.com/Gu7y) |
| Bruno | UX Lead | [@estudiandob-dev](https://github.com/estudiandob-dev) |

---

## Estado del proyecto

| Hito | Estado |
|---|---|
| Sprint 0 — Planificación y configuración | Completo |
| TP1 — Dominio, patrones y Django | Completo |
| TP2 — Pruebas, CI y ampliación | Próximamente |

---

## Documentación adicional

- [`docs/patrones-tp1.md`](docs/patrones-tp1.md) — Descripción técnica de los patrones State y Observer con ejemplos de código
- [`docs/contrato-de-proyecto.md`](docs/contrato-de-proyecto.md) — Metodología, roles y acuerdos del equipo
- [`docs/AI_LOG.md`](docs/AI_LOG.md) — Registro semanal de uso de herramientas de IA

---

> *Ingeniería de Software II · Universidad de la Cuenca del Plata · 2026*
