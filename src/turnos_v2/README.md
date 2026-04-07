# Turnos Médicos 

## Cómo levantar

```bash
# 1. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Levantar el servidor 
python manage.py runserver
```

Abrí el navegador en: http://127.0.0.1:8000

---

## Usuarios de prueba (ya cargados)

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
| Repository  | TurnoRepository               |

---

## Importante

Los datos se guardan en memoria mientras el servidor esté corriendo.
Al reiniciar el servidor los turnos se pierden (los usuarios se mantienen porque están hardcodeados).
