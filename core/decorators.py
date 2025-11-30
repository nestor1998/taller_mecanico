"""
Decoradores personalizados para el sistema de taller mecánico.
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import PerfilUsuario


def requiere_perfil_usuario(view_func):
    """
    Decorador que verifica que el usuario tenga un PerfilUsuario asociado.
    Si no lo tiene, redirige al login o muestra un error.
    IMPORTANTE: No ejecuta lógica específica de roles, solo verifica que exista el perfil.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Verificar autenticación primero
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Verificar que tenga perfil
        try:
            perfil = request.user.perfilusuario
        except (PerfilUsuario.DoesNotExist, AttributeError):
            messages.error(
                request,
                "Tu cuenta no tiene un perfil asociado. Por favor, contacta al administrador."
            )
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def requiere_rol(*roles_permitidos):
    """
    Decorador que verifica que el usuario tenga uno de los roles permitidos.
    Uso: @requiere_rol('ENCARGADO_TALLER', 'RECEPCIONISTA')
    IMPORTANTE: Este decorador NO ejecuta lógica específica de roles (como buscar Mecanico).
    Solo verifica el rol del perfil.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Verificar autenticación primero
            if not request.user.is_authenticated:
                return redirect('login')
            
            # Verificar que tenga perfil y rol correcto
            try:
                perfil = request.user.perfilusuario
                if perfil.rol not in roles_permitidos:
                    messages.error(request, "No tienes permisos para acceder a esta página.")
                    return redirect('dashboard')
            except (PerfilUsuario.DoesNotExist, AttributeError):
                messages.error(
                    request,
                    "Tu cuenta no tiene un perfil asociado. Por favor, contacta al administrador."
                )
                return redirect('login')
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    return decorator

