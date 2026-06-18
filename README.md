# LAAB
## Proyecto TurnosMed — Sistema de gestión de turnos para clínica médica

Sistema web para que recepcionistas, médicos y pacientes de una clínica puedan gestionar turnos médicos. Reemplaza el proceso manual por teléfono y planilla de Excel, evita conflictos de agenda y centraliza la información en un solo lugar.

---

## Integrantes

| Nombre | Rol | GitHub |
|---|---|---|
| Lautaro González | Scrum Master | [@Lautaro-gonz](https://github.com/Lautaro-gonz) |
| Angelina Alonso | Dev Lead | [@alonsoangelina070-max](https://github.com/alonsoangelina070-max) |
| Augusto | QA Lead | [@Chico7y](https://github.com/Chico7y) |
| Bruno | UX Lead | [@estudiarb-dev](https://github.com/estudiarb-dev) |

---

## Descripción del sistema

Sistema de turnos médicos que permite a la recepcionista crear, confirmar, cancelar y reprogramar turnos seleccionando médico, especialidad y horario disponible. Los médicos pueden ver su agenda diaria y registrar el estado de cada atención. Los pacientes pueden consultar sus turnos ingresando su DNI. El sistema valida la obra social del paciente, calcula el costo de la consulta automáticamente y notifica al paciente en cada cambio de estado del turno.

**Patrones de diseño implementados:** Observer · State · Singleton · Factory Method

**Caso de uso principal:** La recepcionista selecciona un médico, especialidad, fecha y horario. El sistema verifica que el paciente tenga cobertura válida, crea el turno en estado PENDIENTE y notifica automáticamente al paciente.

---

1. Verificación vs Validación: Con sus palabras, ¿cuál es la diferencia clave? Pongan un ejemplo de cada una en su proyecto.

2. Planificación de V&V: Si tuvieran que planificar la verificación y validación para el próximo sprint (1 semana), ¿qué dos actividades concretas incluirían?

3. Inspecciones de software: ¿En qué se diferencia una inspección de código de una prueba automática? ¿Cuándo conviene más una que la otra?

4. Análisis estático automatizado: Nombre una herramienta que conozcan (SonarQube, ESLint, Pylint, etc.) y digan qué tipo de error podría encontrar en su código sin ejecutarlo.

5. Métodos formales de verificación: ¿Para qué tipo de sistemas son imprescindibles? ¿Por qué no se usan siempre?

6. Reuniones de validación en Scrum/XP: ¿Qué rol cumple el Product Owner en una Sprint Review? ¿Cómo se relaciona con las pruebas automatizadas?
RTA:
1. La verificación busca confirmar que el software fue desarrollado según los requisitos definidos; la validación intenta comprobar si el sistema realmente satisface las necesidades del usuario. En nuestro proyecto, una verificación sería revisar que el módulo de turnos siga las reglas planteadas; una validación sería mostrarlo al cliente y recibir su aprobación.

2. Para el próximo sprint incluiríamos dos actividades concretas: ejecutar pruebas unitarias sobre las nuevas funciones y realizar una revisión grupal del código antes de integrar cambios. Además, haríamos una demostración breve con el Product Owner para validar el funcionamiento esperado.

3. La inspección de código consiste en analizar el código de manera manual; en cambio, una prueba automática ejecuta el sistema para detectar fallos durante su funcionamiento. La inspección conviene para hallar problemas de diseño o lógica; las pruebas automáticas resultan más útiles para verificar comportamientos repetitivos.

4. Pylint permite detectar errores sin ejecutar el programa; por ejemplo, variables no utilizadas, problemas de sintaxis o funciones mal estructuradas. Este tipo de análisis ayuda a mantener un código más claro y ordenado.

5. Los métodos formales son imprescindibles en sistemas críticos; por ejemplo, software médico, aeronáutico o bancario, donde un error podría causar consecuencias graves. No se aplican siempre porque requieren mucho tiempo, conocimientos especializados y un proceso bastante complejo.

6. En Scrum o XP, el Product Owner participa en la Sprint Review para validar que el incremento desarrollado cumpla con lo esperado por el cliente. Las pruebas automatizadas se relacionan con este proceso porque permiten llegar a la revisión con funciones ya comprobadas y más estables.

---

# Mini Plan de Verificación y Validación (V&V)
 
> Borrador de trabajo — Sistema de Gestión de Turnos · Clínica LAAB · 2026
 
---
 
## Sección 1 — Verificación vs. Validación
 
**Verificación (algo que ya hacemos):**
Las pruebas unitarias implementadas en `tests/unit/test_logica.py` verifican que las clases del dominio se comportan exactamente como fueron diseñadas. Específicamente, el caso que verifica que `TurnoFactory` lanza `ValueError` cuando se intenta crear un turno con fecha pasada es una verificación: estamos comprobando que el código hace lo que dice que hace según la especificación técnica, sin necesidad de levantar el servidor ni conectar la base de datos.
 
**Validación (algo que planeamos hacer con el Product Owner):**
Planeamos hacer una sesión corta con el Product Owner donde la secretaria simulada recorra el flujo completo de solicitud de turno usando el sistema real, no el prototipo. La pregunta que queremos responder es si el sistema resuelve el problema original: ¿puede la clínica dejar de usar el Excel y el teléfono para gestionar turnos? Eso es validación — no si el código es correcto, sino si el sistema sirve para lo que fue pedido.
 
---
 
## Sección 2 — Planificación de V&V para los próximos 2 sprints
 
| Sprint | Actividad de V&V | Técnica | Responsable | Herramienta |
|--------|-----------------|---------|-------------|-------------|
| Actual | Inspección de `sistemadeturno.py`: verificar que los métodos de transición del patrón State no tienen lógica condicional mezclada | Inspección de código / revisión manual | QA Lead | Pylint + checklist manual |
| Próximo | Sesión de validación con el Product Owner: secretaria simulada completa el flujo de solicitud, confirmación y cancelación en el sistema real | Prueba de aceptación / demo con usuario | Scrum Master + UX Lead | Sistema corriendo en local + guión de tareas |
 
---
 
## Sección 3 — Inspección y análisis estático
 
**a) ¿Qué archivo inspeccionaríamos primero y por qué?**
 
`sistemadeturno.py`. Es el núcleo de toda la lógica del sistema: ahí están las clases del dominio, los patrones State y Observer, y todas las validaciones de negocio. Es también el archivo que más cambió a lo largo del TP1, lo que lo hace más propenso a tener código duplicado o decisiones contradictorias. Un segundo candidato sería `tests/unit/test_logica.py` — un test mal escrito da falsa seguridad, y eso es peor que no tener test.
 
**b) Herramienta elegida y primera regla a aplicar:**
 
Elegiríamos **Pylint**. La primera regla que aplicaríamos es la detección de complejidad ciclomática alta (`C901`). Esta regla marca funciones con demasiados caminos de ejecución posibles. Si el patrón State está bien implementado, ningún método de la clase `Turno` debería tener complejidad alta — si Pylint reporta lo contrario, significa que hay lógica condicional que debería estar en las clases de estado y no llegó a migrarse.
 
---
 
## Sección 4 — Método formal conceptual
 
**a) Invariante para la clase `Turno`:**
 
En cualquier momento de la vida de un objeto `Turno`, su atributo `_estado` es siempre una instancia de alguna subclase concreta de `EstadoTurno` (`EstadoPendiente`, `EstadoConfirmado`, `EstadoEnAtencion`, `EstadoCompletado` o `EstadoCancelado`). Nunca puede ser `None`, nunca puede ser un string, y nunca puede ser la clase abstracta `EstadoTurno` directamente.
 
Dicho de otra manera: un turno siempre tiene un estado definido. No existe un turno "sin estado".
 
**b) Cómo lo probaríamos con una prueba unitaria:**
 
