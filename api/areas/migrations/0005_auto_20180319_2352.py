# Generated by Django 2.0.1 on 2018-03-19 22:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('areas', '0004_post_anonym'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ['created']},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['pk']},
        ),
    ]
