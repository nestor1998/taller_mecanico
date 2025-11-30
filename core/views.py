from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.template.loader import get_template
from django.http import HttpResponse, JsonResponse
from xhtml2pdf import pisa
from datetime import date

from .models import (
    PerfilUsuario, Cliente, Vehiculo, MarcaVehiculo, ModeloVehiculo,
    OrdenTrabajo, EstadoOT, BitacoraTrabajo, FotoBitacora,
    Repuesto, Herramienta, HerramientaEnUso, Mecanico, ZonaTrabajo,
    ControlCalidad, Notificacion, EspecialidadMecanico
)
from .forms import (
    RegistroUsuarioForm, RegistrarSolicitudForm, AsignarOTForm,
    BitacoraForm, ControlCalidadForm, EditarRepuestoForm,
    MovimientoRepuestoForm, EditarHerramientaForm
)
from .decorators import requiere_perfil_usuario, requiere_rol
from .validators import validar_fecha_estimada_mayor_ingreso
from .helpers import obtener_mecanico_desde_usuario


# ============================
# LOGIN / LOGOUT / REGISTRO
# ============================

def login_view(request):
    """Vista de login."""
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "POST":
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        if user:
            login(request, user)
            # Verificar que tenga perfil
            try:
                user.perfilusuario
            except PerfilUsuario.DoesNotExist:
                messages.error(request, "Tu cuenta no tiene un perfil asociado. Contacta al administrador.")
                logout(request)
                return redirect("login")
            return redirect("dashboard")
        messages.error(request, "Usuario o contraseña incorrectos.")
    return render(request, "core/login.html")


def logout_view(request):
    """Vista de logout."""
    logout(request)
    return redirect("login")


def registro_view(request):
    """Vista de registro de usuario."""
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    if request.method == "POST":
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            nombre = form.cleaned_data["nombre"]
            rol = form.cleaned_data["rol"]
            
            # Crear PerfilUsuario
            perfil = PerfilUsuario.objects.create(usuario=user, rol=rol)
            
            # Si es MECANICO, crear entrada en Mecanico
            if rol == "MECANICO":
                # Obtener o crear una especialidad por defecto
                especialidad_default, _ = EspecialidadMecanico.objects.get_or_create(
                    nombre="General"
                )
                Mecanico.objects.create(
                    nombre=nombre,
                    especialidad=especialidad_default
                )
            
            messages.success(request, f"Usuario {user.username} registrado correctamente. Puedes iniciar sesión.")
            return redirect("login")
    else:
        form = RegistroUsuarioForm()
    
    return render(request, "core/registro.html", {"form": form})


# ============================
# DASHBOARD
# ============================

@login_required
@requiere_perfil_usuario
def dashboard(request):
    """Dashboard principal según el rol del usuario."""
    perfil = request.user.perfilusuario
    
    # Contador de notificaciones no leídas
    notif_no_leidas = perfil.notificaciones_recibidas.filter(leida=False).count()
    
    # RECEPCIONISTA
    if perfil.rol == "RECEPCIONISTA":
        return render(request, "core/dashboard/recepcion.html", {
            "notif_no_leidas": notif_no_leidas,
        })
    
    # ENCARGADO DE TALLER
    if perfil.rol == "ENCARGADO_TALLER":
        pendientes = OrdenTrabajo.objects.filter(estado__nombre="PENDIENTE").count()
        en_progreso = OrdenTrabajo.objects.filter(estado__nombre="EN_PROGRESO").count()
        atrasadas = OrdenTrabajo.objects.filter(
            fecha_estimada_entrega__lt=date.today(),
            estado__nombre="EN_PROGRESO"
        ).count()
        
        return render(request, "core/dashboard/encargado.html", {
            "pendientes": pendientes,
            "en_progreso": en_progreso,
            "atrasadas": atrasadas,
            "notif_no_leidas": notif_no_leidas,
        })
    
    # MECÁNICO
    if perfil.rol == "MECANICO":
        # Obtener mecánico de forma segura
        mecanico_obj = obtener_mecanico_desde_usuario(request.user)
        trabajos = 0
        if mecanico_obj:
            trabajos = OrdenTrabajo.objects.filter(
                mecanico=mecanico_obj,
                estado__nombre="EN_PROGRESO"
            ).count()
        
        return render(request, "core/dashboard/mecanico.html", {
            "trabajos": trabajos,
            "notif_no_leidas": notif_no_leidas,
        })
    
    # ENCARGADO DE BODEGA
    if perfil.rol == "ENCARGADO_BODEGA":
        stock_bajo = Repuesto.objects.filter(stock__lt=3).count()
        
        return render(request, "core/dashboard/bodega.html", {
            "stock_bajo": stock_bajo,
            "notif_no_leidas": notif_no_leidas,
        })
    
    # Fallback
    return render(request, "core/dashboard/base.html", {
        "notif_no_leidas": notif_no_leidas
    })


