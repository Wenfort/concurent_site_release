# Generated by Django 3.1.5 on 2021-02-13 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0030_auto_20210211_0820'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderstatus',
            name='user_order_id',
            field=models.IntegerField(default=1),
        ),
    ]