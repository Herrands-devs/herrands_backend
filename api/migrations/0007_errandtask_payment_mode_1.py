# Generated by Django 4.1.3 on 2024-02-01 07:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_errandtask_payment_mode_subtype_description_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='errandtask',
            name='payment_mode_1',
            field=models.CharField(blank=True, choices=[('ONLINE', 'ONLINE'), ('CASH', 'CASH')], max_length=20, null=True),
        ),
    ]
