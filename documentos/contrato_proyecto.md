

---

# **Contrato de Proyecto**

**Responsable de redacción:** Scrum Master (González Lautaro Sebastián)

---

## **1. Escenario elegido y por qué lo elegimos**

Elegimos el desarrollo de un **Sistema de Gestión de Turnos Médicos** para una clínica que actualmente administra turnos mediante llamadas telefónicas y planillas de Excel. Este proceso manual genera problemas recurrentes como superposición de turnos, falta de visibilidad de la agenda, errores humanos y pérdida de tiempo tanto para pacientes como para recepcionistas. El escenario nos resultó adecuado porque representa un problema real y frecuente en centros de salud, pero a la vez es un dominio que conocemos y podemos modelar sin ambigüedades: médicos, especialidades, agendas y turnos con estados. Además, trabajar con turnos médicos permite aplicar patrones de diseño, principios de arquitectura, pruebas y prácticas ágiles de manera concreta a lo largo del cuatrimestre. Finalmente, es un sistema escalable que podría extenderse en el futuro con historia clínica digital, recordatorios automáticos, integración con obras sociales u otros módulos, lo cual lo convierte en un proyecto con recorrido académico y técnico.

---

## **2. Metodología de desarrollo elegida y justificación técnica**

Para gestionar el proyecto elegimos **Scrum** como metodología ágil principal, complementado con un **tablero Kanban** para visualizar el flujo de tareas. Scrum nos permite trabajar en sprints alineados con los entregables de la materia, mantener reuniones breves de seguimiento, organizar un backlog priorizado y entregar incrementos funcionales en cada hito (TP1, TP2 e integrador). El tablero Kanban cumple con los requisitos de la guía (al menos cinco columnas, tarjetas por épica y responsable asignado) y es clave para mantener transparencia y trazabilidad del trabajo tanto para el equipo como para el docente. La justificación técnica se basa en la necesidad de controlar el avance del proyecto, documentar decisiones de diseño, validar funcionalidades mediante pruebas y asegurar que cada integrante tenga responsabilidades claras. La combinación de Scrum + Kanban reduce la deuda técnica, facilita la detección temprana de bloqueos y permite adaptarnos rápidamente a cambios en requisitos o prioridades del sistema.

---

## **3. Roles asignados con nombre de cada integrante**

| **Nombre**                 | **Rol**                               | **GitHub**         |
| -------------------------- | ------------------------------------- | ------------------ |
| González Lautaro Sebastián | Scrum Master                          | @Lautaro-gonz      |
| Alonso Angelina            | Líder de desarrollo                   | @angelinaalonsoucp |
| Piedrafita José Augusto    | Líder de control de calidad (QA Lead) | @Gu7y              |
| Bruno                      | Líder de UX                           | @estudiandob-dev   |

---

## **4. Acuerdos de trabajo del equipo**

**Horarios de reunión y disponibilidad:**
El equipo acordará reuniones breves de sincronización durante los horarios de cursada o en bloques acordados previamente por el grupo. Cada integrante deberá comunicar su disponibilidad semanal en el canal principal para garantizar participación. Antes de cada entrega importante (TP1, TP2 y trabajo integrador) se realizará una reunión de seguimiento obligatorio para revisar el estado del proyecto, resolver bloqueos y redistribuir tareas según carga de trabajo.

**Canales de comunicación:**
Se utilizará un grupo de **WhatsApp** para comunicación rápida, avisos y coordinación diaria. El trabajo técnico se gestionará exclusivamente en **GitHub**, utilizando issues, branches, pull requests y el tablero Kanban, lo que garantiza trazabilidad completa. Todos los documentos importantes (tablero, repositorio, especificaciones) se compartirán en mensajes fijados para asegurar que todos tengan acceso permanente.

**Frecuencia y calidad de commits:**
Cada integrante deberá realizar commits frecuentes y con mensajes descriptivos, idealmente uno por tarea o por avance significativo. Los commits deben reflejar de forma concreta qué se implementó, documentando decisiones relevantes. El Líder de Desarrollo podrá definir convenciones adicionales como ramas por feature, estándares de PR, formato de nombres o reglas de revisión de código para mantener la coherencia del repositorio y asegurar calidad técnica.

**Criterios para mover tarjetas en el tablero:**
El responsable de la tarea será quien mueva la tarjeta siguiendo este flujo: *Backlog → En curso* al iniciar la actividad; *En curso → En revisión* cuando la tarea está implementada y el PR fue creado; *En revisión → Hecho* una vez aprobado por revisión o validado por el QA Lead. El tablero debe reflejar en todo momento el estado real del trabajo, ya que será utilizado por el docente para evaluar avance, orden y cumplimiento del proceso Scrum.

---

## **5. Descripción del sistema**

El **Sistema de Gestión de Turnos Médicos** permitirá digitalizar y modernizar la asignación de turnos, optimizando la interacción entre pacientes y recepcionistas. Incluirá funcionalidades para solicitar turnos según médico, especialidad y fecha disponible; visualizar agendas diarias; gestionar estados de turno (pendiente, confirmado, cancelado, atendido); y enviar notificaciones simuladas al paciente. Los usuarios principales serán la recepcionista y los pacientes, con acceso a funciones diferenciadas según rol. El sistema está diseñado para ser modular y escalable, de modo que se puedan agregar mejoras futuras como recordatorios automáticos reales, historial médico o gestión de profesionales.

---

