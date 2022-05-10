# Generated by Django 4.0.3 on 2022-05-06 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0019_alter_anonuser_username'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='profession',
            field=models.CharField(choices=[('Family physicians', 'Family physicians'), ('Internists', 'Internists'), ('Emergency physicians', 'Emergency physicians'), ('Psychiatrists', 'Psychiatrists'), ('Obstetricians and gynecologists', 'Obstetricians and gynecologists'), ('Neurologists', 'Neurologists'), ('Radiologists', 'Radiologists'), ('Anesthesiologists', 'Anesthesiologists'), ('Pediatricians', 'Pediatricians'), ('Cardiologists', 'Cardiologists')], max_length=255, null=True),
        ),
    ]
