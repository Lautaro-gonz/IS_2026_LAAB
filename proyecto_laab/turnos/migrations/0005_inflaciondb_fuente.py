from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('turnos', '0004_notificaciondb_leida'),
    ]

    operations = [
        migrations.AddField(
            model_name='inflaciondb',
            name='fuente',
            field=models.CharField(blank=True, default='Manual', max_length=200),
        ),
    ]
