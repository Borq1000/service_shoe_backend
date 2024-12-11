# Generated by Django 5.1.1 on 2024-11-17 21:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_order_apartment_order_building_order_floor'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='latitude',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='longitude',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
