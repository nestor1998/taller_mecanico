from django.urls import path
from . import views

urlpatterns = [
    # LOGIN / REGISTRO
    path("", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("registro/", views.registro_view, name="registro"),

    # DASHBOARD general
    path("dashboard/", views.dashboard, name="dashboard"),
    
    # AJAX
    path("ajax/cargar-modelos/", views.cargar_modelos, name="cargar_modelos"),

    # RECEPCIONISTA (HU001)
    path("solicitudes/registrar/", views.registrar_solicitud, name="registrar_solicitud"),

    # ENCARGADO (HU002–HU006)
    path("encargado/planificacion/", views.planificacion, name="planificacion"),
    path("encargado/ot/<int:ot_id>/", views.detalle_ot, name="detalle_ot"),

    # MECÁNICO (HU008–HU010)
    path("mecanico/mis-trabajos/", views.mis_trabajos, name="mis_trabajos"),
    path("mecanico/ot/<int:ot_id>/bitacora/", views.registrar_bitacora, name="registrar_bitacora"),
    path("encargado/ot/<int:ot_id>/informe/", views.generar_informe_pdf, name="generar_informe_pdf"),


    # CONTROL DE CALIDAD (CU-06)
    path("calidad/ot/<int:ot_id>/control/", views.control_calidad, name="control_calidad"),

# Inventario
path("inventario/", views.inventario, name="inventario"),
path("inventario/repuesto/<int:id>/editar/", views.editar_repuesto, name="editar_repuesto"),
path("inventario/herramientas/", views.herramientas, name="herramientas"),
path("inventario/herramienta/<int:id>/editar/", views.editar_herramienta, name="editar_herramienta"),

# Movimientos de stock
path("inventario/repuesto/<int:id>/movimiento/", views.movimiento_repuesto, name="movimiento_repuesto"),

# Retiro / devolución de herramientas
path("herramienta/<int:id>/retirar/", views.retirar_herramienta, name="retirar_herramienta"),
path("herramienta/<int:id>/devolver/", views.devolver_herramienta, name="devolver_herramienta"),

# Notificaciones
path("notificaciones/", views.notificaciones, name="notificaciones"),
path("notificaciones/leida/<int:id>/", views.marcar_notificacion_leida, name="notificacion_leida"),


]
