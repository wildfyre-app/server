from django.db import migrations, models
import django.db.models.deletion


def update_model(model, apps):
    Area = apps.get_model('areas', 'Area')
    Model = apps.get_model('areas', model)

    for obj in Model.objects.all():
        obj.area = Area.objects.get_or_create(
            name=obj.area_string,
            defaults={'displayname': obj.area_string.title()},
        )[0]
        obj.save()


def update_posts(apps, schema_editor):
    return update_model('Post', apps)


def update_reputation(apps, schema_editor):
    return update_model('Reputation', apps)


class Migration(migrations.Migration):

    dependencies = [
        ('areas', '0007_auto_20180512_2011'),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(db_index=True, max_length=30, unique=True)),
                ('displayname', models.CharField(max_length=30, unique=True)),
            ],
        ),

        migrations.RenameField(
            model_name='post',
            old_name='area',
            new_name='area_string',
        ),
        migrations.AddField(
            model_name='post',
            name='area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='areas.Area', null=True),
        ),
        migrations.RunPython(update_posts),
        migrations.AlterField(
            model_name='post',
            name='area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='areas.Area'),
        ),
        migrations.RemoveField(
            model_name='post',
            name='area_string',
        ),

        migrations.RenameField(
            model_name='reputation',
            old_name='area',
            new_name='area_string',
        ),
        migrations.AddField(
            model_name='reputation',
            name='area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='areas.Area', null=True),
        ),
        migrations.RunPython(update_reputation),
        migrations.AlterField(
            model_name='reputation',
            name='area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='areas.Area'),
        ),
        migrations.AlterUniqueTogether(
            name='reputation',
            unique_together={('area', 'user')},
        ),
        migrations.RemoveField(
            model_name='reputation',
            name='area_string',
        ),

        migrations.DeleteModel(
            name='funPost',
        ),
        migrations.DeleteModel(
            name='informationPost',
        ),
    ]
