# Generated by Django 4.0.3 on 2022-03-21 14:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_savedmessages_appointment'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AnonymousUser',
            new_name='AnonUser',
        ),
    ]
