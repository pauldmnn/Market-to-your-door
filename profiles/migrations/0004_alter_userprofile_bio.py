# Generated by Django 5.1.6 on 2025-03-27 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_alter_userprofile_bio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='bio',
            field=models.TextField(blank=True),
        ),
    ]
