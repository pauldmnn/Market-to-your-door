# Generated by Django 5.1.6 on 2025-03-23 14:07

import django_countries.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0014_remove_shippingaddress_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='shippingaddress',
            name='country',
            field=django_countries.fields.CountryField(default='GB', max_length=2),
        ),
    ]
