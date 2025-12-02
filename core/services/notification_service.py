"""
Notification Service - Servicio para gestión de notificaciones.

Usa el patrón Observador para notificaciones automáticas.
"""
from typing import Optional
from ..models import PerfilUsuario, OrdenTrabajo, TipoNotificacion, Notificacion
from ..patterns.observer import get_orden_trabajo_subject


class NotificationService:
    """
    Servicio para gestión de notificaciones.
    Usa el patrón Observador para notificaciones automáticas.
    """
    
    def __init__(self):
        """Inicializa el servicio con el Subject del patrón Observer."""
        self.subject = get_orden_trabajo_subject()
    
    def notificar_solicitud_cambio(
        self,
        orden: OrdenTrabajo,
        mensaje: str,
        emisor: PerfilUsuario
    ) -> None:
        """
        Notifica una solicitud de cambio usando el patrón Observer.
        
        Args:
            orden: OrdenTrabajo relacionada
            mensaje: Mensaje de la solicitud
            emisor: PerfilUsuario que solicita el cambio
        """
        event = {
            'orden': orden,
            'tipo_evento': 'SOLICITUD_CAMBIO',
            'mensaje': mensaje,
            'emisor': emisor
        }
        self.subject.notify(event)
    
    def notificar_atraso(
        self,
        orden: OrdenTrabajo,
        emisor: PerfilUsuario
    ) -> None:
        """
        Notifica un atraso usando el patrón Observer.
        
        Args:
            orden: OrdenTrabajo atrasada
            emisor: PerfilUsuario que detecta el atraso
        """
        # Verificar si ya existe notificación de atraso
        if Notificacion.objects.filter(
            tipo=TipoNotificacion.ATRASO_TRABAJO,
            orden=orden
        ).exists():
            return
        
        event = {
            'orden': orden,
            'tipo_evento': 'ATRASO',
            'emisor': emisor
        }
        self.subject.notify(event)
    
    def notificar_bitacora_registrada(
        self,
        orden: OrdenTrabajo,
        emisor: PerfilUsuario
    ) -> None:
        """
        Notifica que se registró una bitácora usando el patrón Observer.
        
        Args:
            orden: OrdenTrabajo relacionada
            emisor: PerfilUsuario que registró la bitácora
        """
        event = {
            'orden': orden,
            'tipo_evento': 'BITACORA_REGISTRADA',
            'emisor': emisor
        }
        self.subject.notify(event)
    
    def notificar_control_calidad(
        self,
        orden: OrdenTrabajo,
        resultado: str,
        emisor: PerfilUsuario
    ) -> None:
        """
        Notifica resultado de control de calidad usando el patrón Observer.
        
        Args:
            orden: OrdenTrabajo relacionada
            resultado: Resultado del control ('APROBADO' o 'RECHAZADO')
            emisor: PerfilUsuario que realizó el control
        """
        event = {
            'orden': orden,
            'tipo_evento': 'CONTROL_CALIDAD',
            'resultado': resultado,
            'emisor': emisor
        }
        self.subject.notify(event)
    
    def notificar_ot_finalizada(
        self,
        orden: OrdenTrabajo,
        emisor: PerfilUsuario
    ) -> None:
        """
        Notifica que una OT fue finalizada usando el patrón Observer.
        
        Args:
            orden: OrdenTrabajo finalizada
            emisor: PerfilUsuario que finalizó la OT
        """
        event = {
            'orden': orden,
            'tipo_evento': 'OT_FINALIZADA',
            'emisor': emisor
        }
        self.subject.notify(event)

