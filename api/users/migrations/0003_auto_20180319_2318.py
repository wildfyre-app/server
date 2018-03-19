# Generated by Django 2.0.1 on 2018-03-19 22:18

from django.db import migrations, models
import users.models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20170324_1853'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=users.models.Profile.avatar_path),
        ),
    ]
