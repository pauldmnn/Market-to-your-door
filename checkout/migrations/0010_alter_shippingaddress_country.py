# Generated by Django 5.1.6 on 2025-03-23 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0009_alter_shippingaddress_country'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shippingaddress',
            name='country',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
