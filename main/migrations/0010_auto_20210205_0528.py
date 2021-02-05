# Generated by Django 3.1.5 on 2021-02-05 05:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20210204_1148'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderStatus',
            fields=[
                ('order_id', models.IntegerField(default=0, primary_key=True, serialize=False)),
                ('status', models.SmallIntegerField(default=0)),
            ],
        ),
        migrations.RemoveField(
            model_name='order',
            name='status',
        ),
    ]