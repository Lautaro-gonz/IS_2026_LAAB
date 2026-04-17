# Análisis de Estándares HCI y Sistemas Críticos

> **TP2 · Eje 3** — Investigación de estándares internacionales aplicados al proyecto.  
> Archivo ubicado en: `docs/ANALISIS_ESTANDARES.md`

---

## Tabla comparativa de estándares

| Estándar | Año (aprox.) | Enfoque principal | ¿Aplica a mi proyecto? | Justificación |
|---|---|---|---|---|
| **ISO 9241-11** | 1998 / rev. 2018 | Usabilidad: eficacia, eficiencia y satisfacción del usuario en contexto de uso. | ✅ Sí | Toda interfaz de usuario debe garantizar que las tareas se completen correctamente y sin esfuerzo innecesario. Aplica al diseño de pantallas, flujos y retroalimentación al usuario. |
| **ISO 13407** | 1999 (→ ISO 9241-210:2010) | Proceso de diseño centrado en el humano (DCH): 4 pasos iterativos. | ✅ Sí | El proceso de desarrollo debería involucrar al usuario desde el principio. Sus 4 pasos (contexto → requisitos → solución → evaluación) son aplicables en cada sprint. |
| **ISO/IEC 27001** | 2005 / rev. 2013, 2022 | Seguridad de la información: gestión de riesgos, confidencialidad, integridad, disponibilidad (tríada CIA). | ✅ Sí — alta relevancia | Si el sistema maneja datos sensibles (pacientes, transacciones, usuarios), esta norma define los controles mínimos de seguridad: acceso, cifrado, auditoría e incidentes. |
| **ISA/IEC 62443** | Serie 2007–2018 | Ciberseguridad en sistemas de control industrial: SCADA, PLC, DCS, redes OT. | ⚠️ Parcial | Aplica directamente si hay integración con infraestructura física/OT. Sus conceptos de zonas y conductos son adaptables a otros escenarios con distintos niveles de criticidad. |
| **ISO 9001** | 1987 / rev. 2015 | Calidad en procesos: planificación, control, trazabilidad y mejora continua. | ✅ Sí | Aplica al proceso de desarrollo: trazabilidad de requisitos, validación sistemática y criterios de aceptación auditables. |

---

## Análisis aplicado al proyecto

### ¿Cuáles estándares son más relevantes para el escenario elegido?

Para el escenario elegido en el Sprint 0, los estándares más relevantes son:

- **ISO/IEC 27001**: porque el sistema gestiona datos sensibles que requieren protección activa contra accesos no autorizados, pérdida o alteración.
- **ISO 9241-11**: porque los operadores o usuarios finales necesitan interactuar con el sistema de forma eficaz, especialmente en situaciones de presión o urgencia.
- **ISO 9001**: porque la trazabilidad del proceso de desarrollo y la validación sistemática son requisitos mínimos para cualquier sistema que impacte en decisiones críticas.

### ¿Qué estándares serían obligatorios si el sistema fuera declarado "crítico"?

Si el sistema fuera declarado crítico (ej. monitoreo de pacientes, control de tránsito aéreo, gestión de fondos bancarios), debería cumplir **obligatoriamente**:

1. **ISO/IEC 27001** — para garantizar la seguridad de la información en todas sus dimensiones (confidencialidad, integridad, disponibilidad).
2. **ISO 9001** — para asegurar que el proceso de desarrollo, validación y mantenimiento es reproducible, auditable y mejora continuamente.
3. **ISA/IEC 62443** — si existe integración con sistemas de control físico (sensores, actuadores, redes OT), ya que define niveles de seguridad por zonas y requisitos de resiliencia ante ataques.

### ¿Qué concepto de ISO 13407 o ISO 9241-11 sigue siendo útil hoy, incluso en sistemas críticos?

El concepto de **evaluación iterativa con usuarios reales** (paso 4 de ISO 13407) sigue siendo fundamental incluso en sistemas críticos modernos. En entornos de alta presión —dashboards de control aéreo, interfaces de monitoreo médico— un error de usabilidad puede tener consecuencias fatales. Ningún control técnico de seguridad reemplaza la validación con el usuario final en condiciones realistas.

Del lado de ISO 9241-11, el concepto de **eficacia** es el más crítico: un sistema seguro que el operador no puede usar correctamente bajo presión no es un sistema verdaderamente seguro.

---

## Conclusión

Si tuviéramos que certificar nuestro sistema bajo un estándar actual, elegiríamos **ISO/IEC 27001** como eje principal, complementado con **ISO 9001**. ISO/IEC 27001 obliga a realizar un análisis de riesgos formal sobre los activos de información, lo que forzaría revisiones concretas en nuestra arquitectura: el patrón **Observer** debería registrar cada evento en un log de auditoría, y la instancia única del patrón **Singleton** que gestiona configuración debería estar protegida contra modificaciones no autorizadas en tiempo de ejecución. ISO 9001, por su parte, implicaría formalizar cada decisión de diseño con criterios de aceptación verificables, alineando nuestro backlog de GitHub con requisitos auditables. En conjunto, ambas normas elevarían la madurez del proyecto de un prototipo funcional a un sistema listo para entornos reales.

---

## Decisiones de diseño del TP1 y su relación con los estándares

| Patrón utilizado en TP1 | Estándar relacionado | ¿Ayuda o dificulta? | Observación |
|---|---|---|---|
| **Observer** | ISO/IEC 27001 | ✅ Ayuda | Registro desacoplado de eventos → facilita implementar logs de auditoría requeridos por la norma. |
| **Singleton** | ISO/IEC 27001 | ⚠️ Dificulta (parcial) | Punto único de configuración → posible vector de ataque si no tiene control de acceso estricto. |
| **Factory** | ISO 9001 | ✅ Ayuda | Creación centralizada de objetos → trazabilidad y tests de validación sistemáticos más sencillos. |
| **Strategy** | ISO 9241-11 | ✅ Ayuda | Comportamiento intercambiable según perfil de usuario → mejora eficiencia y adaptabilidad de la UI. |

> **Nota:** Adaptar esta tabla con los patrones efectivamente implementados en el TP1 del grupo.

---

## Referencias

| Estándar | Título completo | Organismo |
|---|---|---|
| ISO 9241-11:2018 | Ergonomics of human-system interaction — Usability: Definitions and concepts | ISO/IEC |
| ISO 13407:1999 | Human-centred design processes for interactive systems | ISO |
| ISO/IEC 27001:2022 | Information security management systems — Requirements | ISO/IEC |
| ISA/IEC 62443 | Security for industrial automation and control systems | ISA/IEC |
| ISO 9001:2015 | Quality management systems — Requirements | ISO |

---

*Documento generado para el TP2 · Eje 3 — Análisis de estándares HCI y sistemas críticos.*
