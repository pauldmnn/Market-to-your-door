# Generated by Django 5.1.6 on 2025-03-23 12:22

import django_countries.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0008_rename_address_line_1_shippingaddress_address_line1_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shippingaddress',
            name='country',
            field=django_countries.fields.CountryField(max_length=2),
        ),
    ]
