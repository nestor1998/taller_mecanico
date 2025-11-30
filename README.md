# Sistema de Gestión de Taller Mecánico

Sistema profesional de gestión para talleres mecánicos desarrollado en Django, con roles, bitácoras, inventario, planificación, control de calidad, notificaciones, generación de PDFs y dashboards por rol.

## 📋 Características

- ✅ **Sistema de usuarios con roles**: Recepcionista, Mecánico, Encargado de Taller, Encargado de Bodega
- ✅ **Registro de solicitudes**: Recepción de vehículos y creación de órdenes de trabajo
- ✅ **Planificación**: Asignación de mecánicos y zonas de trabajo
- ✅ **Bitácoras**: Registro de trabajos realizados con fotos
- ✅ **Control de calidad**: Checklist de verificación antes de entregar vehículos
- ✅ **Inventario**: Gestión de repuestos y herramientas
- ✅ **Notificaciones**: Sistema de alertas y mensajes entre roles
- ✅ **Generación de PDFs**: Informes de órdenes de trabajo
- ✅ **Validaciones robustas**: RUT chileno, patentes, fechas, stock
- ✅ **Tests automatizados**: Suite completa de pruebas unitarias y funcionales

## 🚀 Instalación

### Requisitos previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Pasos de instalación

1. **Clonar o descargar el proyecto**

```bash
cd taller_mecanico
```

2. **Crear un entorno virtual (recomendado)**

```bash
python -m venv venv

# En Windows
venv\Scripts\activate

# En Linux/Mac
source venv/bin/activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Aplicar migraciones**

```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Crear usuario superusuario (opcional, para acceder al admin)**

```bash
python manage.py createsuperuser
```

6. **Poblar base de datos con datos de prueba (opcional)**

```bash
python manage.py seed
```

Este comando crea:
- 6 usuarios de prueba (recepcion1, encargado1, bodega1, mecanico1, mecanico2, mecanico3)
- 10 clientes con vehículos
- 12 órdenes de trabajo en diferentes estados
- Bitácoras, repuestos, herramientas, notificaciones y controles de calidad

**Credenciales de prueba:**
- Usuario: `recepcion1` / Contraseña: `123` (Recepcionista)
- Usuario: `encargado1` / Contraseña: `123` (Encargado de Taller)
- Usuario: `bodega1` / Contraseña: `123` (Encargado de Bodega)
- Usuario: `mecanico1` / Contraseña: `123` (Mecánico)
- Usuario: `mecanico2` / Contraseña: `123` (Mecánico)
- Usuario: `mecanico3` / Contraseña: `123` (Mecánico)

7. **Ejecutar el servidor de desarrollo**

```bash
python manage.py runserver
```

El sistema estará disponible en `http://127.0.0.1:8000/`

## 👥 Creación de Usuarios

### Opción 1: Registro desde la interfaz web

1. Ir a `http://127.0.0.1:8000/registro/`
2. Completar el formulario:
   - Usuario
   - Contraseña (y confirmación)
   - Nombre completo
   - Rol (Recepcionista, Mecánico, Encargado de Taller, Encargado de Bodega)
3. Al registrarse como **Mecánico**, se crea automáticamente una entrada en el modelo `Mecanico`

### Opción 2: Desde el admin de Django

1. Acceder a `http://127.0.0.1:8000/admin/`
2. Crear un usuario en "Users"
3. Crear un "Perfil Usuario" asociado al usuario con el rol correspondiente
4. Si el rol es "Mecánico", crear también una entrada en "Mecánicos"

## 🔐 Roles y Permisos

### Recepcionista
- Registrar solicitudes de trabajo
- Ver dashboard con resumen
- Ver notificaciones

### Mecánico
- Ver trabajos asignados
- Registrar bitácoras con fotos
- Retirar y devolver herramientas
- Ver notificaciones

### Encargado de Taller
- Planificar y asignar OTs
- Ver inventario
- Realizar control de calidad
- Generar PDFs de informes
- Ver notificaciones

### Encargado de Bodega
- Gestionar inventario de repuestos
- Editar repuestos
- Realizar movimientos de stock
- Gestionar herramientas
- Ver notificaciones

## 📖 Uso del Sistema

### 1. Registrar una Solicitud (Recepcionista)

1. Ir a "Registrar Solicitud"
2. Completar datos del cliente (RUT, nombre, teléfono)
3. Completar datos del vehículo (patente, marca, modelo, año, kilometraje)
4. Describir el motivo y problema
5. Guardar

