# Generated by Django 2.2.14 on 2020-11-29 10:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20201129_0537'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coupon',
            old_name='amount',
            new_name='monto',
        ),
        migrations.RenameField(
            model_name='orderitem',
            old_name='quantity',
            new_name='cantidad',
        ),
        migrations.RenameField(
            model_name='payment',
            old_name='timestamp',
            new_name='fecha_y_hora',
        ),
        migrations.RenameField(
            model_name='payment',
            old_name='amount',
            new_name='monto',
        ),
        migrations.RenameField(
            model_name='payment',
            old_name='stripe_charge_id',
            new_name='pago_id',
        ),
    ]
