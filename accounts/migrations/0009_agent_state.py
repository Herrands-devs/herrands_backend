# Generated by Django 4.2.6 on 2023-10-28 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_alter_agent_pay_per_hour'),
    ]

    operations = [
        migrations.AddField(
            model_name='agent',
            name='state',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
