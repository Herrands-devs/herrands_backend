# Generated by Django 4.1.3 on 2023-12-24 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_remove_agent_photo'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='photo',
            field=models.URLField(blank=True, null=True),
        ),
    ]