# Sistema de Gestión de Turnos — Clínica Privada

> **Ingeniería de Software II · UCP · 2026**  
> Trabajo Práctico 1 · Python + Django · UCP Inc.

---

## Sobre este repositorio

Este repositorio contiene el desarrollo completo del **Sistema de Gestión de Turnos** para una clínica privada, construido en el marco de la materia Ingeniería de Software II de la Universidad de la Cuenca del Plata.

El proyecto está organizado en carpetas temáticas. Esta guía explica qué hay en cada una y qué va a encontrar quien navegue el repositorio.

---

## Estructura del repositorio

```
/
├── diseño/
├── documentos/
│   ├── AI_LOG.md
│   ├── PATRONES_DISENO.md
│   ├── contrato_proyecto.md
│   ├── matriz de riesgo.png
│   └── plan_contingencia.md
├── pruebas/
├── src/
└── README.md
```

---

## Guía de navegación

### `diseño/`

Carpeta destinada a los prototipos de interfaz de usuario y recursos visuales del proyecto. Aquí se van a encontrar los mockups de las pantallas del sistema desarrollados en Figma, incluyendo las vistas de la recepcionista, el médico y el paciente. También se incluirán las evaluaciones de usabilidad aplicadas según normas ISO. **Actualmente en construcción** — los prototipos se entregan en las semanas 6 y 7.

---

### `documentos/`

Carpeta principal de documentación académica y técnica del proyecto. Contiene todos los archivos de texto y recursos que respaldan las decisiones tomadas durante el desarrollo.

- **`contrato_proyecto.md`** — Documento inicial del proyecto. Define el escenario elegido (sistema de turnos para clínica privada), la metodología de desarrollo adoptada, los roles asignados a cada integrante y los acuerdos de trabajo del equipo: horarios, canales de comunicación, frecuencia de commits y criterios para mover tarjetas en el tablero Kanban.

- **`PATRONES_DISENO.md`** — Descripción técnica detallada de los dos patrones de diseño implementados en el sistema: **State** (gestión de estados del turno sin condicionales) y **Observer** (notificaciones automáticas al paciente ante cada cambio de estado). Incluye diagramas, ejemplos de código y justificación de cada decisión de diseño.

- **`AI_LOG.md`** — Registro semanal del uso de herramientas de inteligencia artificial durante el desarrollo del proyecto. Documenta qué herramientas se usaron, con qué propósito, qué se obtuvo y qué ajustes realizó el equipo sobre el resultado generado.

- **`matriz de riesgo.png`** — Imagen con la matriz de riesgos del proyecto. Identifica los riesgos potenciales del desarrollo, su probabilidad de ocurrencia, su impacto y las estrategias de mitigación definidas por el equipo.

- **`plan_contingencia.md`** — Plan de acción ante los riesgos identificados en la matriz. Describe qué hace el equipo si alguno de los riesgos se materializa durante el desarrollo.

---

### `pruebas/`

Carpeta destinada a las pruebas unitarias del sistema. Aquí se van a encontrar los casos de prueba escritos con la metodología TDD (Test Driven Development) y la configuración de automatización de pruebas con integración continua. **Actualmente en construcción** — las pruebas se desarrollan en las semanas 8 a 11.

---

### `src/`

Carpeta destinada al código fuente del sistema. Aquí va a estar el archivo principal `sistemadeturno.py` con toda la lógica de dominio en Python puro, junto con el proyecto Django que agrega la interfaz web con autenticación por roles. **Actualmente en construcción** — el código se integra al repositorio durante el TP1.

---

### `README.md`

Este archivo. Funciona como punto de entrada al repositorio y guía de navegación para cualquier persona que acceda al proyecto.

---

## Equipo — UCP Inc.

| Nombre | Rol | GitHub |
|---|---|---|
| Gonzalez Lautaro Sebastian | Scrum Master | [@Lautaro-gonz](https://github.com/Lautaro-gonz) |
| Alonso Angelina | Dev Lead | [@angelinaalonsoucp](https://github.com/angelinaalonsoucp) |
| Piedrafita José Augusto | QA Lead | [@Gu7y](https://github.com/Gu7y) |
| López Bruno Daniel | UX Lead | [@estudiandob-dev](https://github.com/estudiandob-dev) |

---

## Estado del proyecto

| Hito | Estado |
|---|---|
| Sprint 0 — Planificación y configuración | Completo |
| TP1 — Dominio, patrones y Django | En curso |
| TP2 — Pruebas, CI y ampliación | Pendiente |

---

##Links


Kanban:https://github.com/users/estudiandob-dev/projects/1/views/1
> *Ingeniería de Software II · Universidad de la Cuenca del Plata · 2026*
