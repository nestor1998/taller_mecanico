from django.db import models
from django.conf import settings


# ============================
#  ROLES / USUARIOS
# ============================

class RolUsuario(models.TextChoices):
    RECEPCIONISTA = "RECEPCIONISTA", "Recepcionista"
    ENCARGADO_TALLER = "ENCARGADO_TALLER", "Encargado de Taller"
    MECANICO = "MECANICO", "Mecánico"
    ENCARGADO_BODEGA = "ENCARGADO_BODEGA", "Encargado de Bodega"


class PerfilUsuario(models.Model):
    """
    Perfil básico para controlar los roles del sistema (RNF04).
    """
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rol = models.CharField(max_length=30, choices=RolUsuario.choices)

    def __str__(self):
        return f"{self.usuario.username} - {self.get_rol_display()}"


# ============================
#  CLIENTES Y VEHÍCULOS
# ============================

class MarcaVehiculo(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class ModeloVehiculo(models.Model):
    marca = models.ForeignKey(MarcaVehiculo, on_delete=models.CASCADE, related_name="modelos")
    nombre = models.CharField(max_length=100)

    class Meta:
        unique_together = ("marca", "nombre")

    def __str__(self):
        return f"{self.marca} {self.nombre}"


class Cliente(models.Model):
    rut = models.CharField(max_length=12, unique=True)
    nombre = models.CharField(max_length=150)
    telefono = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} ({self.rut})"


class Vehiculo(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="vehiculos")
    patente = models.CharField(max_length=10, unique=True)
    marca = models.ForeignKey(MarcaVehiculo, on_delete=models.PROTECT)
    modelo = models.ForeignKey(ModeloVehiculo, on_delete=models.PROTECT)
    anio = models.PositiveIntegerField()
    kilometraje = models.PositiveIntegerField()
    fecha_ultimo_servicio = models.DateField(blank=True, null=True)
    golpes_observados = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.patente} - {self.marca} {self.modelo}"


# ============================
#  RECURSOS: MECÁNICOS, ZONAS
# ============================

class EspecialidadMecanico(models.Model):
    """
    Tipos: motor, transmisión, frenos, suspensión y dirección, escape,
    eléctrico, electrónico, combustible, etc.
    """
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre


class Mecanico(models.Model):
    nombre = models.CharField(max_length=150)
    rut = models.CharField(max_length=12, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    especialidad = models.ForeignKey(EspecialidadMecanico, on_delete=models.PROTECT)
    cantidad_ayudantes = models.PositiveSmallIntegerField(
        default=0,
        help_text="Número de ayudantes (1 o 2 máx.)."
    )

    def __str__(self):
        return f"{self.nombre} - {self.especialidad}"


class ZonaTrabajo(models.Model):
    """
    4 zonas, cada una soporta 5 autos (según entrevista).
    """
    nombre = models.CharField(max_length=50, unique=True)
    capacidad = models.PositiveSmallIntegerField(default=5)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre} (capacidad {self.capacidad})"


# ============================
#  INVENTARIO: PROVEEDORES, REPUESTOS, HERRAMIENTAS
# ============================

class Proveedor(models.Model):
    nombre = models.CharField(max_length=150)
    rut = models.CharField(max_length=12, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.nombre


class Repuesto(models.Model):
    ESTADO_CHOICES = [
        ("DISPONIBLE", "Disponible"),
        ("AGOTADO", "Agotado"),
        ("DESCONTINUADO", "Descontinuado"),
    ]

    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    fabricante = models.CharField(max_length=100, blank=True, null=True)
    modelo_compatible = models.CharField(max_length=150, blank=True, null=True)
    compatibilidad = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        help_text="Descripción general de compatibilidad."
    )
    stock = models.PositiveIntegerField(default=0)
    ubicacion_bodega = models.CharField(max_length=100, blank=True, null=True)
    precio_compra = models.PositiveIntegerField()
    precio_venta = models.PositiveIntegerField()
    fecha_ingreso = models.DateField()
    proveedor = models.ForeignKey(Proveedor, on_delete=models.SET_NULL, null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="DISPONIBLE")

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Herramienta(models.Model):
    ESTADO_CHOICES = [
        ("OPERATIVA", "Operativa"),
        ("EN_MANTENCION", "En mantención"),
        ("FUERA_SERVICIO", "Fuera de servicio"),
    ]

    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    marca = models.CharField(max_length=100, blank=True, null=True)
    modelo = models.CharField(max_length=100, blank=True, null=True)
    cantidad = models.PositiveIntegerField(default=1)
    ubicacion_fisica = models.CharField(max_length=100)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="OPERATIVA")
    fecha_adquisicion = models.DateField()
    responsable_asignado = models.ForeignKey(
        Mecanico,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Mecánico responsable de la herramienta."
    )
    fecha_ultima_mantencion = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