Verificaríamos el invariante en tres momentos distintos del ciclo de vida del turno:
 
```python
def test_invariante_estado_turno(self):
    turno = TurnoFactory.crear(paciente, medico, fecha_valida, "09:00")
 
    # Al crear — debe ser EstadoPendiente
    self.assertIsInstance(turno._estado, EstadoPendiente)
    self.assertIsInstance(turno._estado, EstadoTurno)
    self.assertIsNotNone(turno._estado)
 
    # Después de confirmar — debe ser EstadoConfirmado
    turno.confirmar()
    self.assertIsInstance(turno._estado, EstadoConfirmado)
    self.assertIsInstance(turno._estado, EstadoTurno)
 
    # Después de completar — debe ser EstadoCompletado
    turno.atender()
    turno.completar()
    self.assertIsInstance(turno._estado, EstadoCompletado)
    self.assertIsInstance(turno._estado, EstadoTurno)
```
 
Si alguna transición deja el estado en un valor inválido, la prueba lo detecta inmediatamente.
 
---
 
## Sección 5 — Simulación de reunión de validación con el Product Owner
 
Estas son las dos preguntas que le haríamos al Product Owner en la próxima Sprint Review. No son preguntas técnicas — son preguntas sobre si el sistema resuelve el problema real de la clínica.
 
