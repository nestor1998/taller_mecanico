"""
Señales de Django para notificaciones automáticas usando el patrón Observador.

Estas señales detectan cambios en los modelos y notifican automáticamente
a los observadores registrados.
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from datetime import date

from .models import OrdenTrabajo, BitacoraTrabajo, ControlCalidad
from .patterns.observer import get_orden_trabajo_subject


# Variable para rastrear el estado anterior
_estado_anterior_cache = {}


@receiver(pre_save, sender=OrdenTrabajo)
def guardar_estado_anterior(sender, instance, **kwargs):
    """
    Guarda el estado anterior de la OT antes de guardar.
    Esto permite detectar cambios de estado.
    """
    if instance.pk:
        try:
            ot_anterior = OrdenTrabajo.objects.get(pk=instance.pk)
            _estado_anterior_cache[instance.pk] = ot_anterior.estado.nombre if ot_anterior.estado else None
        except OrdenTrabajo.DoesNotExist:
            _estado_anterior_cache[instance.pk] = None
    else:
        _estado_anterior_cache[instance.pk] = None


@receiver(post_save, sender=OrdenTrabajo)
def notificar_cambio_estado_ot(sender, instance, created, **kwargs):
    """
    Notifica automáticamente cuando cambia el estado de una OT.
    Usa el patrón Observador.
    """
    estado_anterior = _estado_anterior_cache.get(instance.pk)
    estado_nuevo = instance.estado.nombre if instance.estado else None
    
    # Solo notificar si el estado cambió
    if estado_anterior != estado_nuevo and estado_nuevo:
        subject = get_orden_trabajo_subject()
        
        # Obtener emisor (si está disponible en el contexto)
        # Nota: En señales, no tenemos acceso directo al request.user
        # Por eso usamos None como emisor, los observers pueden manejarlo
        event = {
            'orden': instance,
            'tipo_evento': 'ESTADO_CAMBIADO',
            'estado_anterior': estado_anterior,
            'estado_nuevo': estado_nuevo,
            'emisor': None  # Se puede mejorar pasando el usuario en el contexto
        }
        
        subject.notify(event)
        
        # Limpiar cache
        if instance.pk in _estado_anterior_cache:
            del _estado_anterior_cache[instance.pk]


@receiver(post_save, sender=BitacoraTrabajo)
def notificar_bitacora_registrada(sender, instance, created, **kwargs):
    """
    Notifica automáticamente cuando se registra una bitácora.
    Usa el patrón Observador.
    """
    if created:
        subject = get_orden_trabajo_subject()
        
        # Obtener perfil del mecánico si está disponible
        emisor = None
        if instance.mecanico:
            # Intentar obtener el perfil del mecánico
            nombre_parts = instance.mecanico.nombre.split(maxsplit=1)
            if len(nombre_parts) == 2:
                from .models import PerfilUsuario
                emisor = PerfilUsuario.objects.filter(
                    rol="MECANICO",
                    usuario__first_name=nombre_parts[0],
                    usuario__last_name=nombre_parts[1]
                ).first()
        
        event = {
            'orden': instance.orden,
            'tipo_evento': 'BITACORA_REGISTRADA',
            'emisor': emisor
        }
        
        subject.notify(event)


@receiver(post_save, sender=ControlCalidad)
def notificar_control_calidad(sender, instance, created, **kwargs):
    """
    Notifica automáticamente cuando se realiza un control de calidad.
    Usa el patrón Observador.
    """
    if created:
        subject = get_orden_trabajo_subject()
        
        # Obtener perfil del encargado
        from .models import PerfilUsuario
        emisor = PerfilUsuario.objects.filter(
            rol="ENCARGADO_TALLER"
        ).first()
        
        event = {
            'orden': instance.orden,
            'tipo_evento': 'CONTROL_CALIDAD',
            'resultado': instance.resultado,
            'emisor': emisor
        }
        
        subject.notify(event)
        
        # Si está aprobado, notificar que la OT fue finalizada
        if instance.resultado == "APROBADO":
            event_finalizada = {
                'orden': instance.orden,
                'tipo_evento': 'OT_FINALIZADA',
                'emisor': emisor
            }
            subject.notify(event_finalizada)

