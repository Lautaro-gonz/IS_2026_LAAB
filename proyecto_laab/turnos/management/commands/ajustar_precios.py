"""
Ajusta el costo de los turnos futuros (PENDIENTE/CONFIRMADO) según el
porcentaje de inflación más reciente cargado en InflacionDB.

Uso:
    python manage.py ajustar_precios
    python manage.py ajustar_precios --periodo 2025-04   # valida período
    python manage.py ajustar_precios --dry-run           # muestra cambios sin guardar
"""
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from datetime import date

from turnos.models import TurnoDB, InflacionDB


class Command(BaseCommand):
    help = 'Aplica el porcentaje de inflación INDEC sobre los turnos futuros.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--periodo',
            type=str,
            default=None,
            help='Período específico a aplicar (YYYY-MM). Por defecto usa el más reciente.',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Muestra los cambios sin guardar en la base de datos.',
        )

    def handle(self, *args, **options):
        periodo   = options.get('periodo')
        dry_run   = options.get('dry_run')

        # Obtener registro de inflación
        try:
            if periodo:
                inflacion = InflacionDB.objects.get(periodo=periodo)
            else:
                inflacion = InflacionDB.objects.latest('registrado_en')
        except InflacionDB.DoesNotExist:
            raise CommandError(
                'No se encontró registro de inflación. '
                'Cargá el porcentaje desde el panel de administración.'
            )

        porcentaje = inflacion.porcentaje
        factor     = 1 + porcentaje / 100
        hoy        = date.today()

        self.stdout.write(
            self.style.NOTICE(
                f'\nAplicando inflación del {porcentaje}% (período {inflacion.periodo}) '
                f'sobre turnos a partir del {hoy}.'
            )
        )
        if dry_run:
            self.stdout.write(self.style.WARNING('--- MODO DRY-RUN: no se guardan cambios ---'))

        turnos = TurnoDB.objects.filter(
            fecha__gte=hoy,
            estado__in=['PENDIENTE', 'CONFIRMADO'],
        )

        if not turnos.exists():
            self.stdout.write(self.style.WARNING('No hay turnos futuros para ajustar.'))
            return

        count = 0
        for turno in turnos:
            costo_anterior = turno.costo_total
            nuevo_total    = round(turno.costo_total   * factor, 2)
            nuevo_os       = round(turno.cubre_os      * factor, 2)
            nuevo_paciente = round(turno.paga_paciente * factor, 2)

            self.stdout.write(
                f'  Turno #{turno.pk} ({turno.paciente_nombre} — {turno.fecha}): '
                f'${costo_anterior:,.2f} → ${nuevo_total:,.2f}'
            )

            if not dry_run:
                turno.costo_anterior = costo_anterior
                turno.costo_total    = nuevo_total
                turno.cubre_os       = nuevo_os
                turno.paga_paciente  = nuevo_paciente
                turno.save()

            count += 1

        accion = 'se ajustarían' if dry_run else 'ajustados'
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ {count} turno{"s" if count != 1 else ""} {accion} '
                f'con inflación del {porcentaje}% (período {inflacion.periodo}).\n'
            )
        )
