# Generated by Django 4.1.3 on 2024-02-01 13:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_errandtask_payment_mode_1'),
    ]

    operations = [
        migrations.RenameField(
            model_name='errandtask',
            old_name='payment_mode_1',
            new_name='payment_method',
        ),
    ]
