# Generated by Django 5.1.6 on 2025-03-23 13:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0013_alter_shippingaddress_country'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shippingaddress',
            name='country',
        ),
    ]