# ============================
#  SERVICIOS / CATÁLOGO
# ============================

class Servicio(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    precio_base = models.PositiveIntegerField()

    def __str__(self):
        return self.nombre


# ============================
#  ÓRDENES DE TRABAJO
# ============================

class EstadoOT(models.Model):
    """
    Ej: EN_ESPERA, PENDIENTE, EN_PROGRESO, FINALIZADA, ENTREGADA, CANCELADA
    """
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre


class OrdenTrabajo(models.Model):
    PRIORIDAD_CHOICES = [
        ("BAJA", "Baja"),
        ("MEDIA", "Media"),
        ("ALTA", "Alta"),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.PROTECT)
    mecanico = models.ForeignKey(Mecanico, on_delete=models.SET_NULL, null=True, blank=True)
    zona_trabajo = models.ForeignKey(ZonaTrabajo, on_delete=models.SET_NULL, null=True, blank=True)

    fecha_ingreso = models.DateField()
    fecha_estimada_entrega = models.DateField(blank=True, null=True)
    fecha_entrega_real = models.DateField(blank=True, null=True)

    motivo_ingreso = models.CharField(max_length=200)
    descripcion_problema = models.TextField()
    observaciones_iniciales = models.TextField(blank=True, null=True)

    estado = models.ForeignKey(EstadoOT, on_delete=models.PROTECT)
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default="MEDIA")
    en_lista_espera = models.BooleanField(
        default=False,
        help_text="True si la OT está en lista de espera (RF11)."
    )

    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"OT #{self.id} - {self.vehiculo.patente}"

    # Cálculos de totales (RF06)
    def total_servicios(self):
        return sum(item.total() for item in self.servicios.all())

    def total_repuestos(self):
        return sum(item.total() for item in self.repuestos.all())

    def total_general(self):
        return self.total_servicios() + self.total_repuestos()


class ItemServicio(models.Model):
    """
    Servicios asociados a la OT (mano de obra).
    """
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name="servicios")
    servicio = models.ForeignKey(Servicio, on_delete=models.PROTECT)
    precio = models.PositiveIntegerField(help_text="Precio aplicado a este servicio.")

    def total(self):
        return self.precio

    def __str__(self):
        return f"{self.servicio.nombre} en OT {self.orden.id}"


class ItemRepuesto(models.Model):
    """
    Repuestos utilizados en una OT.
    """
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name="repuestos")
    repuesto = models.ForeignKey(Repuesto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.PositiveIntegerField()

    def total(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.repuesto.nombre} x{self.cantidad} en OT {self.orden.id}"


class HerramientaEnUso(models.Model):
    """
    Herramientas asignadas a una OT (para CU-07 Controlar Herramientas).
    """
    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name="herramientas_usadas")
    herramienta = models.ForeignKey(Herramienta, on_delete=models.PROTECT)
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_devolucion = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.herramienta.nombre} en OT {self.orden.id}"


# ============================
#  BITÁCORA (HU009, CU-10)
# ============================

