# Generated by Django 2.2.14 on 2020-11-29 10:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20201129_0521'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='apartment_address',
            new_name='direccion',
        ),
        migrations.RenameField(
            model_name='address',
            old_name='street_address',
            new_name='direccion2',
        ),
        migrations.RenameField(
            model_name='address',
            old_name='country',
            new_name='pais',
        ),
    ]
