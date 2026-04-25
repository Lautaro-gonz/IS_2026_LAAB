#### **Dependencias externas identificadas**

El sistema tiene las siguientes dependencias externas:

**Dependencia 1 — Servicio de Email (EmailObservador)** En **`turnos/logica.py`**, el **`EmailObservador`** simula el envío de un correo al paciente cuando cambia el estado del turno. En producción real esto conectaría con un servidor SMTP externo (Gmail, etc.). Es una dependencia de red que no debe ejecutarse en las pruebas.

**Dependencia 2 — Servicio de SMS (SMSObservador)** Similar al anterior, el **`SMSObservador`** simula el envío de un mensaje de texto. En producción conectaría con una API de terceros como Twilio. Tampoco debe ejecutarse en las pruebas.

#### **Herramienta utilizada**

**`unittest.mock`** — incluida en la biblioteca estándar de Python.

#### **Diferencia entre Mock y Stub en el sistema**

Un **stub** reemplaza una dependencia y devuelve valores controlados, sin verificar cómo fue llamado. Un **mock** además registra las interacciones y permite verificar que el componente bajo prueba llamó a la dependencia de la manera esperada.

#### **Prueba de integración N°1 — Observer con Mock de Email**

**Componente bajo prueba:** El patrón Observer en la clase **`Turno`**, específicamente la notificación al confirmar un turno.

**Dependencia aislada con Mock:** `EmailObservador` — se reemplaza para no enviar emails reales.

**Flujo:**

1. Se crea un `Paciente` con email y un `Medico`  
2. Se crea un `Turno` en estado PENDIENTE  
3. Se reemplaza `EmailObservador` con un `MagicMock`  
4. Se suscribe el mock al turno  
5. Se llama `turno.confirmar()`  
6. Se verifica que el mock fue llamado exactamente una vez con el mensaje correcto  
7. Se verifica que el estado cambió a CONFIRMADO

#### **Prueba de integración N°2 — Factory con Stub de ObraSocialRepository**

**Componente bajo prueba:** `TurnoFactory` y el cálculo de costos con `CalculoCosto`.

**Dependencia aislada con Stub:** `ObraSocialRepository` — se reemplaza con un stub que siempre devuelve una obra social activa con 90% de cobertura, sin depender del estado global en memoria.

**Flujo:**

1. Se crea un stub del `ObraSocialRepository` que devuelve OSDE activa con 90%  
2. Se parchea `obra_social_repo` en `logica.py` con el stub usando `patch()`  
3. Se crea un `Paciente` con email, teléfono y obra social OSDE  
4. Se llama `TurnoFactory.crear()`  
5. Se verifica que el turno tiene 3 observadores suscritos (Email \+ SMS \+ Console)  
6. Se verifica que el costo se calculó correctamente: paciente paga $1.000 (10% de $10.000)

