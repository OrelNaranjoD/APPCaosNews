from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from CaosNewsApp.models import Suscripcion


class Command(BaseCommand):
    help = 'Revisa suscripciones próximas a vencer y envía notificaciones por email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dias',
            type=int,
            default=3,
            help='Días antes del vencimiento para enviar notificación (default: 3)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra las suscripciones sin enviar emails'
        )

    def handle(self, *args, **options):
        dias_limite = options['dias']
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS(f'🔍 Revisando suscripciones próximas a vencer en {dias_limite} días...')
        )
        
        # Buscar suscripciones próximas a vencer
        fecha_limite = timezone.now() + timedelta(days=dias_limite)
        
        suscripciones_proximas = Suscripcion.objects.filter(
            estado='A',  # Activas
            fecha_fin__lte=fecha_limite,
            fecha_fin__gte=timezone.now()  # Incluir las que expiran hoy (>=)
        ).select_related('usuario', 'plan', 'precio_plan')

        if not suscripciones_proximas.exists():
            self.stdout.write(
                self.style.WARNING('✅ No hay suscripciones próximas a vencer.')
            )
            return

        self.stdout.write(
            self.style.WARNING(f'⚠️  Encontradas {suscripciones_proximas.count()} suscripciones próximas a vencer:')
        )

        notificaciones_enviadas = 0
        errores = 0

        for suscripcion in suscripciones_proximas:
            dias_restantes = suscripcion.dias_restantes
            usuario = suscripcion.usuario
            
            # Mostrar información de la suscripción
            self.stdout.write(
                f'  📋 Usuario: {usuario.username} ({usuario.email})'
            )
            self.stdout.write(
                f'     Plan: {suscripcion.plan.nombre}'
            )
            self.stdout.write(
                f'     Días restantes: {dias_restantes}'
            )
            self.stdout.write(
                f'     Fecha vencimiento: {suscripcion.fecha_fin.strftime("%d/%m/%Y %H:%M")}'
            )
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING('     🔄 Modo prueba - Email y notificación NO enviados')
                )
                continue
            
            # Crear mensaje para notificación del dashboard
            if dias_restantes == 0:
                mensaje_dashboard = f"🚨 Tu suscripción al plan '{suscripcion.plan.nombre}' expira HOY. Renueva ahora para no perder el acceso."
            elif dias_restantes == 1:
                mensaje_dashboard = f"⚠️ Tu suscripción al plan '{suscripcion.plan.nombre}' expira MAÑANA. Te recomendamos renovar pronto."
            else:
                mensaje_dashboard = f"📅 Tu suscripción al plan '{suscripcion.plan.nombre}' expira en {dias_restantes} días. Considera renovar tu plan."
            
            # Crear notificación en el dashboard (evitar duplicados)
            if not usuario.notificaciones.filter(mensaje=mensaje_dashboard, leido=False).exists():
                usuario.crear_notificacion_sistema(mensaje_dashboard)
                self.stdout.write(f'     📱 Notificación creada en dashboard')
            else:
                self.stdout.write(f'     📱 Notificación ya existe en dashboard')
            
            # Preparar mensaje de email
            if dias_restantes == 0:
                asunto = '🚨 Tu suscripción expira HOY'
                urgencia = 'hoy'
            elif dias_restantes == 1:
                asunto = '⚠️ Tu suscripción expira mañana'
                urgencia = 'mañana'
            else:
                asunto = f'📅 Tu suscripción expira en {dias_restantes} días'
                urgencia = f'en {dias_restantes} días'
            
            mensaje = f"""
Hola {usuario.get_full_name() or usuario.username},

Tu suscripción al plan "{suscripcion.plan.nombre}" expirará {urgencia}.

📅 Fecha de vencimiento: {suscripcion.fecha_fin.strftime('%d de %B de %Y a las %H:%M')}
💰 Plan actual: {suscripcion.plan.nombre}
💳 Precio pagado: ${suscripcion.precio_plan.valor} ({suscripcion.precio_plan.nombre_periodo})

Para continuar disfrutando de todos los beneficios de CaosNews, 
te recomendamos renovar tu suscripción antes del vencimiento.

🔗 Renovar suscripción: {settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/suscripciones/

¡Gracias por ser parte de CaosNews!

---
Equipo CaosNews
            """.strip()
            
            # Crear mensaje corto para notificación del dashboard
            if dias_restantes == 0:
                mensaje_dashboard = f"🚨 Tu suscripción al plan '{suscripcion.plan.nombre}' expira HOY. Renueva ahora para mantener el acceso."
            elif dias_restantes == 1:
                mensaje_dashboard = f"⚠️ Tu suscripción al plan '{suscripcion.plan.nombre}' expira MAÑANA. Te recomendamos renovar pronto."
            else:
                mensaje_dashboard = f"📅 Tu suscripción al plan '{suscripcion.plan.nombre}' expira en {dias_restantes} días. Considera renovar tu plan."
            
            # Crear notificación en el dashboard (si no existe una similar sin leer)
            notificaciones_existentes = suscripcion.usuario.get_notificaciones_no_leidas().filter(
                mensaje__icontains=f"suscripción al plan '{suscripcion.plan.nombre}'"
            )
            
            if not notificaciones_existentes.exists():
                suscripcion.usuario.crear_notificacion_sistema(mensaje_dashboard)
                self.stdout.write(
                    self.style.SUCCESS(f'     📱 Notificación creada en dashboard')
                )

            # Enviar email
            try:
                send_mail(
                    subject=asunto,
                    message=mensaje,
                    from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@caosnews.com'),
                    recipient_list=[usuario.email],
                    fail_silently=False,
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'     ✅ Email enviado a {usuario.email}')
                )
                notificaciones_enviadas += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'     ❌ Error enviando email a {usuario.email}: {str(e)}')
                )
                errores += 1
            
            self.stdout.write('') # Línea en blanco para separar

        # Resumen final
        self.stdout.write('=' * 50)
        self.stdout.write(
            self.style.SUCCESS(f'📊 RESUMEN:')
        )
        self.stdout.write(f'   • Suscripciones revisadas: {suscripciones_proximas.count()}')
        
        if not dry_run:
            self.stdout.write(f'   • Notificaciones enviadas: {notificaciones_enviadas}')
            if errores > 0:
                self.stdout.write(
                    self.style.ERROR(f'   • Errores: {errores}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS('   • ✅ Todos los emails enviados correctamente')
                )
        else:
            self.stdout.write(
                self.style.WARNING('   • Modo prueba - Ningún email fue enviado')
            )
