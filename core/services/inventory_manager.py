"""
Inventory Manager - Servicio para gestión de inventario.

Implementa Inyección de Dependencias según la documentación:
"Vista de Asignación de Servicio recibiendo un Inventory Manager inyectado 
para realizar verificación de stock antes de asignar trabajo."
"""
from typing import Optional, List
from django.core.exceptions import ValidationError

from ..models import Repuesto, Notificacion, PerfilUsuario, TipoNotificacion
from django.utils import timezone
from datetime import timedelta


class InventoryManager:
    """
    Manager para gestión de inventario.
    Permite verificar stock, gestionar movimientos y alertas.
    """
    
    def verificar_stock(self, repuesto_id: int, cantidad_requerida: int = 1) -> bool:
        """
        Verifica si hay stock suficiente de un repuesto.
        
        Args:
            repuesto_id: ID del repuesto
            cantidad_requerida: Cantidad requerida
            
        Returns:
            True si hay stock suficiente, False en caso contrario
            
        Raises:
            ValidationError: Si el repuesto no existe
        """
        try:
            repuesto = Repuesto.objects.get(id=repuesto_id)
            return repuesto.stock >= cantidad_requerida
        except Repuesto.DoesNotExist:
            raise ValidationError(f"Repuesto con ID {repuesto_id} no existe")
    
    def obtener_stock_disponible(self, repuesto_id: int) -> int:
        """
        Obtiene el stock disponible de un repuesto.
        
        Args:
            repuesto_id: ID del repuesto
            
        Returns:
            Cantidad de stock disponible
        """
        try:
            repuesto = Repuesto.objects.get(id=repuesto_id)
            return repuesto.stock
        except Repuesto.DoesNotExist:
            return 0
    
    def verificar_stock_bajo(self, umbral: int = 3) -> List[Repuesto]:
        """
        Obtiene lista de repuestos con stock bajo.
        
        Args:
            umbral: Umbral mínimo de stock (default: 3)
            
        Returns:
            Lista de repuestos con stock bajo
        """
        return list(Repuesto.objects.filter(stock__lt=umbral))
    
    def crear_alerta_stock_bajo(self, repuesto: Repuesto, emisor: PerfilUsuario) -> Optional[Notificacion]:
        """
        Crea una alerta de stock bajo si no existe una reciente.
        
        Args:
            repuesto: Repuesto con stock bajo
            emisor: PerfilUsuario que genera la alerta
            
        Returns:
            Notificacion creada o None si ya existe una reciente
        """
        # Verificar si ya existe una notificación reciente (últimas 24 horas)
        hace_24h = timezone.now() - timedelta(hours=24)
        
        if Notificacion.objects.filter(
            tipo=TipoNotificacion.MENSAJE_GENERAL,
            orden__isnull=True,
            mensaje__contains=f"Repuesto {repuesto.nombre} bajo en stock",
            creada_en__gte=hace_24h
        ).exists():
            return None
        
        # Buscar perfil del encargado
        perfil_encargado = PerfilUsuario.objects.filter(
            rol="ENCARGADO_TALLER"
        ).first()
        
        if not perfil_encargado:
            return None
        
        return Notificacion.objects.create(
            tipo=TipoNotificacion.MENSAJE_GENERAL,
            orden=None,
            mensaje=f"Repuesto {repuesto.nombre} bajo en stock (solo {repuesto.stock} unidades).",
            emisor=emisor,
            receptor=perfil_encargado
        )
    
    def realizar_movimiento_stock(
        self, 
        repuesto_id: int, 
        tipo: str, 
        cantidad: int
    ):
        """
        Realiza un movimiento de stock (entrada o salida).
        
        Args:
            repuesto_id: ID del repuesto
            tipo: 'entrada' o 'salida'
            cantidad: Cantidad a mover
            
        Returns:
            Tupla (éxito, mensaje)
        """
        try:
            repuesto = Repuesto.objects.get(id=repuesto_id)
            
            if tipo == 'entrada':
                repuesto.stock += cantidad
                repuesto.save()
                return True, f"Entrada de {cantidad} unidades registrada."
            
            elif tipo == 'salida':
                if repuesto.stock < cantidad:
                    return False, f"No hay suficiente stock. Disponible: {repuesto.stock}"
                
                repuesto.stock -= cantidad
                repuesto.save()
                return True, f"Salida de {cantidad} unidades registrada."
            
            else:
                return False, f"Tipo de movimiento inválido: {tipo}"
                
        except Repuesto.DoesNotExist:
            return False, f"Repuesto con ID {repuesto_id} no existe"

