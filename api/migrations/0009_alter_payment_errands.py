# Generated by Django 4.1.3 on 2024-02-03 07:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_rename_payment_mode_1_errandtask_payment_method'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='errands',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.errandtask'),
        ),
    ]
