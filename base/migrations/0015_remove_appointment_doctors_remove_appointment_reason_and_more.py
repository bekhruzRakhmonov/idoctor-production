# Generated by Django 4.0.3 on 2022-03-23 10:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0014_alter_appointment_clients_alter_appointment_doctors'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='appointment',
            name='doctors',
        ),
        migrations.RemoveField(
            model_name='appointment',
            name='reason',
        ),
        migrations.CreateModel(
            name='Clients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('client', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointment_client', to='base.anonuser')),
                ('doctor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointment_doctor', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='appointment',
            name='clients',
            field=models.ManyToManyField(related_name='appointment_clients', to='base.clients'),
        ),
    ]