# ============================
# RECEPCIONISTA
# ============================

@login_required
@requiere_rol("RECEPCIONISTA")
def registrar_solicitud(request):
    """Registrar nueva solicitud de trabajo."""
    if request.method == "POST":
        form = RegistrarSolicitudForm(request.POST)
        if form.is_valid():
            # Crear o actualizar cliente
            cliente, _ = Cliente.objects.get_or_create(
                rut=form.cleaned_data["rut"],
                defaults={
                    "nombre": form.cleaned_data["nombre"],
                    "telefono": form.cleaned_data["telefono"],
                    "email": form.cleaned_data.get("email", ""),
                }
            )
            
            # Validar que no exista vehículo con esa patente
            patente = form.cleaned_data["patente"]
            if Vehiculo.objects.filter(patente=patente).exists():
                messages.error(request, f"Ya existe un vehículo con la patente {patente}.")
                return render(request, "core/recepcion/registrar_solicitud.html", {
                    "form": form,
                    "marcas": MarcaVehiculo.objects.all(),
                })
            
            # Crear vehículo
            vehiculo = Vehiculo.objects.create(
                cliente=cliente,
                patente=patente,
                marca=form.cleaned_data["marca"],
                modelo=form.cleaned_data["modelo"],
                anio=form.cleaned_data["anio"],
                kilometraje=form.cleaned_data["kilometraje"],
            )
            
            # Obtener estado PENDIENTE
            estado = EstadoOT.objects.get_or_create(nombre="PENDIENTE")[0]
            
            # Crear OT
            OrdenTrabajo.objects.create(
                cliente=cliente,
                vehiculo=vehiculo,
                estado=estado,
                motivo_ingreso=form.cleaned_data["motivo"],
                descripcion_problema=form.cleaned_data["descripcion"],
                fecha_ingreso=form.cleaned_data["fecha"],
            )
            
            messages.success(request, "Solicitud registrada correctamente.")
            return redirect("dashboard")
    else:
        form = RegistrarSolicitudForm()
    
    return render(request, "core/recepcion/registrar_solicitud.html", {
        "form": form,
        "marcas": MarcaVehiculo.objects.all(),
    })


# ============================
# ENCARGADO DE TALLER
# ============================

@login_required
@requiere_rol("ENCARGADO_TALLER")
def planificacion(request):
    """Vista de planificación de OTs."""
    pendientes = OrdenTrabajo.objects.filter(
        estado__nombre__in=["PENDIENTE", "EN_ESPERA"]
    ).order_by("fecha_ingreso")
    
    mecanicos = Mecanico.objects.all().order_by("especialidad__nombre", "nombre")
    zonas = ZonaTrabajo.objects.filter(activa=True)
    
    return render(request, "core/encargado/planificacion.html", {
        "pendientes": pendientes,
        "mecanicos": mecanicos,
        "zonas": zonas,
    })