**Validaciones:**
- RUT debe ser válido (formato chileno)
- Patente debe tener formato válido (ABCD12 o AB1234)
- No se permiten vehículos duplicados por patente

### 2. Planificar y Asignar OT (Encargado de Taller)

1. Ir a "Planificación"
2. Ver lista de OTs pendientes
3. Seleccionar una OT
4. Asignar mecánico, zona y fecha estimada
5. Guardar

**Resultado:** La OT pasa a estado "EN_PROGRESO" y se notifica al mecánico.

### 3. Registrar Bitácora (Mecánico)

1. Ir a "Mis Trabajos"
2. Seleccionar una OT
3. Ir a "Registrar Bitácora"
4. Completar:
   - Descripción del trabajo realizado
   - Tiempo de ejecución (minutos)
   - Estado de avance
   - Fotos (opcional)
   - Solicitud de cambio (opcional)
5. Guardar

### 4. Control de Calidad (Encargado de Taller)

1. Desde el detalle de una OT, ir a "Control de Calidad"
2. Completar checklist:
   - Prueba de ruta OK
   - Fluidos verificados
   - Luces y sistema eléctrico OK
   - Herramientas retiradas
   - Vehículo limpio
3. Seleccionar resultado (Aprobado/Rechazado)
4. Agregar observaciones
5. Guardar

**Resultado:** Si es aprobado, la OT pasa a "FINALIZADO".

### 5. Gestionar Inventario (Encargado de Bodega)

#### Editar Repuesto
1. Ir a "Inventario"
2. Seleccionar "Editar" en un repuesto
3. Modificar datos
4. Guardar

#### Movimiento de Stock
1. Seleccionar "Movimiento" en un repuesto
2. Elegir tipo (Entrada/Salida)
3. Ingresar cantidad
4. Guardar

**Validaciones:**
- No se permite stock negativo
- Si hay salida sin stock suficiente, se muestra error

### 6. Herramientas (Mecánico / Encargado de Bodega)

- **Mecánico:** Puede retirar y devolver herramientas
- **Encargado de Bodega:** Puede editar herramientas

**Validaciones:**
- No se puede retirar una herramienta que no está operativa
- No se puede devolver una herramienta que no se retiró

## 🌱 Poblar Base de Datos con Datos de Prueba

El proyecto incluye un comando de management para poblar la base de datos con datos realistas:

```bash
python manage.py seed
```

Este comando crea automáticamente:

- **Usuarios y perfiles:**
  - 1 recepcionista (recepcion1 / 123)
  - 1 encargado de taller (encargado1 / 123)
  - 1 encargado de bodega (bodega1 / 123)
  - 3 mecánicos (mecanico1, mecanico2, mecanico3 / 123)

- **Clientes y vehículos:**
  - 10 clientes con RUTs chilenos válidos
  - 10 vehículos con patentes chilenas (formato antiguo y nuevo)
  - Marcas y modelos reales

- **Órdenes de trabajo:**
  - 4 OTs en estado PENDIENTE
  - 4 OTs en estado EN_PROGRESO
  - 2 OTs FINALIZADAS
  - 2 OTs ATRASADAS (fecha estimada < hoy)

- **Bitácoras:**
  - Entre 1 y 4 bitácoras por OT (con mecánico asignado)
  - Descripciones realistas
  - Tiempos de ejecución (20-120 minutos)

- **Inventario:**
  - 20 repuestos con códigos, nombres, precios y stock
  - 3 repuestos con stock bajo (1 o 2 unidades)

- **Herramientas:**
  - 10 herramientas (6 operativas, 2 en mantención, 2 retiradas)
  - Asignaciones a mecánicos y OTs

- **Notificaciones:**
  - Notificaciones de atraso
  - Solicitudes de cambio
  - Mensajes generales
  - Alertas de stock bajo

- **Control de calidad:**
  - 1 OT aprobada
  - 1 OT rechazada

**Nota:** El comando es idempotente. Si los usuarios ya existen, no los recrea. Puedes ejecutarlo múltiples veces sin problemas.

## 🧪 Ejecutar Tests

El proyecto incluye una suite completa de tests:

```bash
python manage.py test
```

### Tests incluidos:

- ✅ Login y autenticación
- ✅ Registro de usuario
- ✅ Dashboards por rol
- ✅ Registro de solicitudes
- ✅ Asignación de OTs
- ✅ Registro de bitácoras
- ✅ Gestión de inventario
- ✅ Control de calidad
- ✅ Notificaciones
- ✅ Validaciones (RUT, patente)
- ✅ Herramientas

