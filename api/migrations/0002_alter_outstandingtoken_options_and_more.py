# Generated by Django 4.0.3 on 2022-03-25 13:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0019_alter_anonuser_username'),
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='outstandingtoken',
            options={'ordering': ('anon_user',)},
        ),
        migrations.RemoveField(
            model_name='outstandingtoken',
            name='user',
        ),
        migrations.AlterField(
            model_name='outstandingtoken',
            name='anon_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='base.anonuser'),
        ),
    ]
