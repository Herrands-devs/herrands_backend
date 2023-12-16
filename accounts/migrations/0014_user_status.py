# Generated by Django 4.1.3 on 2023-12-05 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_delete_distancemetric_delete_vehiclemeric'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='status',
            field=models.CharField(blank=True, choices=[('Active', 'Active'), ('Suspended', 'Suspended'), ('Banned', 'Banned'), ('Pending', 'Pending')], default='Active', max_length=100, null=True),
        ),
    ]
