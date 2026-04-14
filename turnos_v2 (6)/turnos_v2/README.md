# Turnos Medicos v2 — Sin base de datos (todo en memoria)

## Estructura del proyecto

```
turnos_v2/
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── manage.py
├── requirements.txt
├── accounts/
│   ├── usuarios.py     → usuarios en memoria + werkzeug
│   ├── views.py        → login, logout, dashboard, panel admin
│   └── urls.py
├── turnos/
│   ├── logica.py       → patrones de diseño (Singleton, State, Observer, Factory, Repository)
│   ├── views.py        → paneles de secretaria, doctor, paciente
│   └── urls.py
├── templates/
│   ├── base.html
│   ├── accounts/
│   └── turnos/
└── static/
    └── css/
        └── style.css
```

---

## Opcion 1 — Levantar con Docker (recomendado)

### Requisitos
- Tener Docker instalado

### Comandos

```bash
# Primera vez (construye la imagen)
docker compose up --build

# Las siguientes veces
docker compose up

# Detener el servidor
docker compose down
```

Abrir en el navegador: http://localhost:8000

---

## Opcion 2 — Levantar sin Docker

### Requisitos
- Python 3.11 o superior

### Comandos

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# Instalar dependencias
pip install -r requirements.txt

# Levantar el servidor
python manage.py runserver
```

Abrir en el navegador: http://127.0.0.1:8000

---

## Usuarios de prueba

| Usuario     | Contrasena | Rol        |
|-------------|------------|------------|
| admin       | admin123   | Admin      |
| secretaria  | secre123   | Secretaria |
| doctor1     | doc123     | Doctor     |
| paciente1   | pac123     | Paciente   |

---

## Patrones de diseño implementados

Todos se encuentran en `turnos/logica.py`

| Patron       | Clase/s                                      | Descripcion                                          |
|--------------|----------------------------------------------|------------------------------------------------------|
| Singleton    | ValidadorCobertura                           | Una sola instancia del validador en todo el sistema  |
| State        | EstadoPendiente, EstadoConfirmado, etc.      | Cada estado del turno define sus propias transiciones|
| Observer     | EmailObservador, SMSObservador, Console...   | Notifica cambios de estado a multiples suscriptores  |
| Factory      | TurnoFactory                                 | Centraliza la creacion del turno y sus observadores  |
| Repository   | TurnoRepository, MedicoRepository            | Centraliza el acceso y busqueda de datos en memoria  |

---

## Roles y accesos

| Rol        | Panel                  | Puede hacer                              |
|------------|------------------------|------------------------------------------|
| admin      | /admin/                | CRUD de usuarios, ver turnos             |
| secretaria | /turnos/secretaria/    | Crear, confirmar, cancelar, reprogramar  |
| doctor     | /turnos/doctor/        | Ver su agenda filtrada por fecha         |
| paciente   | /turnos/paciente/      | Ver sus turnos por DNI                   |

---

## Importante

Los datos se guardan en memoria mientras el servidor este corriendo.
Al reiniciar el servidor los turnos se pierden.
Los usuarios vuelven a los de prueba porque estan hardcodeados en `accounts/usuarios.py`.
