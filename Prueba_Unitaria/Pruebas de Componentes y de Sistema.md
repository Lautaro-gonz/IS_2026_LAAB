# 🏥 Plan de Pruebas — Sistema de Turnos

---

## 📦 Componente elegido

> **Núcleo de gestión de turnos** — lógica central del sistema, aislada de Django.

El componente incluye:

| Elemento | Rol |
|---|---|
| `Turno` | Entidad principal |
| Estados | Patrón **State** |
| Notificaciones | Patrón **Observer** |
| `CalculoCosto` | Lógica de precios y obras sociales |
| `SistemaTurnos` | Coordinador general |

**¿Por qué este componente?**
- ✅ No es una sola clase → no es una prueba unitaria
- ✅ No incluye Django → no es todo el sistema
- ✅ Contiene la lógica más crítica del proyecto

---

## 🧪 Pruebas de componente (aislado)

Pruebas sobre `sistemadeturno.py` sin Django, solo con Python y `pytest`.

**Entorno:**
```
Python 3.x
pytest
archivo: sistemadeturno.py
```

---

### Caso 1 — Creación de turno

**Escenario:** Paciente con obra social, médico válido, fecha y hora definidas.

**Validaciones:**
- [ ] Estado inicial: `PENDIENTE`
- [ ] ID autoincremental
- [ ] Costo correcto según obra social

**Ejemplo:**
```
Obra social: OSDE → paga $1.000
```

---

### Caso 2 — Paciente sin obra social

**Escenario:** Turno creado para paciente sin OS.

**Validaciones:**
- [ ] Paga el costo total: `$10.000`

---

### Caso 3 — Transiciones de estado

**Transiciones válidas:**

```
PENDIENTE → CONFIRMADO ✅
CONFIRMADO → EN ATENCIÓN ✅
```

**Transiciones inválidas:**

```
PENDIENTE → COMPLETADO ❌ → ValueError
```

**Validaciones:**
- [ ] Transiciones válidas se ejecutan sin error
- [ ] Transiciones inválidas lanzan `ValueError`

---

### Caso 4 — Reprogramación

**Escenario:** Turno en estado `CONFIRMADO` es reprogramado.

**Validaciones:**
- [ ] El turno vuelve al estado `PENDIENTE`

---

### Caso 5 — Observer (notificaciones)

**Escenario:** Verificar que se notifica correctamente según los datos del paciente.

| Condición | Observador usado |
|---|---|
| Paciente tiene email | `EmailObservador` |
| Paciente tiene teléfono | `SMSObservador` |
| Siempre | `ConsoleObservador` |

**Estrategia:** Mockear observadores o capturar salida por consola.

---

### Caso 6 — SistemaTurnos

**Escenario:** Operaciones básicas sobre el sistema de turnos.

**Validaciones:**
- [ ] Se pueden agregar turnos correctamente
- [ ] La búsqueda por DNI retorna los turnos del paciente

---

## 🌐 Pruebas de sistema (end-to-end)

Flujo completo del sistema a través de la interfaz web.

### 🔄 Flujo crítico: crear y confirmar turno

```
Login → Crear turno → Confirmar turno → Ver agenda → Consulta por DNI
```

---

#### Paso 1 — Login

| Campo | Valor |
|---|---|
| Usuario | `secretaria` |

**Validaciones:**
- [ ] Acceso correcto
- [ ] Redirección al panel principal

---

#### Paso 2 — Crear turno

**Datos del formulario:**

| Campo | Valor |
|---|---|
| Paciente | nombre del paciente |
| DNI | número de DNI |
| Obra social | según corresponda |
| Médico | médico seleccionado |
| Fecha y hora | slot disponible |

**Validaciones:**
- [ ] Turno creado exitosamente
- [ ] Estado inicial: `PENDIENTE`
- [ ] Costo calculado correctamente

---

#### Paso 3 — Confirmar turno

**Acción:** Click en el botón *Confirmar*.

**Validaciones:**
- [ ] Estado cambia a `CONFIRMADO`
- [ ] El cambio se refleja en la interfaz

---

#### Paso 4 — Ver agenda

**Filtros aplicados:** médico + fecha.

**Validaciones:**
- [ ] El turno es visible en la agenda
- [ ] Estado mostrado es el correcto

---

#### Paso 5 — Consulta del paciente

**Acción:** Búsqueda por DNI.

**Validaciones:**
- [ ] El turno aparece en los resultados
- [ ] Los datos mostrados son correctos

---

## 🛠️ Herramientas E2E — Comparativa

| Herramienta | Ventajas | Desventajas |
|---|---|---|
| **Cypress** | Fácil de usar, rápido | Limitado fuera del navegador, menos flexible |
| **Selenium** | Muy conocido, compatible con todo | Más lento, configuración compleja |
| **Playwright** | Multinavegador, moderno, maneja bien asincronía | Curva de aprendizaje media |

---

## ✅ Herramienta elegida: Playwright

**Motivos de elección:**

- 🔗 Funciona bien con Django
- ⚡ Más moderno que Selenium
- 🧩 Más completo que Cypress
- 📈 Permite escalar a pruebas más complejas

---

## 📋 Resumen

| Aspecto | Decisión |
|---|---|
| Componente probado | Núcleo de gestión de turnos |
| Pruebas de componente | Lógica interna: estados, costos, observer |
| Pruebas de sistema | Flujo completo de usuario (E2E) |
| Herramienta E2E | **Playwright** |
