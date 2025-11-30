"""
Comando Django para poblar la base de datos con datos de prueba realistas.
Uso: python manage.py seed
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import date, timedelta
import random
import string

from core.models import (
    PerfilUsuario, RolUsuario,
    Cliente, Vehiculo, MarcaVehiculo, ModeloVehiculo,
    OrdenTrabajo, EstadoOT, BitacoraTrabajo, FotoBitacora,
    Repuesto, Herramienta, HerramientaEnUso, Mecanico, EspecialidadMecanico,
    ZonaTrabajo, ControlCalidad, Notificacion, Proveedor, Servicio
)


def calcular_digito_verificador_rut(rut_numero):
    """Calcula el dígito verificador de un RUT chileno."""
    multiplicadores = [2, 3, 4, 5, 6, 7, 2, 3]
    suma = 0
    rut_reverso = str(rut_numero)[::-1]
    
    for i, digito in enumerate(rut_reverso):
        suma += int(digito) * multiplicadores[i % 8]
    
    resto = suma % 11
    dv = 11 - resto
    
    if dv == 11:
        return "0"
    elif dv == 10:
        return "K"
    else:
        return str(dv)


def generar_rut_chileno():
    """Genera un RUT chileno válido."""
    numero = random.randint(10000000, 25000000)
    dv = calcular_digito_verificador_rut(numero)
    return f"{numero}-{dv}"


def generar_patente_chilena():
    """Genera una patente chilena válida (formato antiguo o nuevo)."""
    if random.choice([True, False]):
        # Formato antiguo: ABCD12 (4 letras + 2 números)
        letras = ''.join(random.choices(string.ascii_uppercase, k=4))
        numeros = ''.join(random.choices(string.digits, k=2))
        return f"{letras}{numeros}"
    else:
        # Formato nuevo: AB1234 (2 letras + 4 números)
        letras = ''.join(random.choices(string.ascii_uppercase, k=2))
        numeros = ''.join(random.choices(string.digits, k=4))
        return f"{letras}{numeros}"


class Command(BaseCommand):
    help = 'Pobla la base de datos con datos de prueba realistas'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Iniciando generación de datos de prueba...'))
        
        # Limpiar datos existentes (opcional, comentado para no borrar datos reales)
        # self._limpiar_datos()
        
        # 1. Crear usuarios y perfiles
        usuarios_creados = self._crear_usuarios()
        
        # 2. Crear datos base (marcas, modelos, especialidades, zonas, estados, proveedores, servicios)
        datos_base = self._crear_datos_base()
        
        # 3. Crear clientes y vehículos
        clientes_vehiculos = self._crear_clientes_vehiculos(datos_base)
        
        # 4. Crear órdenes de trabajo
        ots = self._crear_ordenes_trabajo(clientes_vehiculos, datos_base, usuarios_creados)
        
        # 5. Crear bitácoras
        self._crear_bitacoras(ots, usuarios_creados)
        
        # 6. Crear inventario (repuestos)
        repuestos = self._crear_repuestos(datos_base)
        
        # 7. Crear herramientas
        herramientas = self._crear_herramientas(usuarios_creados)
        
        # 8. Crear notificaciones
        self._crear_notificaciones(ots, usuarios_creados, repuestos)
        
        # 9. Crear controles de calidad
        self._crear_controles_calidad(ots, usuarios_creados)
        
        self.stdout.write(self.style.SUCCESS('\n✅ Datos de prueba generados correctamente.'))
        self.stdout.write(self.style.SUCCESS(f'   - {len(usuarios_creados["usuarios"])} usuarios creados'))
        self.stdout.write(self.style.SUCCESS(f'   - {len(clientes_vehiculos["clientes"])} clientes creados'))
        self.stdout.write(self.style.SUCCESS(f'   - {len(clientes_vehiculos["vehiculos"])} vehículos creados'))
        self.stdout.write(self.style.SUCCESS(f'   - {len(ots)} órdenes de trabajo creadas'))
        self.stdout.write(self.style.SUCCESS(f'   - {len(repuestos)} repuestos creados'))
        self.stdout.write(self.style.SUCCESS(f'   - {len(herramientas)} herramientas creadas'))

    def _crear_usuarios(self):
        """Crea usuarios con perfiles y mecánicos."""
        usuarios_creados = {
            'recepcionista': None,
            'encargado': None,
            'bodega': None,
            'mecanicos': [],
            'usuarios': []
        }
        
        # Recepcionista
        if not User.objects.filter(username='recepcion1').exists():
            user = User.objects.create_user(
                username='recepcion1',
                password='123',
                first_name='María',
                last_name='González',
                email='recepcion1@taller.com'
            )
            perfil = PerfilUsuario.objects.create(usuario=user, rol=RolUsuario.RECEPCIONISTA)
            usuarios_creados['recepcionista'] = user
            usuarios_creados['usuarios'].append(user)
            self.stdout.write(self.style.SUCCESS(f'  ✓ Usuario recepcion1 creado'))
        
        # Encargado de Taller
        if not User.objects.filter(username='encargado1').exists():
            user = User.objects.create_user(
                username='encargado1',
                password='123',
                first_name='Carlos',
                last_name='Rodríguez',
                email='encargado1@taller.com'
            )
            perfil = PerfilUsuario.objects.create(usuario=user, rol=RolUsuario.ENCARGADO_TALLER)
            usuarios_creados['encargado'] = user
            usuarios_creados['usuarios'].append(user)
            self.stdout.write(self.style.SUCCESS(f'  ✓ Usuario encargado1 creado'))
        
        # Encargado de Bodega
        if not User.objects.filter(username='bodega1').exists():
            user = User.objects.create_user(
                username='bodega1',
                password='123',
                first_name='Ana',
                last_name='Martínez',
                email='bodega1@taller.com'
            )
            perfil = PerfilUsuario.objects.create(usuario=user, rol=RolUsuario.ENCARGADO_BODEGA)
            usuarios_creados['bodega'] = user
            usuarios_creados['usuarios'].append(user)
            self.stdout.write(self.style.SUCCESS(f'  ✓ Usuario bodega1 creado'))
        
        # Mecánicos
        nombres_mecanicos = [
            ('Juan', 'Pérez', 'mecanico1'),
            ('Pedro', 'Sánchez', 'mecanico2'),
            ('Luis', 'Torres', 'mecanico3'),
        ]
        
        especialidades = EspecialidadMecanico.objects.all()
        if not especialidades.exists():
            especialidades = self._crear_especialidades()
        
        for i, (nombre, apellido, username) in enumerate(nombres_mecanicos):
            user, user_creado = User.objects.get_or_create(
                username=username,
                defaults={
                    'password': 'pbkdf2_sha256$600000$dummy$dummy=',  # Se cambiará después
                    'first_name': nombre,
                    'last_name': apellido,
                    'email': f'{username}@taller.com'
                }
            )
            
            if user_creado:
                user.set_password('123')
                user.save()
                perfil = PerfilUsuario.objects.create(usuario=user, rol=RolUsuario.MECANICO)
                self.stdout.write(self.style.SUCCESS(f'  ✓ Usuario {username} creado'))
            else:
                # Usuario ya existe, verificar que tenga perfil
                if not hasattr(user, 'perfilusuario'):
                    PerfilUsuario.objects.create(usuario=user, rol=RolUsuario.MECANICO)
            
            # Crear o obtener mecánico
            nombre_completo = f'{nombre} {apellido}'
            mecanico, mecanico_creado = Mecanico.objects.get_or_create(
                nombre=nombre_completo,
                defaults={
                    'especialidad': random.choice(especialidades),
                    'telefono': f'+569{random.randint(10000000, 99999999)}',
                    'cantidad_ayudantes': random.randint(0, 2)
                }
            )
            
            if mecanico_creado:
                self.stdout.write(self.style.SUCCESS(f'  ✓ Mecánico {nombre_completo} creado'))
            
            usuarios_creados['mecanicos'].append(mecanico)
            if user not in usuarios_creados['usuarios']:
                usuarios_creados['usuarios'].append(user)
        
        return usuarios_creados

    def _crear_especialidades(self):
        """Crea especialidades de mecánicos."""
        especialidades_nombres = [
            'Motor', 'Transmisión', 'Frenos', 'Suspensión y Dirección',
            'Escape', 'Eléctrico', 'Electrónico', 'Combustible', 'General'
        ]
        especialidades = []
        for nombre in especialidades_nombres:
            esp, _ = EspecialidadMecanico.objects.get_or_create(nombre=nombre)
            especialidades.append(esp)
        return especialidades

    def _crear_datos_base(self):
        """Crea marcas, modelos, zonas, estados, proveedores y servicios."""
        # Marcas y Modelos
        marcas_modelos = {
            'Toyota': ['Corolla', 'Camry', 'RAV4', 'Hilux', 'Yaris'],
            'Chevrolet': ['Spark', 'Cruze', 'Trailblazer', 'Silverado', 'Onix'],
            'Nissan': ['Versa', 'Sentra', 'Kicks', 'Frontier', 'X-Trail'],
            'Ford': ['Fiesta', 'Focus', 'Ranger', 'Explorer', 'EcoSport'],
            'Hyundai': ['Accent', 'Elantra', 'Tucson', 'Santa Fe', 'i10'],
            'Kia': ['Rio', 'Cerato', 'Sportage', 'Sorento', 'Picanto'],
            'Volkswagen': ['Polo', 'Golf', 'Amarok', 'Tiguan', 'Vento'],
            'Mazda': ['Mazda2', 'Mazda3', 'CX-5', 'CX-3', 'BT-50'],
        }
        
        marcas_objs = []
        modelos_objs = []
        
        for marca_nombre, modelos_nombres in marcas_modelos.items():
            marca, _ = MarcaVehiculo.objects.get_or_create(nombre=marca_nombre)
            marcas_objs.append(marca)
            
            for modelo_nombre in modelos_nombres:
                modelo, _ = ModeloVehiculo.objects.get_or_create(
                    marca=marca,
                    nombre=modelo_nombre
                )
                modelos_objs.append(modelo)
        
        # Zonas de Trabajo
        zonas = []
        for i in range(1, 5):
            zona, _ = ZonaTrabajo.objects.get_or_create(
                nombre=f'Zona {i}',
                defaults={'capacidad': 5, 'activa': True}
            )
            zonas.append(zona)
        
        # Estados de OT
        estados_nombres = ['PENDIENTE', 'EN_PROGRESO', 'FINALIZADO', 'EN_ESPERA']
        estados = []
        for nombre in estados_nombres:
            estado, _ = EstadoOT.objects.get_or_create(nombre=nombre)
            estados.append(estado)
        
        # Proveedores
        proveedores_nombres = [
            'Repuestos Automotrices S.A.',
            'Distribuidora de Autopartes Ltda.',
            'Importadora de Repuestos Chile',
            'Autopartes del Sur',
            'Repuestos Premium'
        ]
        proveedores = []
        for nombre in proveedores_nombres:
            prov, _ = Proveedor.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'rut': generar_rut_chileno(),
                    'telefono': f'+569{random.randint(10000000, 99999999)}',
                    'email': f'{nombre.lower().replace(" ", "")}@proveedor.com'
                }
            )
            proveedores.append(prov)
        
        # Servicios
        servicios_nombres = [
            ('Cambio de aceite', 15000),
            ('Alineación y balanceo', 25000),
            ('Revisión general', 30000),
            ('Reparación de frenos', 45000),
            ('Cambio de filtros', 20000),
            ('Revisión eléctrica', 35000),
            ('Reparación de motor', 80000),
            ('Lavado y encerado', 15000),
        ]
        servicios = []
        for nombre, precio in servicios_nombres:
            serv, _ = Servicio.objects.get_or_create(
                nombre=nombre,
                defaults={'precio_base': precio}
            )
            servicios.append(serv)
        
        self.stdout.write(self.style.SUCCESS('  ✓ Datos base creados (marcas, modelos, zonas, estados, proveedores, servicios)'))
        
        return {
            'marcas': marcas_objs,
            'modelos': modelos_objs,
            'zonas': zonas,
            'estados': estados,
            'proveedores': proveedores,
            'servicios': servicios
        }

    def _crear_clientes_vehiculos(self, datos_base):
        """Crea 10 clientes con vehículos."""
        nombres = [
            ('Roberto', 'Silva'), ('Patricia', 'Muñoz'), ('Fernando', 'Castro'),
            ('Carmen', 'Vargas'), ('Ricardo', 'Morales'), ('Sandra', 'Jiménez'),
            ('Mauricio', 'López'), ('Claudia', 'Ramírez'), ('Andrés', 'Gutiérrez'),
            ('Valentina', 'Díaz')
        ]
        
        clientes = []
        vehiculos = []
        
        for nombre, apellido in nombres:
            rut = generar_rut_chileno()
            cliente, _ = Cliente.objects.get_or_create(
                rut=rut,
                defaults={
                    'nombre': f'{nombre} {apellido}',
                    'telefono': f'+569{random.randint(10000000, 99999999)}',
                    'email': f'{nombre.lower()}.{apellido.lower()}@email.com',
                    'direccion': f'Calle {random.randint(1, 9999)} # {random.randint(1, 9999)}'
                }
            )
            clientes.append(cliente)
            
            # Crear vehículo para cada cliente
            patente = generar_patente_chilena()
            while Vehiculo.objects.filter(patente=patente).exists():
                patente = generar_patente_chilena()
            
            marca = random.choice(datos_base['marcas'])
            modelos_marca = [m for m in datos_base['modelos'] if m.marca == marca]
            modelo = random.choice(modelos_marca) if modelos_marca else random.choice(datos_base['modelos'])
            
            vehiculo = Vehiculo.objects.create(
                cliente=cliente,
                patente=patente,
                marca=marca,
                modelo=modelo,
                anio=random.randint(2010, 2024),
                kilometraje=random.randint(10000, 150000),
                fecha_ultimo_servicio=date.today() - timedelta(days=random.randint(30, 365))
            )
            vehiculos.append(vehiculo)
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(clientes)} clientes y {len(vehiculos)} vehículos creados'))
        
        return {'clientes': clientes, 'vehiculos': vehiculos}

    def _crear_ordenes_trabajo(self, clientes_vehiculos, datos_base, usuarios_creados):
        """Crea órdenes de trabajo en diferentes estados."""
        motivos = [
            'Revisión de motor', 'Cambio de aceite', 'Reparación de frenos',
            'Problema eléctrico', 'Revisión general', 'Alineación y balanceo',
            'Cambio de filtros', 'Reparación de transmisión', 'Revisión de suspensión',
            'Problema con aire acondicionado', 'Revisión de escape', 'Cambio de batería'
        ]
        
        descripciones = [
            'El vehículo presenta ruidos extraños en el motor',
            'Necesita cambio de aceite y filtros',
            'Los frenos hacen ruido y no responden bien',
            'Problemas con el sistema eléctrico, luces intermitentes',
            'Revisión completa del vehículo',
            'El vehículo se desvía al conducir',
            'Filtros sucios, necesita reemplazo',
            'Problemas al cambiar de marcha',
            'Suspensión hace ruido y se siente inestable',
            'Aire acondicionado no enfría',
            'Ruido fuerte en el escape',
            'Batería descargada, no enciende'
        ]
        
        ots = []
        mecanicos = usuarios_creados['mecanicos']
        estados_dict = {estado.nombre: estado for estado in datos_base['estados']}
        
        # 4 OTs PENDIENTE
        for i in range(4):
            cliente = random.choice(clientes_vehiculos['clientes'])
            vehiculo = random.choice([v for v in clientes_vehiculos['vehiculos'] if v.cliente == cliente])
            
            ot = OrdenTrabajo.objects.create(
                cliente=cliente,
                vehiculo=vehiculo,
                estado=estados_dict['PENDIENTE'],
                motivo_ingreso=random.choice(motivos),
                descripcion_problema=random.choice(descripciones),
                fecha_ingreso=date.today() - timedelta(days=random.randint(1, 7)),
                prioridad=random.choice(['BAJA', 'MEDIA', 'ALTA'])
            )
            ots.append(ot)
        
        # 4 OTs EN_PROGRESO
        for i in range(4):
            cliente = random.choice(clientes_vehiculos['clientes'])
            vehiculo = random.choice([v for v in clientes_vehiculos['vehiculos'] if v.cliente == cliente])
            mecanico = random.choice(mecanicos) if mecanicos else None
            zona = random.choice(datos_base['zonas'])
            
            fecha_ingreso = date.today() - timedelta(days=random.randint(3, 10))
            fecha_estimada = fecha_ingreso + timedelta(days=random.randint(2, 5))
            
            ot = OrdenTrabajo.objects.create(
                cliente=cliente,
                vehiculo=vehiculo,
                mecanico=mecanico,
                zona_trabajo=zona,
                estado=estados_dict['EN_PROGRESO'],
                motivo_ingreso=random.choice(motivos),
                descripcion_problema=random.choice(descripciones),
                fecha_ingreso=fecha_ingreso,
                fecha_estimada_entrega=fecha_estimada,
                prioridad=random.choice(['BAJA', 'MEDIA', 'ALTA'])
            )
            ots.append(ot)
        
        # 2 OTs FINALIZADAS
        for i in range(2):
            cliente = random.choice(clientes_vehiculos['clientes'])
            vehiculo = random.choice([v for v in clientes_vehiculos['vehiculos'] if v.cliente == cliente])
            mecanico = random.choice(mecanicos) if mecanicos else None
            zona = random.choice(datos_base['zonas'])
            
            fecha_ingreso = date.today() - timedelta(days=random.randint(10, 20))
            fecha_estimada = fecha_ingreso + timedelta(days=random.randint(3, 7))
            fecha_entrega = fecha_estimada + timedelta(days=random.randint(0, 2))
            
            ot = OrdenTrabajo.objects.create(
                cliente=cliente,
                vehiculo=vehiculo,
                mecanico=mecanico,
                zona_trabajo=zona,
                estado=estados_dict['FINALIZADO'],
                motivo_ingreso=random.choice(motivos),
                descripcion_problema=random.choice(descripciones),
                fecha_ingreso=fecha_ingreso,
                fecha_estimada_entrega=fecha_estimada,
                fecha_entrega_real=fecha_entrega,
                prioridad=random.choice(['BAJA', 'MEDIA', 'ALTA'])
            )
            ots.append(ot)
        
        # 2 OTs ATRASADAS (fecha estimada < hoy, estado EN_PROGRESO)
        for i in range(2):
            cliente = random.choice(clientes_vehiculos['clientes'])
            vehiculo = random.choice([v for v in clientes_vehiculos['vehiculos'] if v.cliente == cliente])
            mecanico = random.choice(mecanicos) if mecanicos else None
            zona = random.choice(datos_base['zonas'])
            
            fecha_ingreso = date.today() - timedelta(days=random.randint(10, 15))
            fecha_estimada = date.today() - timedelta(days=random.randint(1, 5))  # Atrasada
            
            ot = OrdenTrabajo.objects.create(
                cliente=cliente,
                vehiculo=vehiculo,
                mecanico=mecanico,
                zona_trabajo=zona,
                estado=estados_dict['EN_PROGRESO'],
                motivo_ingreso=random.choice(motivos),
                descripcion_problema=random.choice(descripciones),
                fecha_ingreso=fecha_ingreso,
                fecha_estimada_entrega=fecha_estimada,
                prioridad=random.choice(['MEDIA', 'ALTA'])
            )
            ots.append(ot)
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ {len(ots)} órdenes de trabajo creadas (4 PENDIENTE, 4 EN_PROGRESO, 2 FINALIZADAS, 2 ATRASADAS)'))
        
        return ots

    def _crear_bitacoras(self, ots, usuarios_creados):
        """Crea bitácoras para las OTs."""
        descripciones_bitacora = [
            'Revisión inicial del vehículo. Se identificaron los problemas principales.',
            'Desmontaje de componentes para inspección detallada.',
            'Limpieza y preparación de piezas para reparación.',
            'Instalación de repuestos nuevos. Verificación de funcionamiento.',
            'Pruebas de funcionamiento. Todo operando correctamente.',
            'Ajustes finales realizados. Vehículo listo para pruebas de ruta.',
            'Reparación completada. Pendiente control de calidad.',
            'Trabajo en progreso. Se requiere material adicional.',
        ]
        
        estados_avance = ['EN_PROCESO', 'EN_PAUSA', 'FINALIZADO']
        
        total_bitacoras = 0
        bitacoras_creadas = 0
        bitacoras_existentes = 0
        
        # Solo crear bitácoras para OTs que tienen mecánico asignado
        ots_con_mecanico = [ot for ot in ots if ot.mecanico]
        
        for ot in ots_con_mecanico:
            # Verificar cuántas bitácoras ya existen para esta OT
            bitacoras_existentes_ot = BitacoraTrabajo.objects.filter(orden=ot).count()
            
            # Si ya tiene 4 bitácoras, no crear más
            if bitacoras_existentes_ot >= 4:
                bitacoras_existentes += bitacoras_existentes_ot
                total_bitacoras += bitacoras_existentes_ot
                continue
            
            # Crear entre 1 y 4 bitácoras, pero no más de las que faltan
            num_bitacoras = random.randint(1, 4)
            num_bitacoras = min(num_bitacoras, 4 - bitacoras_existentes_ot)
            
            for i in range(num_bitacoras):
                mecanico_obj = ot.mecanico
                descripcion = random.choice(descripciones_bitacora)
                tiempo = random.randint(20, 120)
                estado = random.choice(estados_avance)
                
                # Verificar si ya existe una bitácora similar (evitar duplicados exactos)
                bitacora_existente = BitacoraTrabajo.objects.filter(
                    orden=ot,
                    mecanico=mecanico_obj,
                    descripcion=descripcion
                ).first()
                
                if not bitacora_existente:
                    bitacora = BitacoraTrabajo.objects.create(
                        orden=ot,
                        mecanico=mecanico_obj,
                        descripcion=descripcion,
                        tiempo_ejecucion_minutos=tiempo,
                        estado_avance=estado
                    )
                    bitacoras_creadas += 1
                    total_bitacoras += 1
                else:
                    bitacoras_existentes += 1
                    total_bitacoras += 1
        
        mensaje = f'  ✓ {total_bitacoras} bitácoras procesadas'
        if bitacoras_creadas > 0 and bitacoras_existentes > 0:
            mensaje += f' ({bitacoras_creadas} creadas, {bitacoras_existentes} ya existían)'
        elif bitacoras_creadas > 0:
            mensaje += f' ({bitacoras_creadas} creadas)'
        elif bitacoras_existentes > 0:
            mensaje += f' ({bitacoras_existentes} ya existían)'
        
        self.stdout.write(self.style.SUCCESS(mensaje))

    def _crear_repuestos(self, datos_base):
        """Crea 20 repuestos con diferentes stocks."""
        repuestos_data = [
            ('FIL-001', 'Filtro de aceite', 'Filtro de aceite estándar', 'Toyota', 8000, 12),
            ('FIL-002', 'Filtro de aire', 'Filtro de aire de alta eficiencia', 'K&N', 15000, 8),
            ('PAST-001', 'Pastillas de freno delanteras', 'Pastillas cerámicas', 'Brembo', 45000, 5),
            ('PAST-002', 'Pastillas de freno traseras', 'Pastillas orgánicas', 'Brembo', 35000, 3),
            ('ACE-001', 'Aceite motor 5W-30', 'Aceite sintético 4L', 'Mobil', 25000, 15),
            ('ACE-002', 'Aceite motor 10W-40', 'Aceite mineral 4L', 'Castrol', 18000, 10),
            ('BAT-001', 'Batería 60Ah', 'Batería sellada', 'ACDelco', 65000, 4),
            ('BAT-002', 'Batería 70Ah', 'Batería sellada', 'ACDelco', 75000, 2),
            ('DIS-001', 'Disco de freno delantero', 'Disco ventilado', 'Brembo', 55000, 6),
            ('DIS-002', 'Disco de freno trasero', 'Disco sólido', 'Brembo', 45000, 4),
            ('BOM-001', 'Bomba de agua', 'Bomba de agua original', 'Gates', 85000, 3),
            ('TER-001', 'Termostato', 'Termostato estándar', 'Gates', 12000, 7),
            ('COR-001', 'Correa de distribución', 'Correa de goma', 'Gates', 35000, 5),
            ('BUL-001', 'Amortiguador delantero', 'Amortiguador hidráulico', 'Monroe', 95000, 2),
            ('BUL-002', 'Amortiguador trasero', 'Amortiguador hidráulico', 'Monroe', 85000, 1),  # Stock bajo
            ('BUF-001', 'Bujía de encendido', 'Bujía iridium', 'NGK', 8000, 12),
            ('RAD-001', 'Radiador', 'Radiador de aluminio', 'Spectra', 120000, 1),  # Stock bajo
            ('BOM-002', 'Bomba de combustible', 'Bomba eléctrica', 'Bosch', 95000, 3),
            ('SEN-001', 'Sensor de oxígeno', 'Sensor lambda', 'Bosch', 45000, 4),
            ('FIL-003', 'Filtro de combustible', 'Filtro de línea', 'Mann', 15000, 2),  # Stock bajo
        ]
        
        repuestos = []
        repuestos_creados = 0
        repuestos_existentes = 0
        
        for codigo, nombre, descripcion, marca, precio_venta, stock in repuestos_data:
            proveedor = random.choice(datos_base['proveedores'])
            precio_compra = int(precio_venta * 0.6)  # 60% del precio de venta
            
            estado = 'DISPONIBLE'
            if stock == 0:
                estado = 'AGOTADO'
            elif stock < 3:
                estado = 'DISPONIBLE'  # Pero con stock bajo
            
            # Usar get_or_create para evitar duplicados
            repuesto, creado = Repuesto.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'marca': marca,
                    'precio_compra': precio_compra,
                    'precio_venta': precio_venta,
                    'stock': stock,
                    'estado': estado,
                    'proveedor': proveedor,
                    'fecha_ingreso': date.today() - timedelta(days=random.randint(1, 180)),
                    'ubicacion_bodega': f'Estante {random.choice(["A", "B", "C"])} - {random.randint(1, 10)}'
                }
            )
            
            if creado:
                repuestos_creados += 1
            else:
                repuestos_existentes += 1
            
            repuestos.append(repuesto)
        
        mensaje = f'  ✓ {len(repuestos)} repuestos procesados'
        if repuestos_creados > 0 and repuestos_existentes > 0:
            mensaje += f' ({repuestos_creados} creados, {repuestos_existentes} ya existían)'
        elif repuestos_creados > 0:
            mensaje += f' ({repuestos_creados} creados)'
        elif repuestos_existentes > 0:
            mensaje += f' ({repuestos_existentes} ya existían)'
        
        self.stdout.write(self.style.SUCCESS(mensaje))
        
        return repuestos

    def _crear_herramientas(self, usuarios_creados):
        """Crea 10 herramientas. Idempotente."""
        herramientas_data = [
            ('LL-001', 'Llave inglesa ajustable', 'Llave de 12 pulgadas', 'Bahco', 'OPERATIVA'),
            ('LL-002', 'Juego de llaves allen', 'Juego completo 9 piezas', 'Bahco', 'OPERATIVA'),
            ('TOR-001', 'Torquímetro digital', 'Rango 10-200 Nm', 'CDI', 'OPERATIVA'),
            ('ELE-001', 'Multímetro digital', 'Multímetro profesional', 'Fluke', 'OPERATIVA'),
            ('ELE-002', 'Escáner OBD2', 'Escáner diagnóstico', 'Autel', 'OPERATIVA'),
            ('ELE-003', 'Probador de batería', 'Probador de carga', 'Schumacher', 'OPERATIVA'),
            ('ELE-004', 'Cargador de batería', 'Cargador 12V 10A', 'Schumacher', 'EN_MANTENCION'),
            ('HID-001', 'Gato hidráulico 2 ton', 'Gato de piso', 'Torin', 'EN_MANTENCION'),
            ('COM-001', 'Compresor de aire', 'Compresor portátil 12V', 'VIAIR', 'OPERATIVA'),
            ('EXT-001', 'Extractor de bujías', 'Extractor magnético', 'Lisle', 'OPERATIVA'),
        ]
        
        herramientas = []
        mecanicos = usuarios_creados['mecanicos']
        herramientas_creadas = 0
        herramientas_existentes = 0
        
        for i, (codigo, nombre, descripcion, marca, estado) in enumerate(herramientas_data):
            # Verificar si ya existe
            herramienta, creada = Herramienta.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'nombre': nombre,
                    'descripcion': descripcion,
                    'marca': marca,
                    'cantidad': 1,
                    'ubicacion_fisica': f'Caja de herramientas {random.choice(["A", "B", "C"])}',
                    'estado': estado,
                    'fecha_adquisicion': date.today() - timedelta(days=random.randint(30, 1000))
                }
            )
            
            if creada:
                herramientas_creadas += 1
            else:
                herramientas_existentes += 1
            
            # Si está en mantención o retirada, asignar a un mecánico (solo si fue creada o no tiene responsable)
            if estado == 'EN_MANTENCION' and mecanicos and (creada or not herramienta.responsable_asignado):
                herramienta.responsable_asignado = random.choice(mecanicos)
                herramienta.save()
                
                # Crear entrada en HerramientaEnUso si hay OTs en progreso y no existe ya
                ots_progreso = OrdenTrabajo.objects.filter(
                    estado__nombre='EN_PROGRESO',
                    mecanico=herramienta.responsable_asignado
                )
                if ots_progreso.exists():
                    ot = random.choice(ots_progreso)
                    # Verificar si ya existe la relación
                    if not HerramientaEnUso.objects.filter(orden=ot, herramienta=herramienta, fecha_devolucion__isnull=True).exists():
                        HerramientaEnUso.objects.create(
                            orden=ot,
                            herramienta=herramienta,
                            fecha_asignacion=timezone.now() - timedelta(days=random.randint(1, 5))
                        )
            
            herramientas.append(herramienta)
        
        # 2 herramientas retiradas por mecánicos (solo si no están ya asignadas)
        if mecanicos and len(herramientas) >= 2:
            herramientas_operativas = [h for h in herramientas if h.estado == 'OPERATIVA' and not h.responsable_asignado]
            herramientas_a_retirar = min(2, len(herramientas_operativas))
            
            for i in range(herramientas_a_retirar):
                herramienta = herramientas_operativas[i]
                herramienta.estado = 'EN_MANTENCION'
                herramienta.responsable_asignado = random.choice(mecanicos)
                herramienta.save()
                
                # Crear entrada en HerramientaEnUso si no existe
                ots_progreso = OrdenTrabajo.objects.filter(
                    estado__nombre='EN_PROGRESO',
                    mecanico=herramienta.responsable_asignado
                )
                if ots_progreso.exists():
                    ot = random.choice(ots_progreso)
                    # Verificar si ya existe la relación
                    if not HerramientaEnUso.objects.filter(orden=ot, herramienta=herramienta, fecha_devolucion__isnull=True).exists():
                        HerramientaEnUso.objects.create(
                            orden=ot,
                            herramienta=herramienta,
                            fecha_asignacion=timezone.now() - timedelta(days=random.randint(1, 3))
                        )
        
        mensaje = f'  ✓ {len(herramientas)} herramientas procesadas'
        if herramientas_creadas > 0 and herramientas_existentes > 0:
            mensaje += f' ({herramientas_creadas} creadas, {herramientas_existentes} ya existían)'
        elif herramientas_creadas > 0:
            mensaje += f' ({herramientas_creadas} creadas)'
        elif herramientas_existentes > 0:
            mensaje += f' ({herramientas_existentes} ya existían)'
        
        self.stdout.write(self.style.SUCCESS(mensaje))
        
        return herramientas

    def _crear_notificaciones(self, ots, usuarios_creados, repuestos):
        """Crea notificaciones de diferentes tipos."""
        perfil_encargado = PerfilUsuario.objects.filter(rol=RolUsuario.ENCARGADO_TALLER).first()
        perfil_recepcionista = PerfilUsuario.objects.filter(rol=RolUsuario.RECEPCIONISTA).first()
        perfiles_mecanicos = PerfilUsuario.objects.filter(rol=RolUsuario.MECANICO)
        
        total_notificaciones = 0
        
        # Notificaciones de atraso
        ots_atrasadas = [ot for ot in ots if ot.fecha_estimada_entrega and ot.fecha_estimada_entrega < date.today() and ot.estado.nombre == 'EN_PROGRESO']
        for ot in ots_atrasadas[:2]:  # Máximo 2 notificaciones de atraso
            if ot.mecanico:
                perfil_mecanico = perfiles_mecanicos.filter(usuario__username=ot.mecanico.nombre.split()[0].lower() + '1').first()
                if perfil_mecanico and perfil_encargado:
                    Notificacion.objects.create(
                        tipo='ATRASO_TRABAJO',
                        orden=ot,
                        mensaje=f'La OT #{ot.id} está atrasada. Fecha estimada: {ot.fecha_estimada_entrega}',
                        emisor=perfil_mecanico,
                        receptor=perfil_encargado
                    )
                    total_notificaciones += 1
        
        # Notificaciones de solicitud de cambio
        ots_progreso = [ot for ot in ots if ot.estado.nombre == 'EN_PROGRESO']
        for ot in ots_progreso[:2]:  # Máximo 2 solicitudes
            if ot.mecanico:
                perfil_mecanico = perfiles_mecanicos.filter(usuario__username=ot.mecanico.nombre.split()[0].lower() + '1').first()
                if perfil_mecanico and perfil_encargado:
                    solicitudes = [
                        'Necesito cambiar el repuesto por uno de mejor calidad',
                        'Se requiere autorización para trabajo adicional',
                        'El vehículo necesita más tiempo del estimado',
                        'Falta material para completar el trabajo'
                    ]
                    Notificacion.objects.create(
                        tipo='SOLICITUD_CAMBIO',
                        orden=ot,
                        mensaje=random.choice(solicitudes),
                        emisor=perfil_mecanico,
                        receptor=perfil_encargado
                    )
                    total_notificaciones += 1
        
        # Notificaciones de stock bajo
        repuestos_bajo_stock = [r for r in repuestos if r.stock < 3]
        for repuesto in repuestos_bajo_stock[:3]:  # Máximo 3 notificaciones de stock
            if perfil_encargado and perfil_recepcionista:
                Notificacion.objects.create(
                    tipo='MENSAJE_GENERAL',
                    orden=None,
                    mensaje=f'Repuesto {repuesto.nombre} bajo en stock (solo {repuesto.stock} unidades).',
                    emisor=perfil_recepcionista,
                    receptor=perfil_encargado
                )
                total_notificaciones += 1
        
        # Notificaciones generales
        if perfil_encargado and perfiles_mecanicos.exists():
            mensajes_generales = [
                'Nueva orden de trabajo asignada',
                'Recordatorio: Revisar herramientas antes de finalizar',
                'Reunión de coordinación programada',
            ]
            for i in range(2):
                Notificacion.objects.create(
                    tipo='MENSAJE_GENERAL',
                    orden=None,
                    mensaje=random.choice(mensajes_generales),
                    emisor=perfil_encargado,
                    receptor=random.choice(list(perfiles_mecanicos))
                )
                total_notificaciones += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ {total_notificaciones} notificaciones creadas'))

    def _crear_controles_calidad(self, ots, usuarios_creados):
        """Crea controles de calidad para algunas OTs."""
        perfil_encargado = PerfilUsuario.objects.filter(rol=RolUsuario.ENCARGADO_TALLER).first()
        if not perfil_encargado:
            return
        
        ots_progreso = [ot for ot in ots if ot.estado.nombre == 'EN_PROGRESO']
        
        # Una OT aprobada
        if ots_progreso:
            ot_aprobada = random.choice(ots_progreso)
            control = ControlCalidad.objects.create(
                orden=ot_aprobada,
                responsable=perfil_encargado.usuario.username,
                resultado='APROBADO',
                observaciones_generales='Trabajo realizado correctamente. Vehículo en perfectas condiciones.',
                prueba_ruta_ok=True,
                fluidos_verificados=True,
                luces_sistema_electrico_ok=True,
                herramientas_retiradas=True,
                vehiculo_limpio=True
            )
            # Cambiar estado a FINALIZADO
            estado_finalizado = EstadoOT.objects.get_or_create(nombre='FINALIZADO')[0]
            ot_aprobada.estado = estado_finalizado
            ot_aprobada.save()
        
        # Una OT rechazada
        ots_progreso_restantes = [ot for ot in ots_progreso if ot.id != ot_aprobada.id]
        if ots_progreso_restantes:
            ot_rechazada = random.choice(ots_progreso_restantes)
            control = ControlCalidad.objects.create(
                orden=ot_rechazada,
                responsable=perfil_encargado.usuario.username,
                resultado='RECHAZADO',
                observaciones_generales='Se encontraron problemas adicionales. Requiere revisión.',
                prueba_ruta_ok=False,
                fluidos_verificados=True,
                luces_sistema_electrico_ok=False,
                herramientas_retiradas=True,
                vehiculo_limpio=False
            )
            # Cambiar estado a PENDIENTE
            estado_pendiente = EstadoOT.objects.get_or_create(nombre='PENDIENTE')[0]
            ot_rechazada.estado = estado_pendiente
            ot_rechazada.save()
        
        self.stdout.write(self.style.SUCCESS('  ✓ 2 controles de calidad creados (1 aprobado, 1 rechazado)'))

