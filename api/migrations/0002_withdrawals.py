# Generated by Django 4.1.3 on 2023-12-24 18:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Withdrawals',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bank_name', models.CharField(max_length=200)),
                ('bank_account_number', models.PositiveIntegerField()),
                ('beneficiary_name', models.CharField(max_length=200)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('wallet', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.wallet')),
            ],
        ),
    ]
