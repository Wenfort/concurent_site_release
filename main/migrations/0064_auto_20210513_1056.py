# Generated by Django 3.1.7 on 2021-05-13 10:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0063_auto_20210421_1651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='handledxml',
            name='request_id',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.request'),
        ),
        migrations.AlterField(
            model_name='request',
            name='region',
            field=models.OneToOneField(default=255, on_delete=django.db.models.deletion.DO_NOTHING, to='main.region'),
        ),
    ]
