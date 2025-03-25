# Generated by Django 5.1.6 on 2025-03-25 11:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0015_shippingaddress_country'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='shippingaddress',
            name='user',
        ),
        migrations.AddField(
            model_name='shippingaddress',
            name='email',
            field=models.EmailField(blank=True, max_length=255, null=True),
        ),
    ]
