# Generated by Django 3.1.7 on 2021-04-17 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0058_auto_20210407_1415'),
    ]

    operations = [
        migrations.AddField(
            model_name='handledxml',
            name='reruns_count',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='handledxml',
            name='refresh_timer',
            field=models.SmallIntegerField(default=10),
        ),
    ]
