# Generated by Django 4.2.10 on 2024-08-18 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='start_date',
            field=models.DateTimeField(verbose_name='Дата и время начала курса'),
        ),
    ]
