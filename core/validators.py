"""
Validadores personalizados para el sistema de taller mecánico.
"""
import re
from django.core.exceptions import ValidationError


def validar_rut_chileno(value):
    """
    Valida RUT chileno con formato: 12345678-9 o 12.345.678-9
    """
    if not value:
        return

    # Limpiar el RUT
    rut_limpio = value.replace(".", "").replace("-", "").upper()

    if len(rut_limpio) < 8 or len(rut_limpio) > 9:
        raise ValidationError("RUT inválido")

    # Separar número y dígito verificador
    if len(rut_limpio) == 9:
        numero = rut_limpio[:-1]
        dv = rut_limpio[-1]
    else:
        numero = rut_limpio[:-1]
        dv = rut_limpio[-1]

    # Validar que el número sea numérico
    if not numero.isdigit():
        raise ValidationError("RUT inválido")

    # Validar dígito verificador
    if dv not in "0123456789K":
        raise ValidationError("RUT inválido")

    # Calcular dígito verificador
    multiplicadores = [2, 3, 4, 5, 6, 7, 2, 3]
    suma = 0
    numero_reverso = numero[::-1]

    for i, digito in enumerate(numero_reverso):
        suma += int(digito) * multiplicadores[i % 8]

    resto = suma % 11
    dv_calculado = 11 - resto

    if dv_calculado == 11:
        dv_calculado = "0"
    elif dv_calculado == 10:
        dv_calculado = "K"
    else:
        dv_calculado = str(dv_calculado)

    if dv != dv_calculado:
        raise ValidationError("RUT inválido")


def validar_patente_chilena(value):
    """
    Valida patente chilena: formato antiguo (ABCD12) o nuevo (ABCD12 o AB1234)
    """
    if not value:
        return

    # Normalizar: quitar espacios y convertir a mayúsculas
    patente = value.replace(" ", "").upper()

    # Formato antiguo: 4 letras + 2 números (ej: ABCD12)
    patron_antiguo = re.compile(r'^[A-Z]{4}\d{2}$')
    # Formato nuevo: 2 letras + 4 números (ej: AB1234)
    patron_nuevo = re.compile(r'^[A-Z]{2}\d{4}$')

    if not (patron_antiguo.match(patente) or patron_nuevo.match(patente)):
        raise ValidationError(
            "La patente debe tener formato antiguo (ABCD12) o nuevo (AB1234)."
        )


def validar_fecha_no_futura(value):
    """Valida que la fecha no sea futura."""
    from django.utils import timezone
    if value > timezone.now().date():
        raise ValidationError("La fecha no puede ser futura.")


def validar_fecha_no_pasada(value):
    """Valida que la fecha no sea muy antigua (más de 100 años)."""
    from datetime import date, timedelta
    if value < date.today() - timedelta(days=36500):
        raise ValidationError("La fecha es demasiado antigua.")


def validar_fecha_estimada_mayor_ingreso(fecha_estimada, fecha_ingreso):
    """Valida que la fecha estimada sea mayor que la fecha de ingreso."""
    if fecha_estimada and fecha_ingreso:
        if fecha_estimada < fecha_ingreso:
            raise ValidationError("La fecha estimada de entrega debe ser posterior a la fecha de ingreso.")


def validar_stock_no_negativo(value):
    """Valida que el stock no sea negativo."""
    if value < 0:
        raise ValidationError("El stock no puede ser negativo.")


def validar_kilometraje_positivo(value):
    """Valida que el kilometraje sea positivo."""
    if value < 0:
        raise ValidationError("El kilometraje debe ser un número positivo.")

