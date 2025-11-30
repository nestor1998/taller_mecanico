"""
Suite completa de tests para el sistema de taller mecánico.
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta

from .models import (
    PerfilUsuario, RolUsuario, Cliente, Vehiculo, MarcaVehiculo, ModeloVehiculo,
    OrdenTrabajo, EstadoOT, BitacoraTrabajo, FotoBitacora,
    Repuesto, Herramienta, Mecanico, EspecialidadMecanico, ZonaTrabajo,
    ControlCalidad, Notificacion, Proveedor
)


class BaseTestCase(TestCase):
    """Clase base para tests con datos comunes."""
    
    def setUp(self):
        """Configuración inicial para todos los tests."""
        # Crear usuarios y perfiles
        self.user_recepcionista = User.objects.create_user(
            username="recepcionista",
            password="test123"
        )
        self.perfil_recepcionista = PerfilUsuario.objects.create(
            usuario=self.user_recepcionista,
            rol=RolUsuario.RECEPCIONISTA
        )
        
        self.user_encargado = User.objects.create_user(
            username="encargado",
            password="test123"
        )
        self.perfil_encargado = PerfilUsuario.objects.create(
            usuario=self.user_encargado,
            rol=RolUsuario.ENCARGADO_TALLER
        )
        
        self.user_mecanico = User.objects.create_user(
            username="mecanico",
            password="test123"
        )
        self.perfil_mecanico = PerfilUsuario.objects.create(
            usuario=self.user_mecanico,
            rol=RolUsuario.MECANICO
        )
        
        self.user_bodega = User.objects.create_user(
            username="bodega",
            password="test123"
        )
        self.perfil_bodega = PerfilUsuario.objects.create(
            usuario=self.user_bodega,
            rol=RolUsuario.ENCARGADO_BODEGA
        )
        
        # Crear datos básicos
        self.marca = MarcaVehiculo.objects.create(nombre="Toyota")
        self.modelo = ModeloVehiculo.objects.create(marca=self.marca, nombre="Corolla")
        
        self.cliente = Cliente.objects.create(
            rut="12345678-9",
            nombre="Juan Pérez",
            telefono="123456789"
        )
        
        self.vehiculo = Vehiculo.objects.create(
            cliente=self.cliente,
            patente="ABCD12",
            marca=self.marca,
            modelo=self.modelo,
            anio=2020,
            kilometraje=50000
        )
        
        self.estado_pendiente = EstadoOT.objects.create(nombre="PENDIENTE")
        self.estado_en_progreso = EstadoOT.objects.create(nombre="EN_PROGRESO")
        self.estado_finalizado = EstadoOT.objects.create(nombre="FINALIZADO")
        
        self.especialidad = EspecialidadMecanico.objects.create(nombre="Motor")
        self.mecanico_obj = Mecanico.objects.create(
            nombre="mecanico",
            especialidad=self.especialidad
        )
        
        self.zona = ZonaTrabajo.objects.create(nombre="Zona 1", capacidad=5)
        
        self.proveedor = Proveedor.objects.create(nombre="Proveedor Test")
        
        self.repuesto = Repuesto.objects.create(
            codigo="REP001",
            nombre="Filtro de aceite",
            stock=10,
            precio_compra=5000,
            precio_venta=8000,
            fecha_ingreso=date.today(),
            proveedor=self.proveedor
        )
        
        self.herramienta = Herramienta.objects.create(
            codigo="HER001",
            nombre="Llave inglesa",
            cantidad=1,
            ubicacion_fisica="Estante A",
            fecha_adquisicion=date.today()
        )


class LoginTests(BaseTestCase):
    """Tests para login y autenticación."""
    
    def test_login_exitoso(self):
        """Test de login exitoso."""
        client = Client()
        response = client.post(reverse('login'), {
            'username': 'recepcionista',
            'password': 'test123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(response.url, reverse('dashboard'))
    
    def test_login_fallido(self):
        """Test de login con credenciales incorrectas."""
        client = Client()
        response = client.post(reverse('login'), {
            'username': 'recepcionista',
            'password': 'wrong'
        })
        self.assertEqual(response.status_code, 200)  # No redirect
    
    def test_logout(self):
        """Test de logout."""
        client = Client()
        client.login(username='recepcionista', password='test123')
        response = client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))


class RegistroTests(BaseTestCase):
    """Tests para registro de usuario."""
    
    def test_registro_exitoso(self):
        """Test de registro exitoso."""
        client = Client()
        response = client.post(reverse('registro'), {
            'username': 'nuevo_usuario',
            'password1': 'test123456',
            'password2': 'test123456',
            'nombre': 'Nuevo Usuario',
            'rol': RolUsuario.RECEPCIONISTA
        })
        self.assertEqual(response.status_code, 302)  # Redirect a login
        
        # Verificar que se creó el usuario
        self.assertTrue(User.objects.filter(username='nuevo_usuario').exists())
        
        # Verificar que se creó el perfil
        user = User.objects.get(username='nuevo_usuario')
        self.assertTrue(PerfilUsuario.objects.filter(usuario=user).exists())
    
    def test_registro_mecanico_crea_mecanico(self):
        """Test que al registrar un mecánico se crea entrada en Mecanico."""
        client = Client()
        response = client.post(reverse('registro'), {
            'username': 'nuevo_mecanico',
            'password1': 'test123456',
            'password2': 'test123456',
            'nombre': 'Nuevo Mecánico',
            'rol': RolUsuario.MECANICO
        })
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se creó el mecánico
        self.assertTrue(Mecanico.objects.filter(nombre='Nuevo Mecánico').exists())


class DashboardTests(BaseTestCase):
    """Tests para dashboards por rol."""
    
    def test_dashboard_recepcionista(self):
        """Test dashboard de recepcionista."""
        client = Client()
        client.login(username='recepcionista', password='test123')
        response = client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Recepcionista')
    
    def test_dashboard_encargado(self):
        """Test dashboard de encargado."""
        client = Client()
        client.login(username='encargado', password='test123')
        response = client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Encargado')
    
    def test_dashboard_mecanico(self):
        """Test dashboard de mecánico."""
        client = Client()
        client.login(username='mecanico', password='test123')
        response = client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mecánico')
    
    def test_dashboard_bodega(self):
        """Test dashboard de encargado de bodega."""
        client = Client()
        client.login(username='bodega', password='test123')
        response = client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bodega')


class RegistrarSolicitudTests(BaseTestCase):
    """Tests para registrar solicitud."""
    
    def test_registrar_solicitud_exitoso(self):
        """Test de registro exitoso de solicitud."""
        client = Client()
        client.login(username='recepcionista', password='test123')
        
        # RUT válido: 98765432-5 (según el validador)
        response = client.post(reverse('registrar_solicitud'), {
            'rut': '98765432-5',
            'nombre': 'María González',
            'telefono': '987654321',
            'email': 'maria@test.com',
            'patente': 'EFGH34',
            'marca': self.marca.id,
            'modelo': self.modelo.id,
            'anio': 2021,
            'kilometraje': 30000,
            'motivo': 'Mantención',
            'descripcion': 'Cambio de aceite',
            'fecha': date.today()
        })
        
        # Si hay errores en el formulario, mostrar el contenido de la respuesta
        if response.status_code != 302:
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.content.decode()}")
        
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verificar que se creó la OT
        self.assertTrue(OrdenTrabajo.objects.filter(
            vehiculo__patente='EFGH34'
        ).exists())
    
    def test_registrar_solicitud_sin_permiso(self):
        """Test que un usuario sin permiso no puede registrar solicitud."""
        client = Client()
        client.login(username='mecanico', password='test123')
        response = client.get(reverse('registrar_solicitud'))
        self.assertEqual(response.status_code, 302)  # Redirect a dashboard


class AsignacionOTTests(BaseTestCase):
    """Tests para asignación de OT."""
    
    def setUp(self):
        super().setUp()
        self.ot = OrdenTrabajo.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            estado=self.estado_pendiente,
            motivo_ingreso="Reparación",
            descripcion_problema="Problema en motor",
            fecha_ingreso=date.today()
        )
    
    def test_asignar_ot_exitoso(self):
        """Test de asignación exitosa de OT."""
        client = Client()
        client.login(username='encargado', password='test123')
        
        fecha_estimada = date.today() + timedelta(days=5)
        response = client.post(reverse('detalle_ot', args=[self.ot.id]), {
            'mecanico': self.mecanico_obj.id,
            'zona': self.zona.id,
            'fecha_estimada': fecha_estimada
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verificar que se asignó
        self.ot.refresh_from_db()
        self.assertEqual(self.ot.mecanico, self.mecanico_obj)
        self.assertEqual(self.ot.zona_trabajo, self.zona)
        self.assertEqual(self.ot.estado.nombre, "EN_PROGRESO")


class BitacoraTests(BaseTestCase):
    """Tests para bitácoras."""
    
    def setUp(self):
        super().setUp()
        self.ot = OrdenTrabajo.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            estado=self.estado_en_progreso,
            mecanico=self.mecanico_obj,
            motivo_ingreso="Reparación",
            descripcion_problema="Problema en motor",
            fecha_ingreso=date.today()
        )
    
    def test_registrar_bitacora_exitoso(self):
        """Test de registro exitoso de bitácora."""
        client = Client()
        client.login(username='mecanico', password='test123')
        
        response = client.post(reverse('registrar_bitacora', args=[self.ot.id]), {
            'descripcion': 'Cambio de aceite realizado',
            'tiempo_ejecucion_minutos': 30,
            'estado_avance': 'FINALIZADO'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verificar que se creó la bitácora
        self.assertTrue(BitacoraTrabajo.objects.filter(
            orden=self.ot,
            descripcion='Cambio de aceite realizado'
        ).exists())


class InventarioTests(BaseTestCase):
    """Tests para inventario."""
    
    def test_ver_inventario(self):
        """Test de visualización de inventario."""
        client = Client()
        client.login(username='bodega', password='test123')
        response = client.get(reverse('inventario'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Filtro de aceite')
    
    def test_editar_repuesto(self):
        """Test de edición de repuesto."""
        client = Client()
        client.login(username='bodega', password='test123')
        
        response = client.post(reverse('editar_repuesto', args=[self.repuesto.id]), {
            'nombre': 'Filtro de aceite actualizado',
            'descripcion': 'Nueva descripción',
            'precio_venta': 9000,
            'marca': 'Toyota'
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verificar cambios
        self.repuesto.refresh_from_db()
        self.assertEqual(self.repuesto.nombre, 'Filtro de aceite actualizado')
    
    def test_movimiento_repuesto_entrada(self):
        """Test de movimiento de entrada de repuesto."""
        client = Client()
        client.login(username='bodega', password='test123')
        
        stock_inicial = self.repuesto.stock
        response = client.post(reverse('movimiento_repuesto', args=[self.repuesto.id]), {
            'tipo': 'entrada',
            'cantidad': 5
        })
        
        self.assertEqual(response.status_code, 302)
        
        self.repuesto.refresh_from_db()
        self.assertEqual(self.repuesto.stock, stock_inicial + 5)
    
    def test_movimiento_repuesto_salida_sin_stock(self):
        """Test de movimiento de salida sin stock suficiente."""
        client = Client()
        client.login(username='bodega', password='test123')
        
        self.repuesto.stock = 2
        self.repuesto.save()
        
        response = client.post(reverse('movimiento_repuesto', args=[self.repuesto.id]), {
            'tipo': 'salida',
            'cantidad': 10
        })
        
        # Debe mostrar error
        self.assertEqual(response.status_code, 200)  # No redirect


class ControlCalidadTests(BaseTestCase):
    """Tests para control de calidad."""
    
    def setUp(self):
        super().setUp()
        self.ot = OrdenTrabajo.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            estado=self.estado_en_progreso,
            mecanico=self.mecanico_obj,
            motivo_ingreso="Reparación",
            descripcion_problema="Problema en motor",
            fecha_ingreso=date.today()
        )
    
    def test_control_calidad_aprobado(self):
        """Test de control de calidad aprobado."""
        client = Client()
        client.login(username='encargado', password='test123')
        
        response = client.post(reverse('control_calidad', args=[self.ot.id]), {
            'resultado': 'APROBADO',
            'observaciones_generales': 'Todo correcto',
            'prueba_ruta_ok': True,
            'fluidos_verificados': True,
            'luces_sistema_electrico_ok': True,
            'herramientas_retiradas': True,
            'vehiculo_limpio': True
        })
        
        self.assertEqual(response.status_code, 302)  # Redirect
        
        # Verificar que se creó el control
        self.assertTrue(ControlCalidad.objects.filter(orden=self.ot).exists())
        
        # Verificar que la OT cambió a FINALIZADO
        self.ot.refresh_from_db()
        self.assertEqual(self.ot.estado.nombre, "FINALIZADO")


class NotificacionesTests(BaseTestCase):
    """Tests para notificaciones."""
    
    def test_ver_notificaciones(self):
        """Test de visualización de notificaciones."""
        # Crear notificación
        Notificacion.objects.create(
            tipo="MENSAJE_GENERAL",
            orden=None,
            mensaje="Test notification",
            receptor=self.perfil_recepcionista
        )
        
        client = Client()
        client.login(username='recepcionista', password='test123')
        response = client.get(reverse('notificaciones'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test notification')
    
    def test_marcar_notificacion_leida(self):
        """Test de marcar notificación como leída."""
        notif = Notificacion.objects.create(
            tipo="MENSAJE_GENERAL",
            orden=None,
            mensaje="Test notification",
            receptor=self.perfil_recepcionista
        )
        
        client = Client()
        client.login(username='recepcionista', password='test123')
        response = client.get(reverse('notificacion_leida', args=[notif.id]))
        self.assertEqual(response.status_code, 302)
        
        notif.refresh_from_db()
        self.assertTrue(notif.leida)


class ValidacionesTests(BaseTestCase):
    """Tests para validaciones."""
    
    def test_validar_rut_chileno(self):
        """Test de validación de RUT chileno."""
        from .validators import validar_rut_chileno
        from django.core.exceptions import ValidationError
        
        # RUT válido (12345678-5 es un RUT válido según el algoritmo)
        try:
            validar_rut_chileno("12345678-5")
        except ValidationError:
            self.fail("RUT válido no debería lanzar error")
        
        # RUT inválido
        with self.assertRaises(ValidationError):
            validar_rut_chileno("12345678-0")
    
    def test_validar_patente_chilena(self):
        """Test de validación de patente chilena."""
        from .validators import validar_patente_chilena
        from django.core.exceptions import ValidationError
        
        # Patente válida (formato antiguo)
        try:
            validar_patente_chilena("ABCD12")
        except ValidationError:
            self.fail("Patente válida no debería lanzar error")
        
        # Patente válida (formato nuevo)
        try:
            validar_patente_chilena("AB1234")
        except ValidationError:
            self.fail("Patente válida no debería lanzar error")
        
        # Patente inválida
        with self.assertRaises(ValidationError):
            validar_patente_chilena("ABC123")


class HerramientasTests(BaseTestCase):
    """Tests para herramientas."""
    
    def test_ver_herramientas(self):
        """Test de visualización de herramientas."""
        client = Client()
        client.login(username='bodega', password='test123')
        response = client.get(reverse('herramientas'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Llave inglesa')
    
    def test_retirar_herramienta(self):
        """Test de retiro de herramienta."""
        client = Client()
        client.login(username='mecanico', password='test123')
        
        # Crear OT activa
        ot = OrdenTrabajo.objects.create(
            cliente=self.cliente,
            vehiculo=self.vehiculo,
            estado=self.estado_en_progreso,
            mecanico=self.mecanico_obj,
            motivo_ingreso="Reparación",
            descripcion_problema="Problema",
            fecha_ingreso=date.today()
        )
        
        response = client.get(reverse('retirar_herramienta', args=[self.herramienta.id]))
        self.assertEqual(response.status_code, 302)  # Redirect
        
        self.herramienta.refresh_from_db()
        self.assertEqual(self.herramienta.estado, "EN_MANTENCION")
    
    def test_devolver_herramienta(self):
        """Test de devolución de herramienta."""
        # Primero retirar
        self.herramienta.estado = "EN_MANTENCION"
        self.herramienta.responsable_asignado = self.mecanico_obj
        self.herramienta.save()
        
        client = Client()
        client.login(username='mecanico', password='test123')
        response = client.get(reverse('devolver_herramienta', args=[self.herramienta.id]))
        self.assertEqual(response.status_code, 302)
        
        self.herramienta.refresh_from_db()
        self.assertEqual(self.herramienta.estado, "OPERATIVA")