@login_required
@requiere_rol("ENCARGADO_TALLER")
def detalle_ot(request, ot_id):
    """Detalle y asignación de OT."""
    ot = get_object_or_404(OrdenTrabajo, pk=ot_id)
    
    if request.method == "POST":
        form = AsignarOTForm(request.POST)
        if form.is_valid():
            mecanico = form.cleaned_data["mecanico"]
            zona = form.cleaned_data["zona"]
            fecha_estimada = form.cleaned_data["fecha_estimada"]
            
            # Validar fecha estimada
            try:
                validar_fecha_estimada_mayor_ingreso(fecha_estimada, ot.fecha_ingreso)
            except Exception as e:
                messages.error(request, str(e))
                return render(request, "core/encargado/detalle_ot.html", {
                    "ot": ot,
                    "form": form,
                    "mecanicos": Mecanico.objects.all(),
                    "zonas": ZonaTrabajo.objects.filter(activa=True),
                })
            
            ot.mecanico = mecanico
            ot.zona_trabajo = zona
            ot.fecha_estimada_entrega = fecha_estimada
            
            estado_en_progreso = EstadoOT.objects.get_or_create(nombre="EN_PROGRESO")[0]
            ot.estado = estado_en_progreso
            ot.en_lista_espera = False
            ot.save()
            
            # Crear notificación al mecánico
            # Buscar el perfil del mecánico por el nombre completo
            perfil_mecanico = None
            if mecanico.nombre:
                # Buscar usuario que tenga first_name + last_name igual al nombre del mecánico
                nombre_parts = mecanico.nombre.split(maxsplit=1)
                if len(nombre_parts) == 2:
                    perfil_mecanico = PerfilUsuario.objects.filter(
                        rol="MECANICO",
                        usuario__first_name=nombre_parts[0],
                        usuario__last_name=nombre_parts[1]
                    ).first()
            
            if perfil_mecanico:
                Notificacion.objects.create(
                    tipo="MENSAJE_GENERAL",
                    orden=ot,
                    mensaje=f"Se le ha asignado la OT #{ot.id}.",
                    emisor=request.user.perfilusuario,
                    receptor=perfil_mecanico
                )
            
            messages.success(request, "Asignación realizada correctamente.")
            return redirect("planificacion")
    else:
        form = AsignarOTForm()
    
    return render(request, "core/encargado/detalle_ot.html", {
        "ot": ot,
        "form": form,
        "mecanicos": Mecanico.objects.all(),
        "zonas": ZonaTrabajo.objects.filter(activa=True),
    })


@login_required
@requiere_rol("ENCARGADO_TALLER", "RECEPCIONISTA")
def generar_informe_pdf(request, ot_id):
    """Generar PDF de informe de OT."""
    ot = get_object_or_404(OrdenTrabajo, pk=ot_id)
    
    # Calcular totales
    total_servicios = ot.total_servicios()
    total_repuestos = ot.total_repuestos()
    total_general = ot.total_general()
    
    # Calcular tiempo total
    tiempo_total = sum([b.tiempo_ejecucion_minutos for b in ot.bitacoras.all()])
    
    template_path = "core/encargado/informe_pdf.html"
    context = {
        "ot": ot,
        "total_servicios": total_servicios,
        "total_repuestos": total_repuestos,
        "total_general": total_general,
        "tiempo_total": tiempo_total,
    }
    
    template = get_template(template_path)
    html = template.render(context)
    
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=informe_OT_{ot.id}.pdf"
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    
    if pisa_status.err:
        return HttpResponse("Hubo un error generando el PDF", status=500)
    
    return response


