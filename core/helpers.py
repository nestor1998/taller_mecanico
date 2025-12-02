"""
Funciones helper para el sistema de taller mecánico.
"""
from .models import Mecanico, PerfilUsuario


def obtener_mecanico_desde_usuario(user):
    """
    Obtiene el objeto Mecanico asociado a un usuario de forma segura.
    
    Busca el Mecanico por el nombre completo del usuario (first_name + last_name).
    Si no existe, lo crea automáticamente para evitar errores.
    
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
    
    # Si no hay nombre completo, usar username como fallback
    if not nombre_completo or nombre_completo == "":
        nombre_completo = user.username
    
    # Buscar el mecánico
    mecanico = Mecanico.objects.filter(nombre=nombre_completo).first()
    
    # Si no existe, crearlo automáticamente
    if not mecanico:
        from .models import EspecialidadMecanico
        # Obtener o crear especialidad por defecto
        especialidad_default, _ = EspecialidadMecanico.objects.get_or_create(
            nombre="General"
        )
        mecanico = Mecanico.objects.create(
            nombre=nombre_completo,
            especialidad=especialidad_default
        )
    
    return mecanico

