# Generated by Django 3.1.7 on 2021-04-17 11:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0059_auto_20210417_1015'),
    ]

    operations = [
        migrations.AddField(
            model_name='handledxml',
            name='bottom_ads_count',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='handledxml',
            name='top_ads_count',
            field=models.SmallIntegerField(default=0),
        ),
    ]