@login_required
@requiere_rol("ENCARGADO_TALLER")
def control_calidad(request, ot_id):
    """Control de calidad de una OT."""
    ot = get_object_or_404(OrdenTrabajo, pk=ot_id)
    
    # Si ya existe control de calidad, mostrarlo
    if hasattr(ot, "control_calidad"):
        return render(request, "core/calidad/control_calidad.html", {
            "ot": ot,
            "control": ot.control_calidad,
            "modo": "ver"
        })
    
    if request.method == "POST":
        form = ControlCalidadForm(request.POST)
        if form.is_valid():
            control = form.save(commit=False)
            control.orden = ot
            control.responsable = request.user.username
            control.save()
            
            # Cambiar estado de la OT
            if control.resultado == "APROBADO":
                estado_finalizado = EstadoOT.objects.get_or_create(nombre="FINALIZADO")[0]
                ot.estado = estado_finalizado
            else:
                estado_pendiente = EstadoOT.objects.get_or_create(nombre="PENDIENTE")[0]
                ot.estado = estado_pendiente
            
            ot.save()
            
            # Notificación al mecánico
            if ot.mecanico:
                # Buscar el perfil del mecánico por el nombre completo
                perfil_mecanico = None
                if ot.mecanico.nombre:
                    nombre_parts = ot.mecanico.nombre.split(maxsplit=1)
                    if len(nombre_parts) == 2:
                        perfil_mecanico = PerfilUsuario.objects.filter(
                            rol="MECANICO",
                            usuario__first_name=nombre_parts[0],
                            usuario__last_name=nombre_parts[1]
                        ).first()
                
                if perfil_mecanico:
                    Notificacion.objects.create(
                        tipo="MENSAJE_GENERAL",
                        orden=ot,
                        mensaje=f"Control de calidad {control.resultado} para la OT #{ot.id}.",
                        emisor=request.user.perfilusuario,
                        receptor=perfil_mecanico
                    )
            
            messages.success(request, "Control de calidad registrado.")
            return redirect("detalle_ot", ot_id=ot.id)
    else:
        form = ControlCalidadForm()
    
    return render(request, "core/calidad/control_calidad.html", {
        "ot": ot,
        "form": form,
        "modo": "crear"
    })


# ============================
# MECÁNICO
# ============================

@login_required
@requiere_rol("MECANICO")
def mis_trabajos(request):
    """Lista de trabajos asignados al mecánico."""
    # El decorador @requiere_rol("MECANICO") ya garantiza que el usuario es mecánico
    # Obtener mecánico de forma segura
    mecanico_obj = obtener_mecanico_desde_usuario(request.user)
    
    if not mecanico_obj:
        # Si no se encuentra el mecánico, mostrar mensaje pero no error crítico
        messages.warning(request, "Tu perfil de mecánico no está completamente configurado. Contacta al administrador.")
        trabajos = []
    else:
        trabajos = OrdenTrabajo.objects.filter(
            mecanico=mecanico_obj,
            estado__nombre__in=["EN_PROGRESO", "PENDIENTE"]
        ).order_by("fecha_ingreso")
        
        # ALERTAS DE ATRASO (HU010)
        perfil_encargado = PerfilUsuario.objects.filter(rol="ENCARGADO_TALLER").first()
        
        for ot in trabajos:
            if ot.fecha_estimada_entrega and ot.estado.nombre != "FINALIZADO":
                if date.today() > ot.fecha_estimada_entrega:
                    if not Notificacion.objects.filter(
                        tipo="ATRASO_TRABAJO",
                        orden=ot
                    ).exists() and perfil_encargado:
                        Notificacion.objects.create(
                            tipo="ATRASO_TRABAJO",
                            orden=ot,
                            mensaje=f"La OT #{ot.id} está atrasada.",
                            emisor=request.user.perfilusuario,
                            receptor=perfil_encargado
                        )
    
    return render(request, "core/mecanico/mis_trabajos.html", {"trabajos": trabajos})


@login_required
@requiere_rol("MECANICO")
def registrar_bitacora(request, ot_id):
    """Registrar bitácora de trabajo."""
    ot = get_object_or_404(OrdenTrabajo, pk=ot_id)
    
    # Obtener mecánico de forma segura
    mecanico_obj = obtener_mecanico_desde_usuario(request.user)
    
    if not mecanico_obj:
        messages.warning(request, "Tu perfil de mecánico no está completamente configurado. Contacta al administrador.")
        return redirect("mis_trabajos")
    
    if request.method == "POST":
        form = BitacoraForm(request.POST, request.FILES)
        if form.is_valid():
            bitacora = form.save(commit=False)
            bitacora.orden = ot
            bitacora.mecanico = mecanico_obj
            bitacora.save()
            
            # Guardar fotos
            imagenes = request.FILES.getlist("imagenes")
            for img in imagenes:
                FotoBitacora.objects.create(bitacora=bitacora, imagen=img)
            
            # Solicitud de cambio (HU007)
            solicitud_cambio = form.cleaned_data.get("solicitud_cambio", "").strip()
            if solicitud_cambio:
                perfil_encargado = PerfilUsuario.objects.filter(rol="ENCARGADO_TALLER").first()
                if perfil_encargado:
                    Notificacion.objects.create(
                        tipo="SOLICITUD_CAMBIO",
                        orden=ot,
                        mensaje=solicitud_cambio,
                        emisor=request.user.perfilusuario,
                        receptor=perfil_encargado
                    )
            
            messages.success(request, "Bitácora registrada correctamente.")
            return redirect("mis_trabajos")
    else:
        form = BitacoraForm()
    
    return render(request, "core/mecanico/registrar_bitacora.html", {
        "ot": ot,
        "form": form,
    })


