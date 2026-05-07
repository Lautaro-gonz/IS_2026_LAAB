# IA_LOG — Registro de uso de Inteligencia Artificial

**Proyecto:** Sistema de Gestión de Turnos — Clínica Médica  
**Herramienta principal:** Claude (Anthropic)  
**Herramienta de diagramas:** PlantUML

---

## Índice

- [TP1 — Registro original](#tp1--registro-original)
- [TP2 — Actualización](#tp2--actualización)
- [Estadística acumulada](#estadística-acumulada-tp1--tp2)
- [Reflexión del equipo](#reflexión-del-equipo)

---

## TP1 — Registro original

### Resumen ejecutivo

| Área | Participación IA | Participación equipo |
|---|---|---|
| Código fuente | 100% generado por IA | Especificación, revisión y validación |
| Documentación de patrones | Expansión y corrección de sintaxis | Estructura, decisiones y redacción base |
| Diagrama de clases | Generación del código PlantUML | Diseño de entidades y relaciones |
| Decisiones de arquitectura | Sin participación | 100% del equipo |
| Elección de patrones de diseño | Sin participación | 100% del equipo |
| Adaptación al contexto clínico | Sin participación | 100% del equipo |

### Desglose por área

**Código fuente — IA: 100%**

El código del proyecto fue generado íntegramente mediante Claude. El equipo se encargó de:

- Definir qué debía hacer cada clase y cada método antes de pedírselo a la IA
- Especificar las reglas de negocio concretas (qué estados son válidos, qué transiciones están permitidas, qué datos necesita un turno)
- Revisar el código generado para verificar que respetara las decisiones de diseño tomadas previamente
- Validar que la integración entre módulos (`logica.py`, `views.py`, `accounts/`) fuera coherente con la arquitectura planteada

El equipo actuó como **arquitecto y revisor**: la IA ejecutó la escritura del código bajo especificaciones precisas dadas por el grupo.

```
turnos/logica.py        — clases de dominio, patrones Observer, State, Singleton, Factory
turnos/views.py         — vistas Django y lógica de control
accounts/views.py       — autenticación, panel admin, gestión de usuarios
accounts/usuarios.py    — modelo de usuario y repositorio en memoria
templates/              — todas las plantillas HTML
```

**Documentación de patrones — IA: parcial**

La documentación del archivo `PATRONES_DISENO.md` fue un trabajo conjunto:

Aporte del equipo: redacción inicial de cada sección, definición de qué justificar y por qué se eligió cada patrón, estructura y orden del documento.

Aporte de la IA: expansión del texto base escrito por el equipo, corrección de sintaxis y redacción, formateo en Markdown para GitHub (tablas, bloques de código, encabezados).

> La IA no tomó ninguna decisión de contenido. Todas las justificaciones, comparaciones entre patrones y ejemplos de código negativo fueron definidos por el equipo.

**Diagrama de clases — PlantUML + IA: parcial**

Aporte del equipo: identificación de entidades, definición de atributos, diseño de relaciones y multiplicidades, decisiones de composición entre clases.

Aporte de la IA: traducción del diseño al código PlantUML, aplicación de `skinparam`, corrección de sintaxis en relaciones y multiplicidades.

### Estadística TP1

```
Código fuente
██████████████████████████████  100% IA

Documentación de patrones
████████████████░░░░░░░░░░░░░░   55% IA — 45% equipo

Diagrama de clases (PlantUML)
██████████░░░░░░░░░░░░░░░░░░░░   35% IA — 65% equipo

Decisiones de arquitectura
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    0% IA — 100% equipo

Elección de patrones
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    0% IA — 100% equipo
```

```
Estimación global TP1
Participación IA      ████████████░░░░░░░░░░░░░░░░░░   ~40%
Participación equipo  ██████████████████░░░░░░░░░░░░   ~60%
```

---

## TP2 — Actualización

### Resumen ejecutivo

| Área | Participación IA | Participación equipo |
|---|---|---|
| Código de pruebas unitarias (`test_logica.py`) | 100% generado por IA | Especificación de casos, revisión y validación |
| Pipeline GitHub Actions (`test.yml`) | Generación del YAML | Configuración, verificación y push (Angelina) |
| `docs/tp2-pruebas-unitarias.md` | Expansión y formateo | Diseño de clases de equivalencia y valores límite (Guty) |
| `docs/tp2-ui-ux.md` | Expansión y corrección de sintaxis | Análisis de usuarios, criterios ISO, mejoras propuestas (Guty) |
| `docs/testing-strategy.md` | Generación asistida | Estructura, decisiones de estrategia y prioridades |
| Diseño conceptual de integración (B3) | Generación asistida | Identificación de dependencias y flujo (Guty) |
| Informe PDF final | Generación asistida | Contenido, revisión y validación del equipo |
| Selección de criterios ISO 9241-11 | Sin participación | 100% del equipo (Guty) |
| Diseño de clases de equivalencia y valores límite | Sin participación | 100% del equipo (Guty) |
| Auditoría de usabilidad | Sin participación | 100% del equipo (Guty) |
| Prototipo Figma (3 pantallas navegables) | Sin participación | 100% del equipo (Guty) |
| Delegación de tareas y tablero Kanban | Sin participación | 100% del equipo (Scrum Master) |

### Desglose por área

**Código de pruebas unitarias — IA: 100%**

Los 20 casos de prueba del archivo `tests/unit/test_logica.py` fueron generados íntegramente por Claude a partir de las especificaciones del equipo. El equipo se encargó de:

- Definir qué funciones testear (`TurnoFactory`, `ObraSocial`, `CalculoCosto`, `EstadoTurno`, `ValidadorCobertura`)
- Diseñar las clases de equivalencia y los valores límite **antes** de pedirle el código a la IA
- Revisar cada caso generado para verificar que los `assert` fueran correctos
- Validar que los resultados esperados correspondieran a las reglas de negocio reales del sistema

```
tests/unit/test_logica.py — 20 casos de prueba sobre 6 funciones del sistema
```

**Documentación `tp2-pruebas-unitarias.md` — IA: parcial**

Aporte del equipo (Guty): diseño de las clases de equivalencia y valores límite (B0), identificación de las dos dependencias externas para B3, flujo de integración en pseudocódigo.

Aporte de la IA: expansión del texto base, formateo Markdown, ejemplos de código de mock basados en las clases reales del proyecto (`TurnoRepositorio`, `ValidadorCobertura`, `EmailObservador`).

**Documentación `tp2-ui-ux.md` — IA: parcial**

Aporte del equipo (Guty): identificación de perfiles de usuario (recepcionista y médico), selección de los criterios ISO 9241-11 (eficacia y eficiencia), identificación de problemas concretos en el prototipo, propuesta de mejoras (campos obligatorios marcados y selector encadenado especialidad/médico).

Aporte de la IA: expansión de los párrafos del análisis de usuario (A2), formateo de las tablas de auditoría (A3), redacción del párrafo de alineación con ISO 13407.

**`docs/testing-strategy.md` — IA: parcial**

Aporte del equipo: decisión sobre qué niveles de prueba incluir, prioridad de cobertura futura, reglas del equipo para evitar regresiones, identificación del `ValidadorCobertura` con `threading.Lock()` como caso de estrés específico.

Aporte de la IA: estructura del documento completo, tabla de herramientas, flujo E2E en pseudocódigo basado en el sistema real, plan de estrés con Locust apuntando a los endpoints críticos.

**Pipeline GitHub Actions — IA: parcial**

Aporte del equipo (Angelina): configuración del repositorio, verificación de que el pipeline corra correctamente en GitHub Actions, push y validación del workflow, captura de pantalla como evidencia.

Aporte de la IA: generación del contenido del archivo `.github/workflows/test.yml` con los pasos de checkout, instalación de Python, instalación de pytest y ejecución de los tests.

**Informe PDF final — IA: asistida**

El informe PDF fue generado con código Python usando la librería `reportlab`, producido con asistencia de IA a partir de todo el contenido trabajado durante el TP2. El equipo revisó el contenido y validó que refleje fielmente lo trabajado en cada parte.

**Lo que la IA NO hizo en el TP2:**

- Diseñar las clases de equivalencia ni los valores límite — eso fue trabajo de Guty como QA Lead
- Seleccionar qué criterios de la ISO 9241-11 aplicar ni identificar los problemas del prototipo
- Producir el prototipo Figma ni tomar ninguna decisión de UX
- Identificar qué dependencias externas tiene el sistema ni cómo mockearlas conceptualmente
- Decidir la estrategia de regresión ni las prioridades de cobertura futura
- Organizar la delegación de tareas ni mantener el tablero Kanban al día

### Estadística TP2

```
Código de pruebas unitarias
██████████████████████████████  100% IA

Pipeline GitHub Actions
████████████████████░░░░░░░░░░   65% IA — 35% equipo

Documentación técnica (tp2-pruebas, tp2-ui-ux, testing-strategy)
████████████████░░░░░░░░░░░░░░   55% IA — 45% equipo

Informe PDF
████████████████░░░░░░░░░░░░░░   55% IA — 45% equipo

Diseño de clases de equivalencia y valores límite
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    0% IA — 100% equipo

Auditoría ISO 9241-11
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    0% IA — 100% equipo

Prototipo Figma
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    0% IA — 100% equipo

Delegación y Kanban
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    0% IA — 100% equipo
```

```
Estimación global TP2
Participación IA      ████████████░░░░░░░░░░░░░░░░░░   ~43%
Participación equipo  ██████████████████░░░░░░░░░░░░   ~57%
```

---

## Estadística acumulada (TP1 + TP2)

```
Código fuente + pruebas unitarias
██████████████████████████████  100% IA

Pipeline CI/CD
████████████████████░░░░░░░░░░   65% IA — 35% equipo

Documentación técnica (todos los .md)
████████████████░░░░░░░░░░░░░░   55% IA — 45% equipo

Informe PDF
████████████████░░░░░░░░░░░░░░   55% IA — 45% equipo

Diagrama de clases (PlantUML)
██████████░░░░░░░░░░░░░░░░░░░░   35% IA — 65% equipo

Diseño de clases de equivalencia
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    0% IA — 100% equipo

Auditoría ISO 9241-11 y UX
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    0% IA — 100% equipo

Prototipo Figma
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    0% IA — 100% equipo

Decisiones de arquitectura y patrones
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    0% IA — 100% equipo

Delegación, Kanban y coordinación
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    0% IA — 100% equipo
```

**Estimación global acumulada TP1 + TP2**

```
Participación IA      ████████████░░░░░░░░░░░░░░░░░░   ~42%
Participación equipo  ██████████████████░░░░░░░░░░░░   ~58%
```

---

## Reflexión del equipo

A lo largo del TP1 y el TP2, el uso de IA evolucionó junto con el proyecto. En el TP1 la IA fue principalmente una herramienta de escritura de código — el equipo diseñaba y la IA ejecutaba. En el TP2 el rol se complejizó: la IA también participó en la generación de documentación técnica especializada (testing strategy, pruebas de integración conceptual, informe PDF), siempre a partir de decisiones y especificaciones del equipo.

Lo que se mantuvo constante en ambas entregas es la separación entre **decisión** e **implementación**. Las decisiones — qué patrones usar, qué funciones testear, qué criterios ISO aplicar, qué dependencias mockear — fueron siempre del equipo. La IA implementó lo que el equipo decidió, y el equipo revisó que lo implementado fuera correcto.

Usar IA de esta manera no elimina el conocimiento técnico necesario — lo reenfoca. Para especificar bien lo que la IA debe producir, para revisar críticamente lo que produce y para detectar cuando algo no se adapta al contexto real del proyecto, se necesita entender el dominio profundamente. Esa comprensión es lo que el equipo aportó en cada etapa del proyecto.
