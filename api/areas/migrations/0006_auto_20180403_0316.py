# Generated by Django 2.0.1 on 2018-04-03 01:16

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('areas', '0005_auto_20180319_2352'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='draft',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='post',
            name='active',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AlterField(
            model_name='post',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='post',
            name='stack_outstanding',
            field=models.IntegerField(default=0),
        ),
    ]