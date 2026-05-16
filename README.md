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

1. La verificación busca confirmar que el software fue desarrollado según los requisitos definidos; la validación intenta comprobar si el sistema realmente satisface las necesidades del usuario. En nuestro proyecto, una verificación sería revisar que el módulo de turnos siga las reglas planteadas; una validación sería mostrarlo al cliente y recibir su aprobación.

2. Para el próximo sprint incluiríamos dos actividades concretas: ejecutar pruebas unitarias sobre las nuevas funciones y realizar una revisión grupal del código antes de integrar cambios. Además, haríamos una demostración breve con el Product Owner para validar el funcionamiento esperado.

3. La inspección de código consiste en analizar el código de manera manual; en cambio, una prueba automática ejecuta el sistema para detectar fallos durante su funcionamiento. La inspección conviene para hallar problemas de diseño o lógica; las pruebas automáticas resultan más útiles para verificar comportamientos repetitivos.

4. Pylint permite detectar errores sin ejecutar el programa; por ejemplo, variables no utilizadas, problemas de sintaxis o funciones mal estructuradas. Este tipo de análisis ayuda a mantener un código más claro y ordenado.

5. Los métodos formales son imprescindibles en sistemas críticos; por ejemplo, software médico, aeronáutico o bancario, donde un error podría causar consecuencias graves. No se aplican siempre porque requieren mucho tiempo, conocimientos especializados y un proceso bastante complejo.

6. En Scrum o XP, el Product Owner participa en la Sprint Review para validar que el incremento desarrollado cumpla con lo esperado por el cliente. Las pruebas automatizadas se relacionan con este proceso porque permiten llegar a la revisión con funciones ya comprobadas y más estables.

---

## Enlaces

- 
https://github.com/users/estudiandob-dev/projects/1/views/1
