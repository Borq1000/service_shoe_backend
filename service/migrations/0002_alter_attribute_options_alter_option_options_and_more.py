# Generated by Django 5.1.1 on 2024-10-29 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('service', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attribute',
            options={'verbose_name': 'Атрибут', 'verbose_name_plural': 'Атрибуты'},
        ),
        migrations.AlterModelOptions(
            name='option',
            options={'verbose_name': 'Опция', 'verbose_name_plural': 'Опции'},
        ),
        migrations.AlterModelOptions(
            name='service',
            options={'verbose_name': 'Услуга', 'verbose_name_plural': 'Услуги'},
        ),
    ]