## 📁 Estructura del Proyecto

```
taller_mecanico/
├── core/
│   ├── models.py          # Modelos de datos
│   ├── views.py           # Vistas del sistema
│   ├── forms.py           # Formularios Django
│   ├── urls.py            # Rutas de la aplicación
│   ├── validators.py      # Validadores personalizados
│   ├── decorators.py      # Decoradores para permisos
│   ├── context_processors.py  # Context processors
│   ├── tests.py           # Suite de tests
│   ├── admin.py           # Configuración del admin
│   └── templates/         # Templates HTML
├── taller_mecanico/
│   ├── settings.py        # Configuración de Django
│   ├── urls.py            # URLs principales
│   └── wsgi.py
├── media/                 # Archivos subidos (fotos de bitácoras)
├── db.sqlite3             # Base de datos SQLite
├── requirements.txt        # Dependencias
└── README.md              # Este archivo
```

## 🔧 Validaciones Implementadas

### RUT Chileno
- Formato: 12345678-9 o 12.345.678-9
- Validación del dígito verificador

### Patente Chilena
- Formato antiguo: ABCD12 (4 letras + 2 números)
- Formato nuevo: AB1234 (2 letras + 4 números)

### Fechas
- Fecha estimada debe ser posterior a fecha de ingreso
- Validación de fechas no futuras (según contexto)

### Stock
- No permite valores negativos
- Validación al realizar movimientos de salida

### Kilometraje
- Solo valores positivos

## 📄 Generación de PDFs

Los PDFs se generan usando `xhtml2pdf`. Para generar un informe:

1. Como Encargado de Taller o Recepcionista
2. Ir al detalle de una OT
3. Seleccionar "Generar Informe PDF"

El PDF incluye:
- Datos del cliente y vehículo
- Descripción del trabajo
- Servicios y repuestos utilizados
- Totales
- Tiempo total de ejecución

## 🔔 Sistema de Notificaciones

Las notificaciones se crean automáticamente en estos casos:

- **Asignación de OT:** Al asignar una OT a un mecánico
- **Atrasos:** Cuando una OT supera la fecha estimada
- **Solicitud de cambio:** Cuando un mecánico solicita cambios
- **Control de calidad:** Al aprobar o rechazar una OT
- **Stock bajo:** Cuando un repuesto tiene menos de 3 unidades

## 🛠️ Tecnologías Utilizadas

- **Django 5.2.5:** Framework web
- **Bootstrap 5.3.2:** Framework CSS
- **xhtml2pdf:** Generación de PDFs
- **Pillow:** Manejo de imágenes
- **SQLite:** Base de datos (desarrollo)

## 📝 Notas Importantes

1. **Base de datos:** El proyecto usa SQLite por defecto. Para producción, se recomienda usar PostgreSQL o MySQL.

2. **Archivos media:** Las fotos de bitácoras se guardan en `media/bitacora/`. Asegúrate de tener permisos de escritura.

3. **Seguridad:** En producción, cambiar `SECRET_KEY` y configurar `DEBUG=False`.

4. **Estados de OT:** El sistema requiere que existan los siguientes estados:
   - PENDIENTE
   - EN_PROGRESO
   - FINALIZADO
   - EN_ESPERA (opcional)

   Estos se crean automáticamente al usar el sistema, pero puedes crearlos desde el admin.

## 🐛 Solución de Problemas

### Error: "PerfilUsuario.DoesNotExist"
- **Causa:** Usuario sin perfil asociado
- **Solución:** Crear PerfilUsuario desde el admin o usar el registro web

### Error: "No se encontró tu perfil de mecánico"
- **Causa:** Usuario con rol MECANICO pero sin entrada en modelo Mecanico
- **Solución:** Crear entrada en Mecanico desde el admin o re-registrarse

### Error al generar PDF
- **Causa:** Falta instalar xhtml2pdf
- **Solución:** `pip install xhtml2pdf`

### Error al subir imágenes
- **Causa:** Falta configurar MEDIA_ROOT o permisos
- **Solución:** Verificar que existe la carpeta `media/` y tiene permisos de escritura

## 📞 Soporte

Para problemas o consultas, revisar:
1. Los logs del servidor Django
2. La consola del navegador (F12)
3. Los tests para verificar el funcionamiento esperado

## 📜 Licencia

Este proyecto es de uso educativo y profesional.

---

**Desarrollado con ❤️ para talleres mecánicos**

