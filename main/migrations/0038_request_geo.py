# Generated by Django 3.1.5 on 2021-02-17 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0037_auto_20210217_1302'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='geo',
            field=models.IntegerField(default=255),
        ),
    ]
