# Generated by Django 4.2.7 on 2023-11-10 19:36

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('smarthexboard', '0006_gamedatamodel_mapdatamodel_mapgenerationdata_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gamedatamodel',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('3e8aa3f4-6ac4-4798-a738-9685ab3076e3'), editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='mapdatamodel',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('cb6a21fb-f262-4b16-8b96-f5fb1f8131ac'), editable=False, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='mapgenerationdata',
            name='uuid',
            field=models.UUIDField(default=uuid.UUID('f96e8827-fd23-41df-a86c-0b3f1ff7b6e4'), editable=False, primary_key=True, serialize=False),
        ),
    ]