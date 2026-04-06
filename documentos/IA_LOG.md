# IA_LOG — Registro de uso de Inteligencia Artificial

**Proyecto:** Sistema de Gestión de Turnos — Clínica Médica  
**Entrega:** TP1  
**Herramienta principal:** Claude (Anthropic)  
**Herramienta de diagramas:** PlantUML  

---

## Resumen ejecutivo

| Área | Participación IA | Participación equipo |
|---|---|---|
| Código fuente | 100% generado por IA | Especificación, revisión y validación |
| Documentación de patrones | Expansión y corrección de sintaxis | Estructura, decisiones y redacción base |
| Diagrama de clases | Generación del código PlantUML | Diseño de entidades y relaciones |
| Decisiones de arquitectura | Sin participación | 100% del equipo |
| Elección de patrones de diseño | Sin participación | 100% del equipo |
| Adaptación al contexto clínico | Sin participación | 100% del equipo |

---

## Desglose por área

### Código fuente — IA: 100%

El código del proyecto fue generado íntegramente mediante Claude. El equipo se encargó de:

- Definir **qué** debía hacer cada clase y cada método antes de pedírselo a la IA
- Especificar las reglas de negocio concretas (qué estados son válidos, qué transiciones están permitidas, qué datos necesita un turno)
- Revisar el código generado para verificar que respetara las decisiones de diseño tomadas previamente
- Validar que la integración entre módulos (`logica.py`, `views.py`, `accounts/`) fuera coherente con la arquitectura planteada

El equipo actuó como **arquitecto y revisor**: la IA ejecutó la escritura del código bajo especificaciones precisas dadas por el grupo.

**Archivos generados con asistencia IA:**

```
turnos/logica.py        — clases de dominio, patrones Observer, State, Singleton, Factory
turnos/views.py         — vistas Django y lógica de control
accounts/views.py       — autenticación, panel admin, gestión de usuarios
accounts/usuarios.py    — modelo de usuario y repositorio en memoria
templates/              — todas las plantillas HTML
```

---

### Documentación de patrones — IA: parcial

La documentación del archivo `PATRONES_DISENO.md` fue un trabajo conjunto:

**Aporte del equipo:**
- Redacción inicial de cada sección con las ideas propias del grupo
- Definición de qué justificar y por qué se eligió cada patrón sobre las alternativas
- Estructura del documento y orden de los contenidos

**Aporte de la IA:**
- Expansión del texto base escrito por el equipo, ampliando explicaciones sin cambiar el contenido
- Corrección de sintaxis y redacción en párrafos que el equipo ya había elaborado
- Formateo en Markdown para GitHub (tablas, bloques de código, encabezados)

> La IA no tomó ninguna decisión de contenido en la documentación. Todas las justificaciones, comparaciones entre patrones y ejemplos de código negativo fueron definidos por el equipo.

---

### Diagrama de clases — PlantUML + IA: parcial

El diagrama de clases fue construido en dos etapas:

**Aporte del equipo:**
- Identificación de todas las entidades del sistema (Turno, Paciente, Medico, Agenda, Especialidad, Notificacion, Recepcionista, Administrador, Reporte, Permiso)
- Definición de atributos principales de cada clase
- Diseño de las relaciones entre clases y sus multiplicidades (1:N, N:M, composición, asociación)
- Decisiones de diseño como la separación entre `Agenda` y `Turno` y la relación de composición entre ambas

**Aporte de la IA:**
- Traducción del diseño elaborado por el equipo al código PlantUML
- Aplicación del `skinparam` para estilos visuales
- Corrección de sintaxis PlantUML en la definición de relaciones y multiplicidades

La herramienta utilizada para renderizar el diagrama fue **PlantUML**, con el código generado a partir del diseño conceptual previo del equipo.

---

## Estadística de uso

```
Código fuente
██████████████████████████████  100% IA

Documentación
████████████████░░░░░░░░░░░░░░   55% IA — 45% equipo

Diagrama de clases (PlantUML)
██████████░░░░░░░░░░░░░░░░░░░░   35% IA — 65% equipo

Decisiones de arquitectura
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    0% IA — 100% equipo

Elección de patrones
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░    0% IA — 100% equipo
```

**Estimación global del proyecto**

```
Participación IA      ████████████░░░░░░░░░░░░░░░░░░   ~40%
Participación equipo  ██████████████████░░░░░░░░░░░░   ~60%
```

---

## Uso honesto y transparente

El equipo reconoce que el código fue producido en su totalidad por la herramienta de IA, bajo una dinámica donde el grupo especificaba los requerimientos, revisaba los resultados y validaba que las decisiones de diseño se respetaran correctamente.

Lo que la IA **no hizo en ningún momento:**

- Elegir qué patrones de diseño aplicar ni por qué
- Decidir la arquitectura del sistema ni la separación de módulos
- Definir las entidades del dominio ni sus relaciones
- Adaptar la lógica al contexto específico de una clínica médica
- Tomar decisiones sobre qué casos de uso priorizar en esta entrega

Lo que el equipo considera **aporte propio no delegable:**

- El análisis del problema (digitalizar la gestión de turnos de una clínica)
- La identificación de los actores y sus responsabilidades (Recepcionista, Médico, Paciente, Administrador)
- El diseño del ciclo de vida del turno con sus 5 estados y transiciones válidas
- La decisión de combinar State con Observer para que cada cambio de estado dispare notificaciones automáticamente
- La justificación de por qué Singleton para `ValidadorCobertura` y no una función estática o variable global

---

## Reflexión del equipo

Utilizar IA como herramienta de escritura de código cambia el rol del programador: en lugar de escribir línea por línea, el trabajo se concentra en diseñar correctamente antes de generar, y en revisar críticamente después. Las decisiones de fondo — qué construir, cómo estructurarlo, qué patrones aplicar y por qué — siguieron siendo responsabilidad exclusiva del equipo.

La diferencia entre usar IA bien y usarla mal está en si uno sabe evaluar lo que produce. En este TP, el equipo validó cada fragmento generado contra las decisiones de diseño previas, rechazó o ajustó lo que no se adaptaba al contexto, y mantuvo coherencia entre el diagrama de clases, los patrones documentados y el código final.
