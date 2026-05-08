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


---

## Enlaces

- 
https://github.com/users/estudiandob-dev/projects/1/views/1
