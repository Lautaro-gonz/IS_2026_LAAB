# Decisiones de Diseño Visual — Sistema de Turnos Médicos

> Documento de justificación de las elecciones gráficas y visuales adoptadas en el desarrollo de la interfaz del sistema.

---

## Índice

1. [Paleta de colores](#1-paleta-de-colores)
2. [Tipografía](#2-tipografía)
3. [Layout y estructura de pantalla](#3-layout-y-estructura-de-pantalla)
4. [Componentes de interfaz](#4-componentes-de-interfaz)
5. [Sistema de badges y estados](#5-sistema-de-badges-y-estados)
6. [Formularios y modales](#6-formularios-y-modales)
7. [Densidad visual y espaciado](#7-densidad-visual-y-espaciado)
8. [Contexto del usuario y accesibilidad](#8-contexto-del-usuario-y-accesibilidad)

---

## 1. Paleta de Colores

### Decisión adoptada

Se eligió una paleta **clara (light mode)**, basada en blancos, grises muy suaves y un azul principal (`#2563eb`), complementada con colores semánticos para estados (verde, amarillo, rojo, violeta).

```css
--bg: #f5f6fa;
--surface: #fff;
--primary: #2563eb;
--success: #059669;
--warning: #d97706;
--danger: #dc2626;
--purple: #7c3aed;
```

### Justificación

**El azul como color principal** es una elección deliberada para un sistema médico/clínico. El azul transmite confianza, profesionalismo y calma, valores que se asocian directamente con el sector salud. Ejemplos de sistemas reconocidos como Mercado Pago, sistemas bancarios y la mayoría de los ERP médicos del mercado usan azules por esta razón.

**El fondo gris suave (`#f5f6fa`)** en lugar de blanco puro reduce la fatiga visual. El personal de secretaría y médicos usa el sistema durante horas seguidas; un fondo completamente blanco genera más cansancio a la vista en pantallas de escritorio.

**Los colores semánticos tienen una función informativa clara:**

| Color | Uso | Razón |
|---|---|---|
| 🟢 Verde | Turnos confirmados / completados | Convención universal: verde = todo bien |
| 🟡 Amarillo/Ámbar | Turnos pendientes | Convención universal: amarillo = atención / en espera |
| 🔴 Rojo | Cancelaciones / eliminar | Convención universal: rojo = alerta / acción destructiva |
| 🟣 Violeta | Rol Admin | Diferencia visualmente el rol de mayor jerarquía |
| 🔵 Azul | Rol Secretaría / acciones primarias | Coherencia con el color principal del sistema |

> **Principio aplicado:** Los usuarios no leen, escanean. Usar color como código informativo permite entender el estado de un turno en menos de un segundo, sin leer el texto del badge.

---

## 2. Tipografía

### Decisión adoptada

Se usaron dos fuentes de la familia **DM** (Google Fonts):

- **DM Sans** → para todo el texto de interfaz (títulos, labels, botones, párrafos)
- **DM Mono** → exclusivamente para datos técnicos: usernames y horarios

### Justificación

**DM Sans** fue elegida porque combina legibilidad excelente a tamaños pequeños (12–14px) con un carácter moderno y neutro, sin ser genérica como Arial o Roboto. Es una fuente diseñada específicamente para interfaces digitales, con formas abiertas que facilitan la lectura rápida de tablas y formularios.

**DM Mono** para nombres de usuario y horarios tiene una razón funcional concreta: las fuentes monoespaciadas hacen que los datos alfanuméricos sean más fáciles de comparar y leer alineados en tabla. Por ejemplo, al ver una lista de usernames o una columna de horarios (`08:00`, `08:30`, `09:00`), la fuente monoespaciada garantiza que los caracteres queden visualmente alineados.

```
Ejemplo con DM Mono:    Ejemplo con DM Sans:
08:00                   8:00
08:30                   8:30
14:00                   14:00
```
> La columna de la izquierda es más fácil de escanear verticalmente.

**Jerarquía tipográfica aplicada:**
- Títulos de sección: `18px / font-weight: 600`
- Títulos de card: `16px / font-weight: 600`
- Texto de tabla: `14px / font-weight: 400`
- Labels de formulario: `13px / font-weight: 500`
- Texto secundario/meta: `12–13px / color: var(--text-muted)`

Esta jerarquía guía el ojo del usuario de lo más importante a lo menos importante, sin necesidad de íconos ni decoraciones adicionales.

---

## 3. Layout y estructura de pantalla

### Decisión adoptada

**Sidebar fija a la izquierda** (240px de ancho) + **área de contenido principal** a la derecha, con una **topbar** fija en la parte superior del área principal.

```
┌─────────────┬──────────────────────────────────────┐
│             │  Topbar (título + acciones)           │
│   Sidebar   ├──────────────────────────────────────┤
│   (240px)   │                                      │
│             │   Contenido principal                │
│   Navega-   │                                      │
│   ción      │                                      │
│   + Usuario │                                      │
└─────────────┴──────────────────────────────────────┘
```

### Justificación

Este patrón de layout se eligió por tres razones principales:

**1. Es el estándar de los sistemas de gestión internos (dashboards).** Herramientas como Notion, Linear, Figma, sistemas de HIS médicos y ERPs usan este layout porque el usuario siempre sabe dónde está la navegación. No hay que buscarlo. La memoria muscular se construye rápido: "la navegación siempre está a la izquierda".

**2. La sidebar muestra solo las opciones del rol activo.** Un médico no ve opciones de secretaría. Un paciente no ve el panel de administración. Esto reduce el ruido visual y evita errores de navegación. Mostrar solo lo que le corresponde al usuario logueado es un principio de diseño llamado *progressive disclosure* (revelación progresiva).

**3. La topbar cumple dos funciones separadas:** a la izquierda muestra el título de la pantalla actual (orientación), y a la derecha las acciones contextuales del botón principal (ej: "+ Nuevo usuario"). Separar "dónde estoy" de "qué puedo hacer" reduce la carga cognitiva.

---

## 4. Componentes de interfaz

### Cards

Las tarjetas (`card`) agrupan información relacionada con bordes redondeados (`border-radius: 16px`) y una sombra muy sutil. Se eligió este componente porque:

- Crea separación visual entre bloques de contenido sin usar líneas divisorias agresivas
- El borde redondeado suaviza la interfaz, apropiado para un contexto de salud donde la experiencia debe sentirse amigable y no intimidante
- La sombra mínima da la percepción de "flotación" y jerarquía sin distraer

### Stat Cards (tarjetas de estadística)

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│     12      │  │      3      │  │      7      │
│   Turnos    │  │  Confirmados│  │  Pendientes │
└─────────────┘  └─────────────┘  └─────────────┘
```

Se muestran al inicio de cada panel para que el usuario entienda de un vistazo el estado general del día. El número grande y el color diferenciado permiten captarlo en menos de 2 segundos, antes de revisar la tabla de detalle.

### Botones

Se definieron variantes con propósito claro:

| Variante | Visual | Uso |
|---|---|---|
| `btn-primary` | Azul sólido | Acción principal (guardar, crear) |
| `btn-danger` | Rojo sólido | Acciones destructivas (eliminar, cancelar turno) |
| `btn-ghost` | Borde gris, sin relleno | Acciones secundarias (cancelar, volver) |
| `btn-success` | Verde sólido | Confirmar / completar |
| `btn-sm` | Tamaño reducido | Acciones dentro de tablas |

> **Principio:** El botón más importante visualmente debe ser la acción más importante de esa pantalla. Un usuario que nunca usó el sistema antes debe poder adivinar cuál es la acción principal.

---

## 5. Sistema de Badges y Estados

### Decisión adoptada

Los estados de los turnos y los roles de usuario se muestran como **badges** (píldoras de colores) en lugar de texto plano.

```
  PENDIENTE    CONFIRMADO    CANCELADO    EN ATENCIÓN
```

### Justificación

En una tabla con muchos turnos, el ojo humano detecta el color antes de leer el texto. Usar badges permite que la secretaría o el médico escaneen una lista de 20 turnos y encuentren inmediatamente los que están pendientes (amarillo) o cancelados (rojo) sin leer fila por fila.

Esto sigue el principio de **preattentive attributes** en visualización: el color y la forma se procesan antes de que el cerebro lea. Aprovecharlo reduce el tiempo que tarda el usuario en encontrar lo que busca.

Los estados de rol (admin, secretaria, doctor, paciente) también usan badges con colores diferenciados, permitiendo identificar el rol de un usuario en la tabla sin leer la columna "Rol".

---

## 6. Formularios y Modales

### Formularios en grilla de 2 columnas

Los formularios con múltiples campos usan un `grid` de dos columnas con `gap: 16px`. Esto fue una decisión deliberada para:

- Aprovechar el espacio horizontal disponible en pantallas de escritorio (el sistema no está pensado para mobile)
- Reducir el largo vertical del formulario, evitando que el usuario tenga que hacer scroll para llegar al botón de guardar
- Agrupar campos relacionados visualmente (nombre + apellido, fecha + hora)

Los campos que necesitan más espacio (como "Obra social") usan `grid-column: 1 / -1` para ocupar todo el ancho.

### Modal para crear usuario

Se eligió un **modal (diálogo superpuesto)** en lugar de una página separada para la creación de usuarios porque:

- La acción de crear un usuario es breve (5-6 campos) y no justifica una navegación completa
- El modal mantiene al usuario en contexto: puede ver la lista de usuarios de fondo mientras completa el formulario
- El overlay semitransparente (`rgba(0,0,0,.4)`) focaliza la atención en el modal sin desorientar al usuario sobre dónde está

---

## 7. Densidad visual y espaciado

### Decisión adoptada

Se eligió una densidad **media**, con padding generoso en cards (`24px`) y celdas de tabla (`14px 16px`), pero sin exceso de espacio en blanco que desperdicie pantalla.

### Justificación

El sistema es usado principalmente por secretarias de consultorio médico, que necesitan ver **varios turnos a la vez** en pantalla. Un diseño con espaciado muy generoso ("aireado") haría que se vean menos filas por pantalla, obligando a hacer scroll constantemente.

Por el contrario, una densidad muy alta (tablas comprimidas, texto pequeño) cansa la vista y aumenta los errores de lectura.

El punto medio elegido permite ver aproximadamente **8-10 turnos** en una pantalla de 1080p sin scroll, que es el rango adecuado para una agenda médica diaria promedio.

> **Referencia de decisión:** Al observar herramientas similares como sistemas de turnos de clínicas o el propio Google Calendar en vista semanal, el espaciado elegido es consistente con lo que los usuarios de este tipo de sistemas ya conocen.

---

## 8. Contexto del usuario y accesibilidad

### Hover en filas de tabla

Las filas de tabla tienen un highlight de hover (`background: var(--surface2)`) que facilita seguir la lectura horizontal en tablas anchas, especialmente cuando hay muchas columnas (nombre, usuario, rol, especialidad, acciones).

### Feedback visual en inputs

Los campos de formulario muestran un borde azul y un `box-shadow` suave al recibir foco. Esto es un principio básico de accesibilidad: el usuario siempre sabe qué campo está editando, especialmente cuando navega con teclado (Tab).

### Confirmación antes de eliminar

Los botones de eliminar usan `onclick="return confirm(...)"` para mostrar un diálogo de confirmación nativo del navegador antes de ejecutar la acción destructiva. Aunque es un componente básico, cumple el principio de **prevención de errores**: una acción irreversible siempre debe pedir confirmación explícita.

### Mensaje vacío en tablas

Cuando no hay datos, la tabla muestra un mensaje centrado en lugar de aparecer vacía. Esto evita que el usuario piense que hubo un error de carga cuando simplemente no hay registros todavía.

---

## Resumen de principios aplicados

| Principio | Aplicación concreta |
|---|---|
| Jerarquía visual | Tamaños tipográficos, colores, botones primarios vs secundarios |
| Código de color semántico | Badges de estado y rol |
| Preattentive attributes | Colores en badges permiten escaneo rápido de tablas |
| Progressive disclosure | Sidebar muestra solo opciones del rol activo |
| Prevención de errores | Confirmación antes de eliminar |
| Feedback inmediato | Focus visible en inputs, hover en filas |
| Densidad adecuada al uso | Ver múltiples turnos sin scroll excesivo |
| Consistencia | Mismos componentes, colores y espaciados en todas las pantallas |

---

*Documento generado como parte de la documentación del proyecto — Sistema de Turnos Médicos.*