class BitacoraTrabajo(models.Model):
    ESTADO_AVANCE_CHOICES = [
        ("PENDIENTE", "Pendiente"),
        ("EN_PROCESO", "En proceso"),
        ("EN_PAUSA", "En pausa"),
        ("FINALIZADO", "Finalizado"),
    ]

    orden = models.ForeignKey(OrdenTrabajo, on_delete=models.CASCADE, related_name="bitacoras")
    mecanico = models.ForeignKey(Mecanico, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    estado_avance = models.CharField(max_length=20, choices=ESTADO_AVANCE_CHOICES, default="EN_PROCESO")
    descripcion = models.TextField(help_text="Tareas realizadas, observaciones, etc.")
    tiempo_ejecucion_minutos = models.PositiveIntegerField(
        default=0,
        help_text="Tiempo aproximado dedicado en esta entrada."
    )

    def __str__(self):
        return f"Bitácora OT {self.orden.id} - {self.fecha}"


class FotoBitacora(models.Model):
    bitacora = models.ForeignKey(BitacoraTrabajo, on_delete=models.CASCADE, related_name="fotos")
    imagen = models.ImageField(upload_to="bitacora/")

    def __str__(self):
        return f"Foto de Bitácora {self.bitacora.id}"


# ============================
#  CONTROL DE CALIDAD (RF07, CU-06)
# ============================

class ControlCalidad(models.Model):
    RESULTADO_CHOICES = [
        ("APROBADO", "Aprobado"),
        ("RECHAZADO", "Rechazado"),
    ]

    orden = models.OneToOneField(OrdenTrabajo, on_delete=models.CASCADE, related_name="control_calidad")
    fecha = models.DateTimeField(auto_now_add=True)
    responsable = models.CharField(max_length=150, help_text="Encargado de Taller que realiza el control.")
    resultado = models.CharField(max_length=10, choices=RESULTADO_CHOICES)
    observaciones_generales = models.TextField(blank=True, null=True)

    # Ejemplo de campos de checklist (adaptables según documento físico)
    prueba_ruta_ok = models.BooleanField(default=False)
    fluidos_verificados = models.BooleanField(default=False)
    luces_sistema_electrico_ok = models.BooleanField(default=False)
    herramientas_retiradas = models.BooleanField(default=False)
    vehiculo_limpio = models.BooleanField(default=False)

    def __str__(self):
        return f"Control de calidad OT {self.orden.id} - {self.resultado}"


# ============================
#  NOTIFICACIONES / ALERTAS (RF05, CU-11)
# ============================

class TipoNotificacion(models.TextChoices):
    SOLICITUD_CAMBIO = "SOLICITUD_CAMBIO", "Solicitud de cambio"
    ATRASO_TRABAJO = "ATRASO_TRABAJO", "Atraso de trabajo"
    MENSAJE_GENERAL = "MENSAJE_GENERAL", "Mensaje general"


class Notificacion(models.Model):
    """
    Usada para:
    - HU005: Avisar cambios en el trabajo
    - HU006 / HU010: Alertar atrasos
    - HU007: Solicitud de cambios del mecánico
    - Alertas generales (stock bajo, etc.) - orden puede ser None
    """
    tipo = models.CharField(max_length=30, choices=TipoNotificacion.choices)
    orden = models.ForeignKey(
        OrdenTrabajo,
        on_delete=models.CASCADE,
        related_name="notificaciones",
        null=True,
        blank=True,
        help_text="Puede ser None para notificaciones generales (ej: stock bajo)"
    )
    emisor = models.ForeignKey(
        PerfilUsuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name="notificaciones_enviadas",
        blank=True,
    )
    receptor = models.ForeignKey(
        PerfilUsuario,
        on_delete=models.SET_NULL,
        null=True,
        related_name="notificaciones_recibidas",
        blank=True,
    )
    mensaje = models.TextField()
    creada_en = models.DateTimeField(auto_now_add=True)
    leida = models.BooleanField(default=False)

    def __str__(self):
        if self.orden:
            return f"{self.get_tipo_display()} - OT {self.orden.id}"
        return f"{self.get_tipo_display()} - General"
