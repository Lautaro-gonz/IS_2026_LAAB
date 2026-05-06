# 🖥️ TP2 — Diseño de Interfaz Centrado en el Usuario

**Proyecto:** Sistema de Gestión de Turnos — Clínica Médica  
**Entrega:** TP2 — Eje 3: Diseño UI / Interacción Hombre–Máquina  
**Equipo:** LAAB

---

## Índice

- [A1 — Prototipo Figma](#a1--prototipo-figma)
- [A2 — Análisis de usuario, tarea y contexto](#a2--análisis-de-usuario-tarea-y-contexto)
- [A3 — Auditoría de usabilidad ISO 9241-11](#a3--auditoría-de-usabilidad-iso-9241-11)
- [Alineación con ISO 13407](#alineación-con-iso-13407)

---

## A1 — Prototipo Figma

> 🔗 **Link al prototipo:** _[insertar link público de Figma aquí]_

**Flujo cubierto:** Calendario → Solicitud de turno → Comprobante

| Pantalla | Descripción |
|---|---|
| Panel principal | Vista de agenda del médico con turnos del día |
| Formulario de turno | Selección de médico, especialidad, fecha y datos del paciente |
| Comprobante | Confirmación del turno creado con estado PENDIENTE |

---

## A2 — Análisis de usuario, tarea y contexto

### Usuarios objetivo

El sistema está orientado a dos perfiles de usuarios principales con necesidades y contextos de uso distintos. Por un lado, la **recepcionista de la clínica** es el usuario más frecuente del sistema: gestiona la agenda diaria, crea turnos en nombre de los pacientes, confirma o cancela citas y consulta el estado de cada turno a lo largo del día. Se trata de una persona con conocimiento básico-medio de herramientas digitales, que opera el sistema de forma continua durante su jornada laboral y que necesita realizar cada acción de forma rápida, sin pasos innecesarios, ya que habitualmente atiende al paciente en persona o por teléfono de forma simultánea.

Por otro lado, el **médico** accede al sistema para consultar su propia agenda del día, ver los datos de los pacientes que tiene asignados y registrar el estado de cada atención. Su interacción con el sistema es más acotada en cantidad de acciones pero igualmente crítica: necesita información clara y disponible de forma inmediata, sin tener que navegar por múltiples pantallas para encontrar lo que busca.

### Contexto de uso y dispositivo

Ambos perfiles utilizan el sistema desde una computadora de escritorio o notebook dentro del ámbito de la clínica, con conexión a internet estable. La recepcionista opera desde un mostrador de atención, donde el sistema es una herramienta de trabajo permanente y el tiempo de respuesta de cada acción impacta directamente en la atención al paciente presencial. El médico accede desde su consultorio, generalmente entre consulta y consulta, por lo que el sistema debe presentar la información de forma sintética y sin requerir interacciones complejas.

### Restricciones y condiciones del entorno

Una restricción importante del contexto es que la recepcionista puede estar atendiendo a un paciente físicamente mientras opera el sistema, lo que limita su atención visual y cognitiva disponible. Esto impone que la interfaz minimice la cantidad de pasos para completar una tarea, evite mensajes de error ambiguos y confirme cada acción de forma clara y visible. El sistema no está diseñado para uso móvil en esta etapa, por lo que no se contempla adaptación responsive como requisito del TP2.

---

## A3 — Auditoría de usabilidad ISO 9241-11

La norma **ISO 9241-11** define la usabilidad como la medida en que un sistema puede ser usado por usuarios específicos para alcanzar objetivos específicos con **eficacia**, **eficiencia** y **satisfacción** en un contexto de uso determinado. Para esta auditoría se seleccionaron los criterios de **eficacia** y **eficiencia**.

---

### Criterio 1 — Eficacia

> *"Exactitud y completitud con la que los usuarios alcanzan los objetivos especificados."*

#### Métrica definida

**Tasa de completitud de la tarea principal:** porcentaje de usuarios que logran crear un turno completo (desde el formulario hasta ver el comprobante) sin cometer errores que requieran reiniciar el flujo.

```
Métrica = (usuarios que completan el flujo sin error / total de usuarios observados) × 100
Umbral aceptable: ≥ 85%
```

#### Simulación en el prototipo actual

En el prototipo, el formulario de creación de turno solicita: nombre del paciente, DNI, médico, especialidad, fecha y hora. Al simular el recorrido con un usuario que completa el formulario por primera vez, se identificó que **si el campo de obra social queda vacío, el sistema no informa claramente si es obligatorio u opcional**. Un usuario que no conoce la lógica del sistema podría enviarlo sin ese dato o detenerse sin saber cómo continuar, reduciendo la tasa de completitud.

#### Problema identificado

El formulario no distingue visualmente entre campos obligatorios y opcionales. No hay indicador (`*`) ni mensaje preventivo que oriente al usuario antes de intentar enviar.

#### Mejora propuesta

Marcar con asterisco rojo (`*`) todos los campos obligatorios del formulario y agregar una leyenda al pie que diga *"Los campos marcados con * son obligatorios"*. Adicionalmente, mostrar un mensaje de validación inline (debajo del campo, no en un alert global) cuando el usuario intente enviar con campos obligatorios vacíos, indicando exactamente cuál campo falta completar.

---

### Criterio 2 — Eficiencia

> *"Recursos utilizados en relación con la exactitud y completitud con que los usuarios alcanzan los objetivos."*

#### Métrica definida

**Tiempo promedio para completar la tarea principal:** tiempo que tarda un usuario en crear un turno desde que accede al formulario hasta que visualiza el comprobante de confirmación.

```
Métrica = tiempo promedio en segundos para completar el flujo de creación de turno
Umbral aceptable: ≤ 60 segundos para un usuario con experiencia básica
```

#### Simulación en el prototipo actual

Al recorrer el flujo en el prototipo, se detectó que para crear un turno el usuario debe: (1) ir al panel principal, (2) hacer clic en "Nuevo turno", (3) completar el formulario con 6 campos, (4) seleccionar médico de una lista desplegable larga sin filtro, (5) enviar. La lista de médicos no tiene filtro por especialidad en el mismo paso, lo que obliga al usuario a recordar qué médico corresponde a cada especialidad antes de seleccionar. En un escenario real con 20 o más médicos, esto aumenta el tiempo de búsqueda y el riesgo de selección incorrecta.

#### Problema identificado

La selección de médico no está filtrada por especialidad. El usuario ve todos los médicos disponibles en una sola lista, sin agrupación ni búsqueda, lo que aumenta la carga cognitiva y el tiempo necesario para completar el formulario correctamente.

#### Mejora propuesta

Implementar un selector encadenado: primero el usuario elige la **especialidad** y luego el sistema filtra automáticamente la lista de **médicos** mostrando solo los que corresponden a esa especialidad. Esto reduce la cantidad de opciones visibles en el segundo selector, disminuye el tiempo de selección y elimina la posibilidad de asignar un médico a una especialidad incorrecta.

---

## Alineación con ISO 13407

La norma **ISO 13407** define el **Diseño Centrado en el Usuario (DCU)** como un proceso iterativo compuesto por cuatro actividades principales: comprender el contexto de uso, especificar los requisitos del usuario, producir soluciones de diseño y evaluar esas soluciones contra los requisitos.

El proceso que siguió el equipo en este TP2 se alinea con ese ciclo de la siguiente manera:

**1. Comprender el contexto de uso** — realizado en la sección A2, donde se identificaron los perfiles de usuario (recepcionista y médico), sus tareas principales, el entorno físico de trabajo y las restricciones cognitivas del contexto (atención simultánea al paciente).

**2. Especificar requisitos del usuario** — el caso de uso principal definido desde el TP1 (crear un turno seleccionando médico, especialidad, fecha y horario) funcionó como requisito central que guió el diseño del prototipo y la selección de pantallas.

**3. Producir soluciones de diseño** — realizado en A1, donde se diseñaron las tres pantallas navegables en Figma que cubren el flujo completo del caso de uso principal.

**4. Evaluar contra requisitos** — realizado en esta sección A3, donde se aplicaron dos criterios de la ISO 9241-11 (eficacia y eficiencia) para identificar problemas concretos en el prototipo y proponer mejoras medibles.

El proceso no termina aquí: las mejoras propuestas (campos obligatorios marcados y selector encadenado de especialidad/médico) deberán incorporarse al prototipo en la siguiente iteración, reiniciando el ciclo con una nueva evaluación. Esto es precisamente lo que la ISO 13407 define como diseño centrado en el usuario: un ciclo continuo de diseño, evaluación y mejora orientado siempre a las necesidades reales del usuario.