# ============================
# INVENTARIO
# ============================

@login_required
@requiere_rol("ENCARGADO_BODEGA", "ENCARGADO_TALLER")
def inventario(request):
    """Vista de inventario de repuestos."""
    repuestos = Repuesto.objects.all().order_by("nombre")
    
    # ALERTA DE STOCK BAJO (solo crear notificación si hay stock bajo y no existe notificación reciente)
    perfil_encargado = PerfilUsuario.objects.filter(rol="ENCARGADO_TALLER").first()
    
    for r in repuestos:
        if r.stock < 3:
            # Verificar si ya existe una notificación reciente (últimas 24 horas)
            from django.utils import timezone
            from datetime import timedelta
            hace_24h = timezone.now() - timedelta(hours=24)
            
            if not Notificacion.objects.filter(
                tipo="MENSAJE_GENERAL",
                orden__isnull=True,
                mensaje__contains=f"Repuesto {r.nombre} bajo en stock",
                creada_en__gte=hace_24h
            ).exists() and perfil_encargado:
                Notificacion.objects.create(
                    tipo="MENSAJE_GENERAL",
                    orden=None,  # Notificación general, no asociada a OT
                    mensaje=f"Repuesto {r.nombre} bajo en stock (solo {r.stock} unidades).",
                    emisor=request.user.perfilusuario,
                    receptor=perfil_encargado
                )
    
    return render(request, "core/inventario/inventario.html", {
        "repuestos": repuestos,
    })


@login_required
@requiere_rol("ENCARGADO_BODEGA")
def editar_repuesto(request, id):
    """Editar repuesto."""
    repuesto = get_object_or_404(Repuesto, id=id)
    
    if request.method == "POST":
        form = EditarRepuestoForm(request.POST, instance=repuesto)
        if form.is_valid():
            form.save()
            messages.success(request, "Repuesto actualizado.")
            return redirect("inventario")
    else:
        form = EditarRepuestoForm(instance=repuesto)
    
    return render(request, "core/inventario/editar_repuesto.html", {
        "repuesto": repuesto,
        "form": form,
    })


@login_required
@requiere_rol("ENCARGADO_BODEGA")
def movimiento_repuesto(request, id):
    """Movimiento de stock de repuesto."""
    repuesto = get_object_or_404(Repuesto, id=id)
    
    if request.method == "POST":
        form = MovimientoRepuestoForm(request.POST)
        if form.is_valid():
            tipo = form.cleaned_data["tipo"]
            cantidad = form.cleaned_data["cantidad"]
            
            if tipo == "entrada":
                repuesto.stock += cantidad
            else:  # salida
                if repuesto.stock < cantidad:
                    messages.error(request, f"No hay suficiente stock. Disponible: {repuesto.stock}")
                    return render(request, "core/inventario/movimiento_repuesto.html", {
                        "repuesto": repuesto,
                        "form": form,
                    })
                repuesto.stock -= cantidad
            
            repuesto.save()
            messages.success(request, "Movimiento de stock realizado.")
            return redirect("inventario")
    else:
        form = MovimientoRepuestoForm()
    
    return render(request, "core/inventario/movimiento_repuesto.html", {
        "repuesto": repuesto,
        "form": form,
    })


@login_required
@requiere_rol("ENCARGADO_BODEGA")
def herramientas(request):
    """Lista de herramientas."""
    herramientas = Herramienta.objects.all()
    return render(request, "core/inventario/herramientas.html", {
        "herramientas": herramientas,
    })


