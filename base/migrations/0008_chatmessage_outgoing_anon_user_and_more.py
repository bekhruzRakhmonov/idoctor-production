# Generated by Django 4.0.3 on 2022-03-20 18:23

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0007_comment_anon_user_alter_comment_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='outgoing_anon_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='outgoing_anon_user', to='base.anonymoususer'),
        ),
        migrations.AlterField(
            model_name='chatmessage',
            name='outgoing',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='outgoing', to=settings.AUTH_USER_MODEL),
        ),
    ]
