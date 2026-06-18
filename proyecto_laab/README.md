# Turnos Médicos v2 — Con Base de Datos SQLite

## Cómo levantar

```bash
# 1. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Aplicar migraciones para crear la base de datos
python manage.py makemigrations
python manage.py migrate

# 4. Levantar el servidor
python manage.py runserver
```

Abrí el navegador en: http://127.0.0.1:8000

---

## Usuarios de prueba (se cargarán al iniciar si no existen)

| Usuario     | Contraseña | Rol        |
|-------------|------------|------------|
| admin       | admin123   | Admin      |
| secretaria  | secre123   | Secretaria |
| doctor1     | doc123     | Doctor     |
| paciente1   | pac123     | Paciente   |

---

## Patrones de diseño implementados

| Patrón      | Dónde                          |
|-------------|-------------------------------|
| Singleton   | ValidadorCobertura            |
| State       | EstadoPendiente/Confirmado... |
| Observer    | Email/SMS/ConsoleObservador   |
| Factory     | TurnoFactory                  |

---
