"""
Context processors para el sistema de taller mecánico.
"""
from .models import PerfilUsuario


def notificaciones(request):
    """
    Context processor que agrega el contador de notificaciones no leídas
    a todos los templates.
    IMPORTANTE: Maneja casos donde el usuario no tiene perfil sin lanzar errores.
    """
    context = {
        'notif_no_leidas': 0,
    }
    
    if request.user.is_authenticated:
        try:
            perfil = request.user.perfilusuario
            context['notif_no_leidas'] = perfil.notificaciones_recibidas.filter(leida=False).count()
        except (PerfilUsuario.DoesNotExist, AttributeError):
            # Usuario autenticado pero sin perfil - no es un error crítico en el context processor
            pass
    
    return context

