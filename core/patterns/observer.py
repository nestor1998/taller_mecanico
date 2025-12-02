"""
Implementación del patrón Observador para notificaciones automáticas.

Según la documentación:
- Subject: Estado de la Orden de Trabajo
- Observers: Diferentes roles (Mecánico, Encargado de Taller, Recepcionista)
- Cuando cambia el estado de una OT, se notifica automáticamente a los observadores
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from django.contrib.auth.models import User

from ..models import PerfilUsuario, Notificacion, OrdenTrabajo, TipoNotificacion


class Observer(ABC):
    """Interfaz para observadores del sistema."""
    
    @abstractmethod
    def update(self, event: Dict[str, Any]) -> None:
        """
        Método que se llama cuando el Subject notifica un cambio.
        
        Args:
            event: Diccionario con información del evento
                - 'orden': OrdenTrabajo
                - 'tipo_evento': str (ej: 'ESTADO_CAMBIADO', 'ASIGNACION', etc.)
                - 'estado_anterior': str (opcional)
                - 'estado_nuevo': str (opcional)
                - 'emisor': PerfilUsuario (opcional)
        """
        pass


class MecanicoObserver(Observer):
    """Observer para notificar a mecánicos."""
    
    def update(self, event: Dict[str, Any]) -> None:
        """Notifica al mecánico cuando hay cambios relevantes."""
        orden = event.get('orden')
        tipo_evento = event.get('tipo_evento')
        emisor = event.get('emisor')
        
        if not orden or not orden.mecanico:
            return
        
        # Buscar perfil del mecánico
        perfil_mecanico = self._obtener_perfil_mecanico(orden.mecanico)
        if not perfil_mecanico:
            return
        
        # Crear notificación según el tipo de evento
        if tipo_evento == 'ASIGNACION':
            mensaje = f"Se le ha asignado la OT #{orden.id}."
            tipo_notif = TipoNotificacion.MENSAJE_GENERAL
        elif tipo_evento == 'CONTROL_CALIDAD':
            resultado = event.get('resultado', '')
            mensaje = f"Control de calidad {resultado} para la OT #{orden.id}."
            tipo_notif = TipoNotificacion.MENSAJE_GENERAL
        elif tipo_evento == 'ESTADO_CAMBIADO':
            estado_nuevo = event.get('estado_nuevo', '')
            mensaje = f"La OT #{orden.id} cambió a estado: {estado_nuevo}."
            tipo_notif = TipoNotificacion.MENSAJE_GENERAL
        else:
            return
        
        Notificacion.objects.create(
            tipo=tipo_notif,
            orden=orden,
            mensaje=mensaje,
            emisor=emisor,
            receptor=perfil_mecanico
        )
    
    def _obtener_perfil_mecanico(self, mecanico):
        """Obtiene el PerfilUsuario asociado a un Mecanico."""
        nombre_parts = mecanico.nombre.split(maxsplit=1)
        if len(nombre_parts) == 2:
            return PerfilUsuario.objects.filter(
                rol="MECANICO",
                usuario__first_name=nombre_parts[0],
                usuario__last_name=nombre_parts[1]
            ).first()
        return None


class EncargadoObserver(Observer):
    """Observer para notificar a encargados de taller."""
    
    def update(self, event: Dict[str, Any]) -> None:
        """Notifica al encargado cuando hay cambios relevantes."""
        orden = event.get('orden')
        tipo_evento = event.get('tipo_evento')
        emisor = event.get('emisor')
        
        if not orden:
            return
        
        # Buscar perfil del encargado
        perfil_encargado = PerfilUsuario.objects.filter(
            rol="ENCARGADO_TALLER"
        ).first()
        
        if not perfil_encargado:
            return
        
        # Crear notificación según el tipo de evento
        if tipo_evento == 'SOLICITUD_CAMBIO':
            mensaje = event.get('mensaje', f"Solicitud de cambio para la OT #{orden.id}.")
            tipo_notif = TipoNotificacion.SOLICITUD_CAMBIO
        elif tipo_evento == 'ATRASO':
            mensaje = f"La OT #{orden.id} está atrasada."
            tipo_notif = TipoNotificacion.ATRASO_TRABAJO
        elif tipo_evento == 'BITACORA_REGISTRADA':
            mensaje = f"Se registró una nueva bitácora para la OT #{orden.id}."
            tipo_notif = TipoNotificacion.MENSAJE_GENERAL
        else:
            return
        
        Notificacion.objects.create(
            tipo=tipo_notif,
            orden=orden,
            mensaje=mensaje,
            emisor=emisor,
            receptor=perfil_encargado
        )


class RecepcionistaObserver(Observer):
    """Observer para notificar a recepcionistas."""
    
    def update(self, event: Dict[str, Any]) -> None:
        """Notifica al recepcionista cuando hay cambios relevantes."""
        orden = event.get('orden')
        tipo_evento = event.get('tipo_evento')
        emisor = event.get('emisor')
        
        if not orden:
            return
        
        # Buscar perfil del recepcionista
        perfil_recepcionista = PerfilUsuario.objects.filter(
            rol="RECEPCIONISTA"
        ).first()
        
        if not perfil_recepcionista:
            return
        
        # Crear notificación según el tipo de evento
        if tipo_evento == 'OT_FINALIZADA':
            mensaje = f"La OT #{orden.id} ha sido finalizada."
            tipo_notif = TipoNotificacion.MENSAJE_GENERAL
            
            Notificacion.objects.create(
                tipo=tipo_notif,
                orden=orden,
                mensaje=mensaje,
                emisor=emisor,
                receptor=perfil_recepcionista
            )


class OrdenTrabajoSubject:
    """
    Subject del patrón Observador.
    Representa el estado de la Orden de Trabajo y notifica cambios a los observadores.
    """
    
    def __init__(self):
        """Inicializa el Subject con una lista vacía de observadores."""
        self._observers: List[Observer] = []
        self._estado_anterior = None
    
    def attach(self, observer: Observer) -> None:
        """
        Registra un observador.
        
        Args:
            observer: Instancia de Observer a registrar
        """
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Observer) -> None:
        """
        Desregistra un observador.
        
        Args:
            observer: Instancia de Observer a desregistrar
        """
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, event: Dict[str, Any]) -> None:
        """
        Notifica a todos los observadores registrados sobre un cambio.
        
        Args:
            event: Diccionario con información del evento
        """
        for observer in self._observers:
            try:
                observer.update(event)
            except Exception as e:
                # Log error pero no interrumpir notificaciones a otros observadores
                print(f"Error notificando a observer {observer.__class__.__name__}: {e}")
    
    def cambiar_estado(self, orden: OrdenTrabajo, estado_nuevo: str, emisor: PerfilUsuario = None) -> None:
        """
        Método helper para notificar cambio de estado.
        
        Args:
            orden: OrdenTrabajo que cambió de estado
            estado_nuevo: Nuevo estado
            emisor: PerfilUsuario que realizó el cambio (opcional)
        """
        self._estado_anterior = orden.estado.nombre if orden.estado else None
        
        event = {
            'orden': orden,
            'tipo_evento': 'ESTADO_CAMBIADO',
            'estado_anterior': self._estado_anterior,
            'estado_nuevo': estado_nuevo,
            'emisor': emisor
        }
        
        self.notify(event)


# Instancia global del Subject (Singleton pattern)
_orden_trabajo_subject = None


def get_orden_trabajo_subject() -> OrdenTrabajoSubject:
    """
    Obtiene la instancia global del Subject (Singleton).
    Registra automáticamente los observadores por defecto.
    
    Returns:
        Instancia de OrdenTrabajoSubject con observadores registrados
    """
    global _orden_trabajo_subject
    
    if _orden_trabajo_subject is None:
        _orden_trabajo_subject = OrdenTrabajoSubject()
        
        # Registrar observadores por defecto
        _orden_trabajo_subject.attach(MecanicoObserver())
        _orden_trabajo_subject.attach(EncargadoObserver())
        _orden_trabajo_subject.attach(RecepcionistaObserver())
    
    return _orden_trabajo_subject

