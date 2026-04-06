Diagrama de clases

Este diagrama se basa en el caso de uso del Sistema de Turnos de la
Clinica Privada, donde los actores principales son el Paciente y la
Recepcionista. El Paciente puede solicitar turnos eligiendo medico,
especialidad, fecha y hora, validando su obra social y calculando el
costo. La Recepcionista gestiona los turnos confirmando, cancelando
y reprogramando, y el sistema notifica automaticamente al paciente
ante cada cambio de estado.

El diagrama representa la estructura del sistema mostrando las clases
principales del dominio (Turno, Paciente, Medico, ObraSocial) y la
implementacion de los patrones de diseño:

- **State**: EstadoTurno y sus 5 estados concretos (Pendiente, Confirmado, En Atencion, Completado, Cancelado)
- **Observer**: ObservadorTurno con Email, SMS y Console
- **Singleton**: ValidadorCobertura
- **Factory**: TurnoFactory
- **Repository**: TurnoRepository, MedicoRepository y UsuarioRepository
  
