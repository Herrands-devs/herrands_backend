# Generated by Django 4.2.6 on 2023-11-01 00:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_alter_errandtask_drop_off_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='errandtask',
            name='files',
            field=models.ManyToManyField(blank=True, null=True, to='api.file'),
        ),
    ]