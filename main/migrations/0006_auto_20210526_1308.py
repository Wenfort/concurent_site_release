# Generated by Django 3.1.7 on 2021-05-26 13:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_orderdata_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='order',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='main.order'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='OrderData',
        ),
    ]
