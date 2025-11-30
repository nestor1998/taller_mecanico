"""
Funciones helper para el sistema de taller mecánico.
"""
from .models import Mecanico, PerfilUsuario


def obtener_mecanico_desde_usuario(user):
    """
    Obtiene el objeto Mecanico asociado a un usuario de forma segura.
    
    Busca el Mecanico por el nombre completo del usuario (first_name + last_name).
    Retorna None si no se encuentra o si el usuario no es mecánico.
    
    Args:
        user: Usuario de Django
        
    Returns:
        Mecanico o None
    """
    if not user or not user.is_authenticated:
        return None
    
    try:
        perfil = user.perfilusuario
        if perfil.rol != "MECANICO":
            return None
    except PerfilUsuario.DoesNotExist:
        return None
    
    # Buscar por nombre completo
    nombre_completo = f"{user.first_name} {user.last_name}".strip()
    if nombre_completo:
        mecanico = Mecanico.objects.filter(nombre=nombre_completo).first()
        if mecanico:
            return mecanico
    
    # Fallback: buscar por username si el nombre no coincide
    # Esto es para compatibilidad con datos existentes
    mecanico = Mecanico.objects.filter(nombre=user.username).first()
    return mecanico

