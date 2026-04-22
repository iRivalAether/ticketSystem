# Generated manually for reportes app models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tickets', '0003_semaforoslaconfig'),
    ]

    operations = [
        migrations.CreateModel(
            name='Reporte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='Activo')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de eliminación')),
                ('tipo', models.CharField(choices=[('semanal', 'Reporte Semanal'), ('mensual', 'Reporte Mensual'), ('personalizado', 'Reporte Personalizado')], max_length=80, verbose_name='Tipo de reporte')),
                ('fecha_generacion', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Fecha de generación')),
                ('area', models.ForeignKey(blank=True, help_text='Si está vacío, es un reporte global', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reportes', to='tickets.area', verbose_name='Área')),
                ('generado_por_usuario', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reportes_generados', to=settings.AUTH_USER_MODEL, verbose_name='Generado por')),
            ],
            options={
                'verbose_name': 'Reporte',
                'verbose_name_plural': 'Reportes',
                'ordering': ['-fecha_generacion'],
                'db_table': 'reporte',
            },
        ),
        migrations.CreateModel(
            name='KPI',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='Activo')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de eliminación')),
                ('tiempo_promedio_atencion', models.FloatField(blank=True, null=True, verbose_name='Tiempo promedio de atención (minutos)')),
                ('tiempo_promedio_resolucion', models.FloatField(blank=True, null=True, verbose_name='Tiempo promedio de resolución (horas)')),
                ('cumplimiento_sla', models.FloatField(blank=True, help_text='Porcentaje de tickets que cumplieron el SLA', null=True, verbose_name='Cumplimiento de SLA (%)')),
                ('reporte', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='kpis', to='reportes.reporte', verbose_name='Reporte')),
            ],
            options={
                'verbose_name': 'KPI',
                'verbose_name_plural': 'KPIs',
                'ordering': ['-created_at'],
                'db_table': 'kpi',
            },
        ),
        migrations.CreateModel(
            name='SLAReporte',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='Activo')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de eliminación')),
                ('area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sla_reportes', to='tickets.area', verbose_name='Área')),
                ('prioridad', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sla_reportes', to='tickets.prioridad', verbose_name='Prioridad')),
                ('reporte', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sla_reportes', to='reportes.reporte', verbose_name='Reporte')),
                ('sla', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sla_reportes', to='tickets.sla', verbose_name='SLA')),
            ],
            options={
                'verbose_name': 'SLA Reporte',
                'verbose_name_plural': 'SLA Reportes',
                'ordering': ['-created_at'],
                'db_table': 'sla_reporte',
            },
        ),
        migrations.CreateModel(
            name='RetroalimentacionTicket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Fecha de creación')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Fecha de actualización')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='Activo')),
                ('deleted_at', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de eliminación')),
                ('especialidad', models.CharField(help_text='Especialidad o categoría evaluada', max_length=120, verbose_name='Especialidad')),
                ('calificacion', models.PositiveSmallIntegerField(choices=[(1, '1 - Muy mala'), (2, '2 - Mala'), (3, '3 - Regular'), (4, '4 - Buena'), (5, '5 - Excelente')], default=3, verbose_name='Calificación')),
                ('comentario', models.TextField(blank=True, verbose_name='Comentario')),
                ('area', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='retroalimentaciones', to='tickets.area', verbose_name='Área')),
                ('creado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='retroalimentaciones_creadas', to=settings.AUTH_USER_MODEL, verbose_name='Creado por')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='retroalimentaciones', to='tickets.ticket', verbose_name='Ticket')),
            ],
            options={
                'verbose_name': 'Retroalimentación de Ticket',
                'verbose_name_plural': 'Retroalimentaciones de Tickets',
                'ordering': ['-created_at'],
                'db_table': 'retroalimentacion_ticket',
            },
        ),
    ]
