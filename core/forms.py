from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import (
    Cliente, Vehiculo, MarcaVehiculo, ModeloVehiculo,
    OrdenTrabajo, BitacoraTrabajo, Repuesto, Herramienta,
    ControlCalidad, Notificacion, Mecanico, EspecialidadMecanico,
    ZonaTrabajo
)
from .validators import validar_rut_chileno, validar_patente_chilena
from .models import RolUsuario


class RegistroUsuarioForm(UserCreationForm):
    """Formulario de registro de usuario con rol."""
    nombre = forms.CharField(max_length=150, required=True, label="Nombre")
    apellido = forms.CharField(max_length=150, required=True, label="Apellido")
    rol = forms.ChoiceField(choices=RolUsuario.choices, required=True, label="Rol")

    class Meta:
        model = User
        fields = ("username", "password1", "password2", "nombre", "apellido", "rol")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Usuario"
        self.fields['password1'].label = "Contraseña"
        self.fields['password2'].label = "Repita la contraseña"
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None


class RegistrarSolicitudForm(forms.Form):
    """Formulario para registrar solicitud de trabajo."""
    # Datos del Cliente
    rut = forms.CharField(max_length=12, validators=[validar_rut_chileno], label="RUT")
    nombre = forms.CharField(max_length=150, label="Nombre")
    telefono = forms.CharField(max_length=20, label="Teléfono")
    email = forms.EmailField(required=False, label="Email", error_messages={'invalid': 'Ingrese una dirección de correo electrónico válida.'})

    # Datos del Vehículo
    patente = forms.CharField(max_length=10, validators=[validar_patente_chilena], label="Patente")
    marca = forms.ModelChoiceField(queryset=MarcaVehiculo.objects.all(), label="Marca")
    modelo = forms.ModelChoiceField(queryset=ModeloVehiculo.objects.none(), label="Modelo")
    anio = forms.IntegerField(min_value=1900, max_value=2100, label="Año")
    kilometraje = forms.IntegerField(min_value=0, label="Kilometraje")

    # Solicitud
    motivo = forms.CharField(max_length=200, label="Motivo de ingreso")
    descripcion = forms.CharField(widget=forms.Textarea, label="Descripción del problema")
    fecha = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Fecha de ingreso")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'marca' in self.data:
            try:
                marca_id = int(self.data.get('marca'))
                self.fields['modelo'].queryset = ModeloVehiculo.objects.filter(marca_id=marca_id)
            except (ValueError, TypeError):
                pass
        else:
            # Si no hay marca seleccionada, mostrar todos los modelos
            self.fields['modelo'].queryset = ModeloVehiculo.objects.all()


class AsignarOTForm(forms.Form):
    """Formulario para asignar mecánico y zona a una OT."""
    mecanico = forms.ModelChoiceField(queryset=Mecanico.objects.all(), label="Mecánico")
    zona = forms.ModelChoiceField(queryset=None, label="Zona de trabajo")
    fecha_estimada = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), label="Fecha estimada de entrega")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['zona'].queryset = ZonaTrabajo.objects.filter(activa=True)


class BitacoraForm(forms.ModelForm):
    """Formulario para registrar bitácora."""
    imagenes = forms.FileField(
        required=False,
        label="Fotos (múltiples)",
        help_text="Puedes seleccionar múltiples archivos"
    )
    solicitud_cambio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label="Solicitud de cambio (opcional)"
    )

    class Meta:
        model = BitacoraTrabajo
        fields = ("descripcion", "tiempo_ejecucion_minutos", "estado_avance")
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 5}),
            "tiempo_ejecucion_minutos": forms.NumberInput(attrs={"min": 0}),
        }


class ControlCalidadForm(forms.ModelForm):
    """Formulario para control de calidad."""
    class Meta:
        model = ControlCalidad
        fields = (
            "resultado", "observaciones_generales",
            "prueba_ruta_ok", "fluidos_verificados",
            "luces_sistema_electrico_ok", "herramientas_retiradas",
            "vehiculo_limpio"
        )
        widgets = {
            "observaciones_generales": forms.Textarea(attrs={"rows": 4}),
        }


class EditarRepuestoForm(forms.ModelForm):
    """Formulario para editar repuesto."""
    class Meta:
        model = Repuesto
        fields = ("nombre", "descripcion", "precio_venta", "marca")
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "precio_venta": forms.NumberInput(attrs={"min": 0}),
        }


class MovimientoRepuestoForm(forms.Form):
    """Formulario para movimiento de stock."""
    tipo = forms.ChoiceField(
        choices=[("entrada", "Entrada"), ("salida", "Salida")],
        label="Tipo de movimiento"
    )
    cantidad = forms.IntegerField(min_value=1, label="Cantidad")


class EditarHerramientaForm(forms.ModelForm):
    """Formulario para editar herramienta."""
    class Meta:
        model = Herramienta
        fields = ("nombre", "descripcion", "estado")
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
        }

