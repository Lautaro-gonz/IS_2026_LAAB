"""
Exporta estadísticas de todos los turnos a TXT (separado por tabulaciones) y PDF.

Uso:
    python exportar_estadistica.py

Archivos generados en la raíz del proyecto:
    turnos_estadistica.txt
    turnos_estadistica.pdf

Requiere:
    pip install reportlab
"""
import os
import sys
import django
from datetime import date

# ── Configuración Django ──────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'turnos_medicos.settings')
django.setup()

from turnos.models import TurnoDB

# ── Constantes ────────────────────────────────────────────────────────────────
DIAS_SEMANA = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
MESES_NOMBRES = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]
COLUMNAS = [
    'fecha', 'especialidad', 'estado', 'duracion_min',
    'costo_total', 'cubre_os', 'paga_paciente', 'obra_social',
    'dias_anticipacion', 'franja_horaria', 'porcentaje_cobertura',
    'dia_semana', 'mes', 'notif_enviadas', 'motivo_consulta',
]

TXT_PATH = os.path.join(BASE_DIR, 'turnos_estadistica.txt')
PDF_PATH = os.path.join(BASE_DIR, 'turnos_estadistica.pdf')


def _franja_horaria(hora_str):
    try:
        h = int(hora_str.split(':')[0])
        if h < 12:
            return 'mañana'
        if h < 17:
            return 'tarde'
        return 'noche'
    except (ValueError, IndexError):
        return ''


def _build_row(turno):
    if turno.creado_en:
        dias_ant = (turno.fecha - turno.creado_en.date()).days
    else:
        dias_ant = 0

    pct_cob = round(turno.cubre_os / turno.costo_total * 100, 1) if turno.costo_total > 0 else 0.0
    notifs  = turno.notificaciones.count()

    return [
        str(turno.fecha),
        turno.medico_especialidad,
        turno.estado,
        str(turno.duracion),
        str(round(turno.costo_total,   2)),
        str(round(turno.cubre_os,      2)),
        str(round(turno.paga_paciente, 2)),
        turno.paciente_obra_social or 'Sin OS',
        str(dias_ant),
        _franja_horaria(turno.hora),
        str(pct_cob),
        DIAS_SEMANA[turno.fecha.weekday()],
        MESES_NOMBRES[turno.fecha.month - 1],
        str(notifs),
        turno.motivo_consulta or '',
    ]


# ── Exportar TXT ─────────────────────────────────────────────────────────────
def exportar_txt(turnos):
    with open(TXT_PATH, 'w', encoding='utf-8') as f:
        f.write('\t'.join(COLUMNAS) + '\n')
        for t in turnos:
            f.write('\t'.join(_build_row(t)) + '\n')
    print(f'[OK] TXT generado: {TXT_PATH}')


# ── Exportar PDF ─────────────────────────────────────────────────────────────
def exportar_pdf(turnos):
    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
    except ImportError:
        print('ERROR: reportlab no está instalado. Ejecutá: pip install reportlab')
        sys.exit(1)

    doc = SimpleDocTemplate(
        PDF_PATH,
        pagesize=landscape(A4),
        leftMargin=18, rightMargin=18,
        topMargin=28, bottomMargin=28,
    )
    styles   = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph('Estadística de Turnos — Clínica LAAB', styles['Title']))
    elements.append(Paragraph(
        f'Generado el {date.today().strftime("%d/%m/%Y")} · Total: {len(turnos)} turno(s)',
        styles['Normal'],
    ))
    elements.append(Spacer(1, 14))

    data = [COLUMNAS] + [_build_row(t) for t in turnos]

    # Anchos (suma ≈ A4 landscape 595 pt − márgenes)
    col_widths = [52, 68, 58, 42, 52, 48, 52, 68, 52, 46, 58, 52, 46, 42, 76]

    table = Table(data, colWidths=col_widths, repeatRows=1)
    tabla_style = [
        ('BACKGROUND',    (0, 0), (-1, 0),  colors.HexColor('#1a56db')),
        ('TEXTCOLOR',     (0, 0), (-1, 0),  colors.white),
        ('FONTNAME',      (0, 0), (-1, 0),  'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, 0),  6.5),
        ('FONTSIZE',      (0, 1), (-1, -1), 6),
        ('GRID',          (0, 0), (-1, -1), 0.35, colors.HexColor('#e4e9f5')),
        ('ALIGN',         (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',    (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]
    # Filas alternadas
    for i in range(1, len(data)):
        if i % 2 == 0:
            tabla_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f0f4ff')))

    table.setStyle(TableStyle(tabla_style))
    elements.append(table)
    doc.build(elements)
    print(f'[OK] PDF generado: {PDF_PATH}')


# ── Main ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('Consultando base de datos...')
    turnos = list(
        TurnoDB.objects.prefetch_related('notificaciones').order_by('fecha', 'hora')
    )
    print(f'Total de turnos a exportar: {len(turnos)}')
    exportar_txt(turnos)
    exportar_pdf(turnos)
    print('\nExportación completada.')
