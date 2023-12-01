# Generated by Django 4.2.6 on 2023-11-23 11:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_distancemetric_vehicletype_vehiclemeric_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='VehicleMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle_type', models.CharField(max_length=200)),
                ('cost', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='errandtask',
            name='distance_in_km',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='VehicleMeric',
        ),
        migrations.AlterField(
            model_name='errandtask',
            name='vehicle_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.vehiclemetric'),
        ),
        migrations.DeleteModel(
            name='VehicleType',
        ),
    ]
