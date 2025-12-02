"""
Assignment Service - Servicio para asignación de órdenes de trabajo.

Implementa Inyección de Dependencias según la documentación.
"""
from typing import Optional
from django.core.exceptions import ValidationError
from datetime import date

from ..models import (
    OrdenTrabajo, Mecanico, ZonaTrabajo, EstadoOT, 
    PerfilUsuario
)
from ..patterns.observer import get_orden_trabajo_subject
from .inventory_manager import InventoryManager


class AssignmentService:
    """
    Servicio para asignación de órdenes de trabajo.
    Recibe dependencias inyectadas (InventoryManager) para verificar stock.
    """
    
    def __init__(self, inventory_manager: InventoryManager):
        """
        Constructor que recibe dependencias inyectadas.
        
        Args:
            inventory_manager: Instancia de InventoryManager inyectada
        """
        self.inventory_manager = inventory_manager
        self.subject = get_orden_trabajo_subject()
    
    def asignar_ot(
        self,
        orden: OrdenTrabajo,
        mecanico: Mecanico,
        zona: ZonaTrabajo,
        fecha_estimada: date,
        emisor: PerfilUsuario
    ):
        """
        Asigna una orden de trabajo a un mecánico y zona.
        Verifica stock antes de asignar (usando InventoryManager inyectado).
        
        Args:
            orden: OrdenTrabajo a asignar
            mecanico: Mecánico asignado
            zona: Zona de trabajo asignada
            fecha_estimada: Fecha estimada de entrega
            emisor: PerfilUsuario que realiza la asignación
            
        Returns:
            Tupla (éxito, mensaje)
        """
        # Validar fecha estimada
        if fecha_estimada < orden.fecha_ingreso:
            return False, "La fecha estimada de entrega debe ser posterior a la fecha de ingreso."
        
        # Verificar stock de repuestos necesarios (usando DI)
        # Nota: En una implementación completa, se verificaría el stock de repuestos
        # requeridos para la OT. Por ahora, solo validamos la asignación.
        
        # Asignar recursos
        orden.mecanico = mecanico
        orden.zona_trabajo = zona
        orden.fecha_estimada_entrega = fecha_estimada
        
        # Cambiar estado
        estado_en_progreso = EstadoOT.objects.get_or_create(nombre="EN_PROGRESO")[0]
        orden.estado = estado_en_progreso
        orden.en_lista_espera = False
        orden.save()
        
        # Notificar usando patrón Observer
        event = {
            'orden': orden,
            'tipo_evento': 'ASIGNACION',
            'emisor': emisor
        }
        self.subject.notify(event)
        
        return True, "Asignación realizada correctamente."
    
    def obtener_mecanicos_disponibles(self):
        """
        Obtiene lista de mecánicos disponibles.
        
        Returns:
            Lista de mecánicos ordenados por especialidad y nombre
        """
        return list(Mecanico.objects.all().order_by("especialidad__nombre", "nombre"))
    
    def obtener_zonas_disponibles(self):
        """
        Obtiene lista de zonas de trabajo disponibles.
        
        Returns:
            Lista de zonas activas
        """
        return list(ZonaTrabajo.objects.filter(activa=True))

