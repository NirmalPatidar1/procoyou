# Generated by Django 5.1.6 on 2025-03-26 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('procoyouApi', '0010_alter_customuser_latitude_alter_customuser_longitude'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='latitude',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='longitude',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
