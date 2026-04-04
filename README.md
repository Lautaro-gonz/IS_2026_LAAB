

Proyecto — Sistema de gestión de turnos médicos

Sistema web orientado a digitalizar la asignación de turnos en una clínica médica, reemplazando el uso de llamadas telefónicas y planillas de Excel por una solución centralizada, eficiente y accesible.

---

¿Por qué elegimos este proyecto?

Elegimos este problema porque representa una situación real muy común en centros de salud, donde la gestión manual de turnos genera ineficiencias, errores y pérdida de tiempo tanto para el personal como para los pacientes.

La digitalización del proceso permite:
- Reducir errores en la asignación de turnos.
- Optimizar el tiempo de la recepcionista.
- Mejorar la experiencia del paciente.
- Tener un mejor control y seguimiento de la agenda médica.

Además, es un sistema escalable que puede evolucionar hacia soluciones más complejas en el ámbito de la salud.

---

👥 Integrantes

| Nombre                          | Rol           | GitHub |
|---------------------------------|--------------|--------|
| Gonzalez Lautaro Sebastian      | Scrum Master | @Lautaro-gonz |
| Alonso Angelina                 | Dev Lead     | @angelinaalonsoucp
| Piedrafita José Augusto         | QA Lead      | @Gu7y |
| Bruno                           | UX Lead      | @estudiandob-dev|

---

Descripción del sistema

El sistema permite gestionar turnos médicos de manera digital, facilitando la interacción entre recepcionistas y pacientes.

Usuarios principales:
- Recepcionista
- Paciente

Funcionalidades principales:

- Solicitar turnos seleccionando:
  - Médico
  - Especialidad
  - Fecha disponible

- Cancelar o reprogramar turnos existentes

- Visualizar la agenda diaria de cada médico

- Notificar al paciente cuando su turno esté próximo *(simulado)*

- Gestionar el estado del turno:
  - Pendiente
  - Confirmado
  - Cancelado
  - Atendido
    
Patrones de diseño

Factory Method — Observer — State — Repository 
 ¿Por qué elegimos estos patrones?

Observer
Se usa porque cuando un turno cambia de estado, múltiples partes del sistema necesitan enterarse: el paciente por email, por SMS, y el sistema por consola. Si no usáramos Observer, el turno tendría que saber cómo enviar emails, SMS y logs al mismo tiempo, mezclando responsabilidades. Con Observer el turno simplemente notifica y cada observador sabe qué hacer con esa notificación.

State
Se usa porque un turno tiene comportamientos completamente distintos según en qué estado esté. Por ejemplo, no tiene sentido cancelar un turno que ya está en atención, ni confirmar uno que ya fue completado. Sin State tendrías un montón de if turno.estado == "pendiente" repartidos por todo el código. Con State cada estado encapsula su propia lógica y lanza un error si se intenta una transición inválida. El código queda mucho más limpio y fácil de extender.

Factory Method
Se usa porque crear un turno no es tan simple como llamar a Turno(...). Hay pasos adicionales: validar la cobertura, calcular el costo, suscribir los observadores según si el paciente tiene email o teléfono. Si esa lógica queda dispersa en el menú principal, es difícil de mantener y de reutilizar. La Factory centraliza toda esa construcción en un solo lugar, garantizando que cada turno se crea siempre de la misma forma correcta.

Repository
Se usa porque el sistema necesita buscar, filtrar y listar turnos de distintas formas: por ID, por DNI del paciente, por médico y fecha. Sin Repository esas consultas están mezcladas con la lógica del menú y acceden directamente a la lista interna. Con Repository toda la lógica de acceso a los datos queda en un solo lugar.


Caso de uso — Crear Turno y Verificar Turno

La Recepcionista selecciona un médico, especialidad y fecha. El sistema consulta la agenda del médico y devuelve los horarios disponibles. La Recepcionista elige un horario y el sistema valida que esté libre. Si todo es correcto, el sistema crea el turno con estado PENDIENTE y genera una notificación simulada al paciente confirmando la creación.
Para verificar, la Recepcionista o el Paciente consultan los turnos existentes. El sistema devuelve el listado con los datos del turno — fecha, médico, estado — permitiendo confirmar que el turno fue creado correctamente.




---

Enlaces

 Tablero Kanban: https://github.com/users/estudiandob-dev/projects/1
 
Matriz de riesgo: https://docs.google.com/document/d/1dPqcOUwNv94cnZP1wG7At5TvyJGaC3kpGKOjuZYRfXo/edit?usp=sharing