**Pregunta 1:**
> Si la secretaria tuviera que usar este sistema mañana para gestionar la agenda del día, ¿hay alguna situación habitual de la clínica que el sistema todavía no pueda manejar?
 
*Por qué la preguntamos:* queremos saber si hay casos de uso reales que no consideramos. Puede haber turnos de urgencia, médicos que atienden en varios consultorios, o pacientes con dos turnos el mismo día. Si el sistema no los contempla, es mejor saberlo ahora que en el integrador final.
 
**Pregunta 2:**
> Mirando el panel de secretaria, ¿la información que aparece en la agenda es suficiente para trabajar sin tener que buscar datos en otro lado, como el Excel que se usaba antes?
 
*Por qué la preguntamos:* el éxito del sistema no es que funcione técnicamente, sino que la clínica pueda abandonar el proceso manual. Si la secretaria todavía necesita el Excel para completar información que el sistema no muestra, el reemplazo no es real.
 
---
## Mejora integradora

### Problema que resolvimos
El sistema contaba con el patrón Observer implementado en logica.py 
(EmailObservador y SMSObservador), pero ambas clases solo ejecutaban 
un print() en la consola del servidor. Las notificaciones se disparaban 
correctamente pero eran invisibles para el usuario y no quedaba ningún 
historial. Además, el precio de las consultas estaba hardcodeado en 
$10.000 sin posibilidad de actualización.

### Qué agregamos

*1. Sistema de notificaciones con registro en base de datos*
- Nuevo modelo NotificacionDB en turnos/models.py
- Clase EmailObservadorDB en views.py que guarda cada notificación 
  en la BD en lugar de imprimir en consola
- Historial de notificaciones visible en el panel del admin y del paciente
- Badge contador en el sidebar que muestra notificaciones no leídas

*2. Ajuste de precios por inflación INDEC*
- Nuevo modelo InflacionDB con historial de porcentajes registrados
- Integración con la API pública oficial de datos.gob.ar para obtener 
  el IPC mensual real del INDEC Argentina
- Botón "Aplicar ajuste sobre turnos futuros" que actualiza el costo 
  de todos los turnos PENDIENTE y CONFIRMADO

*3. Estado AUSENTE*
- Nuevo estado terminal en el ciclo de vida del turno
- Transición desde CONFIRMADO cuando el paciente no se presenta
- Permite calcular tasa de ausentismo en el análisis estadístico

*4. Motivo de consulta y notas del médico*
- Campo motivo_consulta al crear el turno
- Campo notas_medico al completar la atención
- Ambos campos se incluyen en la exportación CSV/TXT

*5. Validación de turno vencido*
- El sistema rechaza confirmar turnos cuya hora ya pasó
- Notifica automáticamente al paciente para que reagende

*6. Exportación de datos para Estadística*
- Script exportar_estadistica.py que genera archivos TXT y PDF
- 15 columnas incluyendo columnas derivadas: dias_anticipacion, 
  franja_horaria, porcentaje_cobertura, dia_semana, mes

### Rama
feature/mejora-integradora

### Cómo ejecutar
bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver


### Nota sobre el mock
El envío de emails se simula guardando el registro en NotificacionDB 
y escribiendo en emails_log.txt. En producción se reemplazaría por 
django.core.mail.send_mail() sin modificar ningún otro componente.

## Enlaces

- 
https://github.com/users/estudiandob-dev/projects/1/views/1
