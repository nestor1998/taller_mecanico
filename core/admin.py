from django.contrib import admin
from .models import (
    PerfilUsuario, RolUsuario,
    MarcaVehiculo, ModeloVehiculo, Cliente, Vehiculo,
    EspecialidadMecanico, Mecanico, ZonaTrabajo,
    Proveedor, Repuesto, Herramienta,
    Servicio, EstadoOT, OrdenTrabajo,
    ItemServicio, ItemRepuesto, HerramientaEnUso,
    BitacoraTrabajo, FotoBitacora,
    ControlCalidad,
    Notificacion
)


# ============================
#  PERFIL USUARIO
# ============================

@admin.register(PerfilUsuario)
class PerfilUsuarioAdmin(admin.ModelAdmin):
    list_display = ("usuario", "rol")
    list_filter = ("rol",)
    search_fields = ("usuario__username", "usuario__email", "rol")


# ============================
#  CLIENTES Y VEHICULOS
# ============================

@admin.register(MarcaVehiculo)
class MarcaVehiculoAdmin(admin.ModelAdmin):
    search_fields = ("nombre",)


@admin.register(ModeloVehiculo)
class ModeloVehiculoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "marca")
    list_filter = ("marca",)
    search_fields = ("nombre", "marca__nombre")


class VehiculoInline(admin.TabularInline):
    model = Vehiculo
    extra = 0


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("nombre", "rut", "telefono", "email")
    search_fields = ("nombre", "rut", "telefono", "email")
    inlines = [VehiculoInline]


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("patente", "cliente", "marca", "modelo", "anio", "kilometraje")
    list_filter = ("marca", "modelo", "anio")
    search_fields = ("patente", "cliente__nombre", "marca__nombre", "modelo__nombre")


# ============================
#  MECANICOS Y RECURSOS
# ============================

@admin.register(EspecialidadMecanico)
class EspecialidadAdmin(admin.ModelAdmin):
    search_fields = ("nombre",)


@admin.register(Mecanico)
class MecanicoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "especialidad", "telefono", "cantidad_ayudantes")
    list_filter = ("especialidad",)
    search_fields = ("nombre", "especialidad__nombre")


@admin.register(ZonaTrabajo)
class ZonaTrabajoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "capacidad", "activa")
    list_filter = ("activa",)
    search_fields = ("nombre",)


# ============================
#  PROVEEDORES / INVENTARIO
# ============================

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("nombre", "rut", "telefono", "email")
    search_fields = ("nombre", "rut", "telefono", "email")


@admin.register(Repuesto)
class RepuestoAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "stock", "precio_venta", "estado", "proveedor")
    list_filter = ("estado", "proveedor")
    search_fields = ("codigo", "nombre", "marca", "fabricante", "proveedor__nombre")
    list_editable = ("stock", "precio_venta", "estado")


@admin.register(Herramienta)
class HerramientaAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "cantidad", "estado", "responsable_asignado")
    list_filter = ("estado",)
    search_fields = ("codigo", "nombre", "marca", "modelo")


# ============================
#  SERVICIOS
# ============================

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio_base")
    search_fields = ("nombre",)


# ============================
#  ORDENES DE TRABAJO
# ============================

class ItemServicioInline(admin.TabularInline):
    model = ItemServicio
    extra = 1


class ItemRepuestoInline(admin.TabularInline):
    model = ItemRepuesto
    extra = 1


class HerramientaEnUsoInline(admin.TabularInline):
    model = HerramientaEnUso
    extra = 1


class BitacoraInline(admin.TabularInline):
    model = BitacoraTrabajo
    extra = 0
    readonly_fields = ("fecha",)


@admin.register(EstadoOT)
class EstadoOTAdmin(admin.ModelAdmin):
    search_fields = ("nombre",)


@admin.register(OrdenTrabajo)
class OrdenTrabajoAdmin(admin.ModelAdmin):
    list_display = (
        "id", "vehiculo", "cliente_nombre", "estado", "mecanico",
        "zona_trabajo", "fecha_ingreso", "fecha_estimada_entrega", "prioridad", "en_lista_espera"
    )
    list_filter = ("estado", "prioridad", "en_lista_espera", "mecanico", "zona_trabajo")
    search_fields = ("vehiculo__patente", "cliente__nombre", "id")

    inlines = [ItemServicioInline, ItemRepuestoInline, HerramientaEnUsoInline, BitacoraInline]

    def cliente_nombre(self, obj):
        return obj.cliente.nombre
    cliente_nombre.short_description = "Cliente"


# ============================
#  BITÁCORA
# ============================

@admin.register(BitacoraTrabajo)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ("orden", "mecanico", "estado_avance", "fecha", "tiempo_ejecucion_minutos")
    list_filter = ("estado_avance", "mecanico")
    search_fields = ("orden__id", "mecanico__nombre")
    readonly_fields = ("fecha",)


@admin.register(FotoBitacora)
class FotoBitacoraAdmin(admin.ModelAdmin):
    list_display = ("bitacora", "imagen")
    search_fields = ("bitacora__id",)


# ============================
#  CONTROL DE CALIDAD
# ============================

@admin.register(ControlCalidad)
class ControlCalidadAdmin(admin.ModelAdmin):
    list_display = ("orden", "resultado", "fecha", "responsable")
    list_filter = ("resultado",)
    search_fields = ("orden__id", "responsable")


# ============================
#  NOTIFICACIONES
# ============================

@admin.register(Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("tipo", "orden", "emisor", "receptor", "creada_en", "leida")
    list_filter = ("tipo", "leida")
    search_fields = ("orden__id", "mensaje", "emisor__usuario__username", "receptor__usuario__username")
    list_editable = ("leida",)