@login_required
@requiere_rol("ENCARGADO_BODEGA")
def editar_herramienta(request, id):
    """Editar herramienta."""
    herramienta = get_object_or_404(Herramienta, id=id)
    
    if request.method == "POST":
        form = EditarHerramientaForm(request.POST, instance=herramienta)
        if form.is_valid():
            form.save()
            messages.success(request, "Herramienta actualizada correctamente.")
            return redirect("herramientas")
    else:
        form = EditarHerramientaForm(instance=herramienta)
    
    return render(request, "core/inventario/editar_herramienta.html", {
        "herramienta": herramienta,
        "form": form,
    })


@login_required
@requiere_rol("MECANICO")
def retirar_herramienta(request, id):
    """Retirar herramienta (mecánico)."""
    herramienta = get_object_or_404(Herramienta, id=id)
    
    # Verificar que la herramienta no esté en uso
    if herramienta.estado != "OPERATIVA":
        messages.error(request, "La herramienta no está disponible para retiro.")
        return redirect("herramientas")
    
    # Obtener mecánico de forma segura
    mecanico_obj = obtener_mecanico_desde_usuario(request.user)
    
    if not mecanico_obj:
        messages.warning(request, "Tu perfil de mecánico no está completamente configurado. Contacta al administrador.")
        return redirect("herramientas")
    
    # Crear registro de herramienta en uso
    ot_activa = OrdenTrabajo.objects.filter(
        mecanico=mecanico_obj,
        estado__nombre="EN_PROGRESO"
    ).first()
    
    if ot_activa:
        HerramientaEnUso.objects.create(
            orden=ot_activa,
            herramienta=herramienta,
            fecha_asignacion=timezone.now(),
        )
    
    herramienta.estado = "EN_MANTENCION"
    herramienta.responsable_asignado = mecanico_obj
    herramienta.save()
    
    messages.success(request, "Herramienta retirada.")
    return redirect("herramientas")


@login_required
@requiere_rol("MECANICO")
def devolver_herramienta(request, id):
    """Devolver herramienta (mecánico)."""
    herramienta = get_object_or_404(Herramienta, id=id)
    
    # Obtener mecánico de forma segura
    mecanico_obj = obtener_mecanico_desde_usuario(request.user)
    
    if not mecanico_obj:
        messages.warning(request, "Tu perfil de mecánico no está completamente configurado. Contacta al administrador.")
        return redirect("herramientas")
    
    # Verificar que el mecánico sea el responsable
    if herramienta.responsable_asignado:
        if herramienta.responsable_asignado != mecanico_obj:
            messages.error(request, "No eres el responsable de esta herramienta.")
            return redirect("herramientas")
    
    # Marcar como devuelta en HerramientaEnUso
    HerramientaEnUso.objects.filter(
        herramienta=herramienta,
        fecha_devolucion__isnull=True
    ).update(fecha_devolucion=timezone.now())
    
    herramienta.estado = "OPERATIVA"
    herramienta.responsable_asignado = None
    herramienta.save()
    
    messages.success(request, "Herramienta devuelta correctamente.")
    return redirect("herramientas")


# ============================
# NOTIFICACIONES
# ============================

@login_required
@requiere_perfil_usuario
def notificaciones(request):
    """Lista de notificaciones del usuario."""
    perfil = request.user.perfilusuario
    
    lista = Notificacion.objects.filter(
        receptor=perfil
    ).order_by("-creada_en")
    
    return render(request, "core/notificaciones/lista.html", {
        "notificaciones": lista
    })


@login_required
@requiere_perfil_usuario
def marcar_notificacion_leida(request, id):
    """Marcar notificación como leída."""
    notif = get_object_or_404(Notificacion, id=id)
    
    if notif.receptor != request.user.perfilusuario:
        messages.error(request, "No tienes permisos para esta acción.")
        return redirect("notificaciones")
    
    notif.leida = True
    notif.save()
    
    return redirect("notificaciones")


# ============================
# AJAX: Cargar modelos por marca
# ============================

@login_required
def cargar_modelos(request):
    """Vista AJAX para cargar modelos según la marca seleccionada."""
    marca_id = request.GET.get("marca_id")
    if marca_id:
        modelos = ModeloVehiculo.objects.filter(marca_id=marca_id).values("id", "nombre")
        return JsonResponse(list(modelos), safe=False)
    return JsonResponse([], safe=False)
